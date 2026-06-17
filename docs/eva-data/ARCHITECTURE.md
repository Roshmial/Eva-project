# Eva hub architecture

## Коротко

В системе есть два разных класса данных.

1. Operational data
- используется приложением в runtime;
- обслуживает auth, CRUD, jobs, threads, feedback, scheduler state;
- хранится в backend DB `hermes_web_app.duckdb`, схема `app`.

2. Analytical data
- используется для анализа, выборок, агентского контекста и отчётности;
- хранится в `eva_hub.duckdb`, схема `eva`;
- собирается refresh-скриптом как набор снимков и views.

Смешивать эти роли в одной схеме нельзя.

## Source of truth

По web users / profiles / threads / messages / feedback:
- source of truth: `app.*` в `/home/hermes/workspace/hermes-web-mvp/services/backend/data/hermes_web_app.duckdb`

По Hermes history:
- source of truth: `~/.hermes/state.db`

По Hermes jobs:
- source of truth: `~/.hermes/cron/jobs.json`

По Telegram monitor:
- source of truth: файлы pipeline в `/home/hermes/workspace/TG-API`

По тендерам:
- source of truth: CSV/JSON-файлы pipeline в `/home/hermes/workspace/tenders`

По рабочим договорённостям:
- source of truth: `/home/hermes/workspace/interaction-notes.md` и `/home/hermes/workspace/decision-log.md`

## Data flow

1. Backend работает только со своей runtime-базой `app.*`.
2. Frontend получает данные только через backend API.
3. `refresh_eva_hub.py` читает source systems и собирает аналитический snapshot в `eva.*`.
4. Любые SQL-выборки для анализа, сверок и agent context идут в `eva_hub.duckdb`.

## Users / profiles / messages / feedback

Operational-слой остаётся у web backend:
- `app.users`
- `app.threads`
- `app.messages`
- `app.feedback`

В аналитическом hub это не дублирующий runtime, а snapshot плюс единые аналитические представления:
- `eva.app_users_raw`
- `eva.app_threads_raw`
- `eva.app_messages_raw`
- `eva.app_feedback_raw`
- `eva.actor_directory`
- `eva.thread_catalog`
- `eva.message_facts`
- `eva.feedback_facts`

Правило такое:
- frontend пишет только в operational backend DB;
- Hermes runtime пишет только в `~/.hermes/state.db`;
- Telegram pipeline пишет только в свои архивные файлы;
- `eva_hub.duckdb` собирает это в единый аналитический слой без подмены operational truth.

## Jobs model

Jobs существуют один раз в operational слое Hermes:
- `~/.hermes/cron/jobs.json`

В аналитическом hub jobs представлены не как второй operational master, а как snapshot и views:
- `eva.app_jobs_raw`
- `eva.app_job_acl_raw`
- `eva.app_job_recipients_raw`
- `eva.app_job_subscriptions_raw`
- `eva.app_job_runs_raw`
- `eva.app_job_catalog`
- `eva.app_job_access_matrix`
- `eva.app_job_delivery_matrix`
- `eva.app_job_run_summary`

Это даёт один и тот же каталог jobs в analytical мире без второго operational master в backend.

## Принцип по схемам

Разрешено:
- `app.*` как runtime storage
- `eva.*` как analytical storage

Запрещено:
- держать отдельный дублирующий runtime-like слой `web.*` внутри hub
- писать из frontend напрямую в analytical DB
- использовать `eva_hub.duckdb` как master для jobs, users, messages, feedback или auth

## Почему так лучше

- у каждой сущности один понятный источник истины;
- backend и frontend не спорят с аналитикой за master-хранение;
- можно спокойно строить views, проверки и отчёты без риска сломать runtime;
- refresh остаётся явным и контролируемым слоем интеграции.

## Проверки после refresh

Минимальный набор сверок:
- counts `app.users` = `eva.app_users_raw`
- counts `app.threads` = `eva.app_threads_raw`
- counts `app.messages` = `eva.app_messages_raw`
- counts `app.feedback` = `eva.app_feedback_raw`
- counts Hermes jobs json = `eva.app_jobs_raw`
- в `eva_hub.duckdb` нет схемы `web`

## Operational rule

Если меняется логика runtime-приложения:
- сначала меняется backend model `app.*` и API;
- потом при необходимости обновляется аналитическая проекция `eva.*` и unified views;
- но не наоборот.
