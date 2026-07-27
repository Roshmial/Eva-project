# Eva backup

Это локальный backup-репозиторий ключевых элементов рабочей конфигурации Евы и комплекта для переноса на чистый сервер.

Что включено:
- skills из `~/.hermes/skills`
- `decision-log.md`
- `interaction-notes.md`
- выборочные рабочие документы из `workspace/eva-data`
- curated snapshot `workspace/TG-API`
- `~/.hermes/config.yaml`, `~/.hermes/cron/jobs.json`, `~/.hermes/scripts/*`
- transfer-kit для чистого Linux-сервера с Hermes

Что намеренно исключено:
- `~/.hermes/memories/*`
- `~/.hermes/state.db*`
- `~/.hermes/logs/*`
- `~/.hermes/sessions/*`
- `~/.hermes/cron/output/*`
- TG API `session/`, `runtime/`, `raw_logs/`, `exports/`, `reports/`, `analytics/`
- токены, auth/state-файлы, кэши, скриншоты и runtime-артефакты

Назначение:
- безопасный backup знаний, навыков и ключевой operational-конфигурации Евы
- база для восстановления на новом сервере после установки Hermes

Последнее обновление: 2026-07-27 06:00:57 UTC
