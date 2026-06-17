# Eva backup

Это локальный backup-репозиторий ключевых элементов рабочей конфигурации Евы.

Что включено:
- skills из `~/.hermes/skills`
- `decision-log.md`
- `interaction-notes.md`
- выборочные рабочие документы из `workspace/eva-data`

Что намеренно исключено:
- `~/.hermes/memories/*`
- `~/.hermes/state.db*`
- `~/.hermes/logs/*`
- `~/.hermes/sessions/*`
- `~/.hermes/cron/output/*`
- кэши, скриншоты, временные дампы, токены и runtime-артефакты

Назначение:
- безопасный бэкап знаний, навыков и ключевых рабочих заметок
- дальнейшая загрузка в private GitHub repo
