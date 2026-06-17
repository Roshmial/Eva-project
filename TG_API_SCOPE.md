# TG API scope inside Eva backup

## Что включено

- основной Python-код и pipeline-скрипты;
- web auth / login / access helpers;
- channel-конфиги, glossary, requirements, install/service scripts;
- cron manifest и setup-файлы.

## Что исключено

- `session/`, `runtime/`, `raw_logs/`, `exports/`, `reports/`, `analytics/`;
- `private-profile.env`, auth/state-файлы и generated outputs.
