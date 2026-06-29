# Runtime reference sync and live form verification

Когда применять:
- локальный код уже содержит правильные labels/types/layout для формы;
- сборка проходит;
- но live UI продолжает показывать старые подписи или старый тип поля.

## Типовой симптом

На диске уже `Состав обзора` + `textarea`, а в живом UI всё ещё `Угол обзора` + обычный `input`.

## Частая реальная причина

Источник истины для формы идёт не прямо из кода, а из persisted runtime-справочника в БД.
Для Hermes Web это может быть dataset вроде `job_templates` в `reference_items` / `reference_catalogs`.
Если startup делает только initial seed, а не refresh/sync, старые значения живут в Postgres бесконечно и перекрывают новые изменения кода.

## Надёжный порядок проверки

1. Проверить локальный код:
- backend meta/REFERENCE data;
- frontend JSX, который выбирает `input` vs `textarea`;
- CSS/layout для нужного шаблона.

2. Проверить live backend payload, а не только код:
- залогиниться в live API;
- прочитать `/api/bootstrap`;
- достать конкретный dataset (`job_templates`) и нужный item (`research_watch`);
- проверить `label`, `type`, `rows`, `layout`, `placeholder`.

3. Если backend всё ещё отдаёт старое:
- искать persisted dataset в БД;
- не чинить это только rebuild фронта;
- исправить sync startup-данных, чтобы system datasets обновлялись не только при первом seed.

4. После backend-fix сделать live reload страницы.

5. Проверить не только текст, но и настоящий DOM:
- нужный field рендерится как `textarea`, а не `input`;
- у `textarea` ожидаемые `rows`;
- размеры и координаты поля подтверждают layout, а не только JSON payload.

## Практический тройной чек

Если форма всё ещё выглядит не так, делай три проверки подряд:
1. backend bootstrap payload;
2. frontend state после reload;
3. финальный DOM (`label`, `input/textarea`, `getBoundingClientRect`).

Только после этого можно честно говорить, что баг либо в runtime-данных, либо во frontend renderer, либо уже в CSS/layout.
