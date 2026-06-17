# DuckDB concurrency + flaky React smoke

Когда live local-first runtime показывает intermittent 500 на supposedly read-only admin route, а базовый smoke зелёный, сначала разделяй две гипотезы:

1. Реальный backend concurrency defect.
2. Drift/хрупкость acceptance automation.

## Признаки backend concurrency defect

- Падает endpoint вроде `/api/admin/chat-notice`, хотя обычный unit/smoke часто зелёный.
- В логах всплывают ошибки класса `Unique file handle conflict`, `BinderException`, `TransactionException` или похожие DuckDB catalog/write conflicts.
- Проблема проявляется именно под параллельными запросами, а одиночные GET проходят.

## Надёжный порядок проверки

1. Прогнать обычный backend smoke.
2. Отдельно воспроизвести live concurrency прямыми HTTP GET в несколько потоков.
3. Если конфликт подтверждён, чинить не UI, а DB connect / retry path.
4. Добавить regression-тест именно на параллельный route.
5. Перезапустить живой backend и повторить concurrency probe.

## Практический fix pattern

- Для local-first DuckDB допустим лёгкий retry вокруг `duckdb.connect(...)` на transient-конфликтах открытия/каталога.
- Не ограничивайся общим `sleep` в UI smoke: сначала стабилизируй backend path.
- После фикса обязательно подтверждай двумя слоями:
  - unit/regression test;
  - live parallel HTTP check на том же route.

## Если потом падает длинный React smoke

Не смешивай это автоматически с тем же backend-дефектом.

Типичный drift после React-эволюции:
- detail panel обновляется не тем текстом, который ждёт smoke;
- `getByRole(..., exact: true)` ломается на реальном mixed screen/onboarding state;
- `.job-card` реально становится `active`, но старое ожидание по heading/detail уже устарело.

## Надёжный fallback для jobs/admin

- Используй unique marker в имени новой job.
- Ищи конкретную `.job-card` по `hasText`.
- Подтверждай не только текст detail, но и structural signal: карточка получила класс `active`.
- Если monolithic smoke всё ещё хрупок, добей product verification targeted probe-ами:
  - create job;
  - list contains job;
  - select job;
  - selected card becomes active;
  - backend round-trip подтверждает созданную сущность.

## Как формулировать итог

Если backend concurrency уже исправлен и live targeted probes подтверждают рабочий contour, а длинный acceptance script всё ещё плавает на локаторах/состоянии экрана, финальный вывод должен разделять:

- product/runtime contour: принят;
- monolithic smoke automation: требует отдельной стабилизации.

Не подавай flaky smoke как доказательство, что сам UI или backend всё ещё не работает.
