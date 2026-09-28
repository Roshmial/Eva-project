# Hermes Cron routing overlay поверх Web API

Краткий session-specific reference по паттерну, который оказался нужен для Hermes Web.

Когда применять:
- расписание и запуск живут в Hermes Cron;
- администратор в Web должен назначать получателей;
- результат нужно разносить по отдельным job-чатам пользователей.

Рабочая модель:
1. Hermes Cron остаётся source of truth для `schedule`, `prompt`, базового `deliver`, статуса запусков.
2. Web backend добавляет overlay recipients для `hermes_job_id`.
3. Отдельные job-чаты создаются по `external_job_id = hermes_job_id`.
4. Готовый результат забирается из `~/.hermes/cron/output/<job_id>/*.md`.
5. Для agent-jobs текст брать из блока `## Response`.
6. Для script/no_agent jobs можно брать tail после `---`, если отдельного response-блока нет.
7. Последний уже доставленный output нужно помнить отдельно, чтобы не делать duplicate fan-out.

Минимальные backend сущности:
- `hermes_job_recipients(hermes_job_id, recipient_type, target_value, label, created_at)`
- `hermes_job_delivery_state(hermes_job_id, last_output_path, last_delivered_at, updated_at)`
- `threads.external_job_id`

Минимальные backend функции:
- fetch/replace recipients overlay
- resolve recipient users
- ensure per-user job thread by external job id
- reconcile latest cron output into messages
- sync threads when recipients change

Ключевой UX-текст:
- не писать пользователю, что cron-зачада «только показывает deliver»;
- лучше писать: «расписание и базовый deliver живут в Hermes, а маршрутизация по пользователям управляется через Web API».

Ключевая ловушка:
- не пытаться втиснуть user-facing routing целиком в raw `deliver`. `deliver` — transport слой Hermes, а не обязательно вся продуктовая адресация.
