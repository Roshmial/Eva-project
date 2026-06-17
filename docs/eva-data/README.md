# Eva data hub

Главная аналитическая база: `eva_hub.duckdb`

## Назначение

`eva_hub.duckdb` — это единый локальный аналитический hub для:
- истории Hermes;
- данных web-приложения Hermes MVP;
- Telegram-парсингов;
- тендерных парсингов;
- рабочих документов `interaction-notes.md` и `decision-log.md`.

База аналитическая. Она не является runtime-базой приложения и не должна использоваться как operational source of truth.

## Архитектурное правило

Есть два явных слоя.

1. Operational layer
- runtime-база web-приложения: `/home/hermes/workspace/hermes-web-mvp/services/backend/data/hermes_web_app.duckdb`
- схема: `app`
- здесь живут auth, users, threads, messages, feedback, jobs и execution state.
- это единственный источник истины для frontend и backend.

2. Analytical layer
- аналитическая база: `/home/hermes/workspace/eva-data/eva_hub.duckdb`
- схема: `eva`
- сюда через refresh загружаются проекции из Hermes state, backend app DB, Telegram, тендеров и рабочих документов.
- frontend сюда не ходит.

Главное правило: runtime-данные не редактируются в `eva_hub.duckdb`. В hub попадают только снимки и аналитические views.

Отдельное правило по source of truth:
- `app.users`, `app.threads`, `app.messages`, `app.feedback` — operational truth web MVP;
- `~/.hermes/state.db` — operational truth истории Hermes;
- `~/.hermes/cron/jobs.json` — operational truth cron-задач Hermes;
- Telegram и тендерные pipeline остаются truth в своих исходных файлах.

## Что хранится в `eva`

### Hermes
- `eva.hermes_sessions`
- `eva.hermes_messages`
- `eva.hermes_dialogue`
- `eva.hermes_recent_user_threads`
- `eva.hermes_recent_user_questions`
- `eva.hermes_open_user_requests`
- `eva.hermes_tool_failures`
- `eva.hermes_session_status`

### Web app snapshot
Raw snapshot из `app.*`:
- `eva.app_users_raw`
- `eva.app_threads_raw`
- `eva.app_messages_raw`
- `eva.app_feedback_raw`

Единый аналитический слой по людям и сообщениям:
- `eva.actor_directory`
- `eva.thread_catalog`
- `eva.message_facts`
- `eva.feedback_facts`

Смысл этих views:
- `actor_directory` — общий справочник акторов по источникам: web users, Hermes runtime users, Telegram channels;
- `thread_catalog` — единый каталог диалогов и сессий;
- `message_facts` — единый поток сообщений из web, Hermes и Telegram с source tagging;
- `feedback_facts` — нормализованный слой feedback поверх web-сообщений.

Важно: это не попытка насильно слить operational данные в один master. Это аналитическая федерация источников с явным `source_system` и собственными ключами.

### Hermes jobs snapshot
Jobs больше не читаются из backend `app.jobs` как из operational master.

Raw snapshot Hermes cron:
- `eva.app_jobs_raw`
- `eva.app_job_acl_raw`
- `eva.app_job_recipients_raw`
- `eva.app_job_subscriptions_raw`
- `eva.app_job_runs_raw`

Готовые аналитические views по jobs:
- `eva.app_job_catalog`
- `eva.app_job_access_matrix`
- `eva.app_job_delivery_matrix`
- `eva.app_job_run_summary`
- `eva.app_jobs_open`

### Telegram
- `eva.telegram_archive_messages_raw`
- `eva.telegram_summary_messages`
- `eva.telegram_digest_rows`
- `eva.telegram_collection_runs`
- `eva.telegram_posts`
- `eva.telegram_post_type_stats`
- `eva.telegram_channel_stats`
- `eva.telegram_top_posts`
- `eva.telegram_cases`
- `eva.telegram_high_signal_posts`
- `eva.telegram_daily_feed`
- `eva.telegram_channel_leaderboard`
- `eva.telegram_client_digest_candidates`

### Тендеры
- `eva.tender_items`
- `eva.tender_source_status`
- `eva.tender_run_summaries`
- `eva.tender_sources_config`
- `eva.tender_summary`
- `eva.tenders_recent`
- `eva.tender_source_health`
- `eva.tender_source_leaderboard`
- `eva.tender_priority_queue`

### Рабочие документы и техданные
- `eva.workspace_documents`
- `eva.workspace_decision_log_entries`
- `eva.interaction_notes_current`
- `eva.decision_log_latest`
- `eva.source_files`
- `eva.import_runs`
- `eva.db_settings`

## Что было убрано

Переходная схема `web.*` из hub больше не используется.

Раньше она дублировала runtime-сущности приложения внутри аналитической базы и размывала источник истины. Теперь правило такое:
- operational truth живёт только в `app.*` backend DB;
- аналитические проекции живут только в `eva.*`.

## Refresh

Полное обновление базы:
`python /home/hermes/workspace/eva-data/refresh_eva_hub.py`

Что делает refresh:
- пересоздаёт схему `eva`;
- удаляет переходную схему `web`, если она осталась от старых прогонов;
- загружает Hermes history из `~/.hermes/state.db`;
- загружает snapshot runtime-базы web-приложения из `app.*`;
- загружает Telegram-данные;
- загружает тендерные данные;
- загружает `interaction-notes.md` и `decision-log.md`;
- пересобирает views и выполняет `ANALYZE`.

## Автообновление

Timer systemd пользователя:
- service: `eva-hub-refresh.service`
- timer: `eva-hub-refresh.timer`

Проверка статуса:
- `systemctl --user status eva-hub-refresh.service`
- `systemctl --user status eva-hub-refresh.timer`
- `systemctl --user list-timers eva-hub-refresh.timer`

## Backup-процедура

Создать backup:
`python /home/hermes/workspace/eva-data/backup_eva_hub.py`

Восстановить из backup:
`python /home/hermes/workspace/eva-data/restore_eva_hub.py eva_hub_YYYYMMDDTHHMMSSZ.duckdb`

Папка backup:
`/home/hermes/workspace/eva-data/backups/`

## Полезные стартовые запросы

Jobs: единый каталог:
`select * from eva.app_job_catalog order by job_id;`

Акторы по всем источникам:
`select * from eva.actor_directory order by source_system, actor_key;`

Единый поток сообщений:
`select * from eva.message_facts order by created_at desc limit 50;`

Feedback по сообщениям:
`select * from eva.feedback_facts order by created_at desc;`

Jobs: права доступа:
`select * from eva.app_job_access_matrix order by job_id, access_source, subject_user_id;`

Jobs: получатели:
`select * from eva.app_job_delivery_matrix order by job_id;`

Jobs: история прогонов:
`select * from eva.app_job_run_summary order by latest_started_at desc;`

Активные jobs:
`select * from eva.app_jobs_open;`

Последние пользовательские треды Hermes:
`select * from eva.hermes_recent_user_threads limit 20;`

Последние вопросы пользователя:
`select * from eva.hermes_recent_user_questions limit 20;`

Ошибки и сбои инструментов:
`select * from eva.hermes_tool_failures limit 20;`

Кандидаты в клиентский дайджест:
`select * from eva.telegram_client_digest_candidates limit 20;`

Очередь приоритетных тендеров:
`select * from eva.tender_priority_queue limit 20;`
