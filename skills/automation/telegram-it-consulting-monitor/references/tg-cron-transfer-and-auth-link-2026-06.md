# TG cron transfer and auth-link verification

Короткая сессионная справка по доведению TG production-контура в Hermes.

## Что считать базовым production-контуром

Три job'ы Hermes:
- `daily-telegram-it-consulting-collector`
- `daily-telegram-it-consulting-digest`
- `weekly-telegram-it-consulting-qa`

Типовая роль:
- collector: `no_agent=True`, локальный script-runner, пишет свежий `collect_*.json` report;
- digest: script подаёт JSON-контекст агенту, агент формирует клиентский дайджест и прикладывает CSV;
- weekly QA: `no_agent=True`, собирает текстовый weekly QA report.

## Важный pitfall по auth-link

Если задан `TG_AUTH_ADMIN_TOKEN`, endpoint `/auth/telegram/admin/create_link` требует токен.

Рабочие варианты:
- заголовок `X-Auth-Token: <token>`;
- или `Authorization: Bearer <token>`.

Следствие:
- локальный POST без токена в таком режиме не доказывает, что endpoint сломан;
- сначала проверять env-режим, потом уже делать вывод по endpoint.

## Перенос cron-контура

Не полагаться на устное копирование параметров из `~/.hermes/cron/jobs.json`.

Предпочтительный слой переноса внутри проекта:
- project-local manifest с описанием job'ов и wrapper-скриптов;
- installer, который:
  - записывает wrappers в `~/.hermes/scripts/`;
  - делает `hermes cron create/edit` idempotent-способом;
  - при необходимости после CLI-синхронизации доводит поля вроде `enabled_toolsets` до актуального состояния.

## Зафиксированные project-local файлы

В текущем контуре это:
- `hermes_tg_cron_manifest.json`
- `install_hermes_tg_cron.py`

Идея этих файлов:
- держать рабочую конфигурацию рядом с кодом TG-API;
- уметь воспроизвести cron-контур в новом Hermes-home без ручной пересборки по памяти.

## Минимальная проверка после переноса

1. Проверить `hermes cron status`.
2. Проверить наличие трёх TG job'ов в `hermes cron list`.
3. Прогнать collector вручную.
4. Прогнать `build_digest_context.py`.
5. Отдельно проверить auth-link create endpoint именно в токеновом режиме, если `TG_AUTH_ADMIN_TOKEN` включён.
