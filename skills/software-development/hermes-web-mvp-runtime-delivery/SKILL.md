---
name: hermes-web-mvp-runtime-delivery
description: Доведение и live-проверка Hermes Web MVP по задачам, рассылке, self-subscribe и админским сценариям без ложного "код готов" при stale runtime.
---

# Когда использовать

Используй для задач по Hermes Web MVP, когда нужно не только изменить код, но и доказать живым runtime, что фронт, backend и фактическая модель доставки работают согласованно.

Типовые случаи:
- задачи/рассылки/jobs UI;
- админские формы и массовые действия;
- recipients vs self-subscribe;
- проверки, что сообщения идут в отдельные `job`-чаты;
- ситуации, где код уже изменён, но live runtime ведёт себя как будто правок нет.

# Основная идея

Для Hermes Web MVP нельзя считать задачу завершённой только по diff, `py_compile`, `node --check` или unit/smoke tests. Обязателен runtime-pass через живой backend и browser/UI.

Отдельно различай:
1. основной механизм доставки: создатель/админ задаёт recipients;
2. дополнительный механизм: пользовательский self-subscribe, если он разрешён настройками задачи.

Не смешивай их в выводах и проверках.

# Порядок работы

1. Сначала уточни целевую продуктовую модель.
- Кто управляет получателями: админ/создатель или сам пользователь.
- Является ли self-subscribe обязательным, дополнительным или отключённым.
- Должна ли доставка идти в выбранный чат или в отдельный `job`-чат.

2. Проверь кодовые точки целиком.
Минимум:
- backend schema / migration / serialization;
- create/update payload;
- permission checks;
- frontend modal / draft / save / detail-view;
- live visibility of controls.

2.1. Для job-сценариев отдельно сверяй модель видимости и модель доставки.
Это два разных контура, и их легко спутать.

Проверь отдельно:
- кто должен видеть задачу в списке `/api/jobs`;
- кто должен иметь `job`-thread и получать delivery;
- какая роль возвращается из общего permission-слоя (`owner`, `editor`, `viewer`, `subscriber`, `recipient` или эквивалент);
- не собрана ли логика списка задач вручную в обход общего `get_job_role()`/`ensure_can_view_job()`.

Практический pitfall:
- backend может корректно создавать `job_recipients` и даже `job`-threads, но пользователь всё равно не видит задачу, если `/api/jobs` считает видимость по урезанной формуле (`owner/acl/subscriber/workspace`) и игнорирует recipients.
- для Hermes Web MVP это надо проверять отдельным smoke: создать задачу с `fixed_user` recipient и убедиться, что получатель видит её и в `/api/jobs`, и в `/api/jobs/<id>`.

3. После правок прогони быстрые локальные проверки.
Минимум:
- `python3 -m py_compile app.py`
- `python3 -m unittest test_smoke`
- `node --check services/frontend/app.js`

4. Перед live-приёмкой проверь, что поднят правильный backend runtime.
Это критический шаг.

Проверяй:
- `GET /api/service-info`
- mode (`hermes-api` vs `mock-hermes`)
- какой процесс реально слушает порт
- из какого cwd и каким launcher он поднят

Если `service-info` не совпадает с ожидаемым режимом, не трать время на UI-диагностику до исправления runtime.

5. Для backend Hermes Web MVP предпочитай project launcher, а не голый `python app.py`, `waitress-serve ...` или частичный ручной restart, если важны env и режим Hermes API.
В этой кодовой базе рабочий launcher:
- `/home/hermes/workspace/hermes-web-mvp-react-8793/run_backend_service.sh`

Причина:
- он поднимает venv;
- подтягивает runtime env через штатную обвязку проекта;
- выставляет `HERMES_WEB_MODE`, `HERMES_WEB_HERMES_API_BASE_URL`, `HERMES_WEB_HERMES_API_KEY` и связанные env;
- снижает риск случайного запуска backend в неверном режиме.

5.1. Отдельный жёсткий pitfall для live-restart на удалённом сервере.
- Не перезапускай backend через голый `kill ... && waitress-serve ...` или через выборочное `source ~/.hermes/.env`, если не доказано, что этого env достаточно.
- Типичный ложный успех: `/api/health` отвечает `ok`, но обычные chat/model вызовы уже падают с `hermes_api_key_missing`, потому что новый процесс поднялся без полного runtime env.
- После любого restart проверяй не только `health`, но и один реальный model-backed запрос. Для этого класса задач `health green` не доказывает, что контур действительно готов.
- Если после рестарта export/file-flow работает, а обычный assistant answer падает, подозревай именно env-drift launcher'а: export может собираться локально без вызова модели, а chat-runtime уже сломан.

6. При проверке self-subscribe делай два live-сценария.

Сценарий A: self-subscribe запрещён
- задача видима тестовому пользователю;
- `self_subscribe_enabled=false`;
- ожидаемый результат: нет кнопки подписки или backend даёт запрет, а не 500.

Сценарий B: self-subscribe разрешён
- включи self-subscribe;
- задай scope (`visible_users` или `workspace`);
- подпишись обычным пользователем;
- подтверди, что создаётся отдельный `job`-чат.

7. Проверяй доставку отдельно от UI-надписей.
Подтверждение должно идти по фактам runtime:
- JSON ответа backend;
- состояние job detail;
- записи thread/message в storage или отдельный живой job-чат в UI.

7.0 Для timezone в задачах фиксируй продуктовую зону времени явно и проверяй обе стороны.
Если по продуктовой модели весь контур живёт в МСК, это нужно подтверждать не только backend schedule-summary, но и frontend-рендером дат.

Минимум проверь:
- какой timezone попадает в normalized job payload при create/update;
- какой fallback используется, если у пользователя timezone пустой;
- в какой timezone frontend форматирует `next_run_at` / `last_run_at`;
- нет ли расхождения вида: агент обещает `09:00`, а карточка задачи показывает `12:00` из-за timezone браузера.

Практический паттерн для Hermes Web MVP:
- если продукт договорился об одной зоне времени (например, `Europe/Moscow`), фронт не должен молча рендерить timestamps в локальной зоне браузера;
- нужна либо принудительная продуктовая timezone в formatter'ах, либо явный и согласованный timezone contract по всему UI.

7.1 Для structured message flow сначала расширяй существующий message path, а не строй параллельный endpoint для reply-action.
Это особенно важно для `clarification_request` / `approval_request`.

Практический паттерн:
- backend возвращает `message_kind` и action-метаданные (`clarification_actions`, `approval_actions` или эквивалент);
- frontend рендерит эти действия как кнопки/варианты;
- нажатие отправляет обычное сообщение в тот же `POST /threads/<id>/messages`, что и composer;
- если artifact уже показывает prompt, не дублируй тот же текст вторым пузырём в message body.

Такой путь лучше, чем отдельный `reply-to-structured-message` route, потому что:
- не дублируется send logic;
- не расходятся optimistic updates;
- проще smoke-проверка и хранение истории сообщений.

7.2 Для acceptance structured message flow нужен не только рендер, но и follow-up сценарий.
Минимум проверь:
- первичный ответ backend действительно приходит как `clarification_request` или `approval_request`;
- в `meta` есть пригодные для UI actions, а не только статические labels;
- follow-up по action prompt возвращает следующий продуктовый шаг (`dashboard_result`, `approval_result` или эквивалент), а не просто ещё один общий текстовый ответ.

8. Если поведение похоже на "код не подхватился", сначала подозревай stale runtime, mode mismatch или другой storage.
Не делай вывод "логика сломана", пока не проверены:
- launcher;
- service mode;
- фактическая БД/схема;
- наличие новых колонок/полей в live response.

8a. Для этого контура отдельно проверяй, что `scripts/runtime_env.sh` действительно выставляет ожидаемый режим backend.
- Не полагайся на README или runbook, если live `GET /api/service-info` показывает `mock-hermes`.
- Если backend должен работать через Hermes API Server, проверь наличие `HERMES_WEB_MODE=hermes-api` в effective env процесса и только потом диагностируй chat/runtime выше по стеку.
- После правки env-обёртки обязательно перезапусти именно backend unit/service и повторно проверь `service-info` и `health`.

8b. Для временного внешнего доступа через reverse tunnel у Vite dev frontend есть отдельная ловушка: host allowlist.
- Если tunnel URL открывается с `Blocked request. This host ... is not allowed`, это не поломка backend и не сетевой отказ.
- Для Vite dev server добавь `server.allowedHosts` (в текущем контуре допустимо `allowedHosts: true` для временного внешнего доступа), затем перезапусти frontend service.
- После этого перепроверь и сам HTML по внешнему URL, и same-origin `GET /api/service-info` через тот же внешний host.

8c. Для внешних ссылок и web-auth страниц не считай `200 OK` доказательством рабочего UI.
- После `curl`/`service-info` обязательно проверь живой рендер: есть ли ожидаемые поля, кнопки и следующий шаг сценария.
- Если HTML содержит формы, а в браузере их нет, сразу проверь JS errors / console и ищи поломку инициализации фронта, а не только backend status.
- Для токенизированных auth-flow страниц минимальный acceptance — не просто заголовок страницы, а видимые интерактивные контролы (`input`, `button`) и корректный initial state (`ready`, `code_sent`, `password_required`, и т.д.).
- Если пользователь сообщает `no tunnel here :(` или аналогичную внешнюю ошибку, отдельно различай: (1) локальный frontend жив, (2) tunnel-процесс жив, (3) внешний URL реально отдаёт рабочий frontend. Даже при живом ssh-процессе внешний endpoint может уже отвечать `503`; в таком случае recycle tunnel и заново проверь внешний `200` и same-origin `/api/service-info`.

8.1 Если browser/UI smoke блокируется средой, не останавливай приёмку на уровне diff.
Для Hermes Web MVP валиден промежуточный fallback:
- прогнать backend smoke на том же structured scenario;
- подтвердить `react:build`;
- проверить живые порты и базовые HTTP endpoint'ы (`/api/service-info`, frontend `200`, runtime info route);
- отдельно зафиксировать, что browser automation ограничена native runtime-слоем, а не сразу объявлять feature неподтверждённой.

8.2 Для user-memory в Hermes Web разделяй profile memory и interaction memory.
Если пользователь жалуется, что агент «использует уже записанное, но сам не фиксирует новые договорённости», не пытайся решать это патчем `pinned_json` или ручными profile fields.

Практический паттерн для этого контура:
- ручной профиль (`pinned_json`, `assistant_profile_json`) остаётся read-mostly слоем персонализации;
- автопамять общения должна жить отдельно в user-scoped поле вроде `interaction_memory_json`;
- нужен отдельный курсор последней обработки (`memory_last_processed_message_id` или эквивалент), чтобы worker не пережёвывал весь диалог заново;
- prompt должен читать `interaction_memory` отдельно от `profile_memory`, а не смешивать оба слоя в одном списке.

8.3 Для накопления памяти в Hermes Web предпочитай периодический backend writeback, а не синхронную запись в основном chat-response path.
Это особенно уместно в local-first runtime этого проекта.

Почему это лучше:
- не тормозит обычный ответ пользователю;
- не делает chat reply хрупким из-за побочного memory-save;
- упрощает retry и дозирование;
- позволяет отдельно тестировать writeback на уровне backend worker.

Минимальный контракт проверки:
- у пользователя появились новые `user/assistant` сообщения после курсора;
- worker выбрал такого пользователя;
- в `interaction_memory_json` записался новый устойчивый факт/предпочтение;
- `memory_last_processed_message_id` продвинулся до последнего обработанного сообщения;
- personalization block начал включать `interaction_memory=` в prompt.

См. также `references/structured-message-flow-2026-06.md` и `references/user-interaction-memory-writeback-2026-06.md`.

# Частые ловушки

- Изменения есть в коде, но live backend запущен не тем способом.
- `python app.py` поднял runtime в режиме, отличном от ожидаемого проектом.
- UI уже обновился, а backend всё ещё старый по mode/storage.
- Проверка идёт под админом, хотя сценарий нужен под обычным пользователем.
- Смешение понятий "админ назначает recipients" и "пользователь сам подписывается".
- Вывод по одной только кнопке в UI без проверки реального канала доставки.
- Для jobs-экрана сохранён stale `activeJobId`, и frontend падает/обнуляет экран на `Новая задача` или при открытии деталей, потому что пытается догрузить уже недоступную задачу. Для этого класса регрессий нужен fallback: при `403/404` переехать на первую доступную задачу, а не ломать экран.
- В job-flow access может быть уже исправлен в `job detail`, но список `/api/jobs` всё ещё собран отдельной логикой и потому даёт другое поведение. Всегда сверяй list-path и detail-path вместе.
- Время в карточках задач может быть неверным не из-за scheduler, а из-за frontend formatter'ов, которые используют timezone браузера вместо продуктовой зоны.
- Если память пользователя уже читается из prompt, это ещё не значит, что она действительно накапливается. Для этого класса задач отдельно проверяй write-path: отдельное поле interaction memory, курсор обработки и факт продвижения курсора после periodic worker pass.

# Критерии завершения

Считать задачу закрытой только если одновременно выполнено всё ниже:
- код собран и базовые проверки зелёные;
- live UI показывает нужные контролы;
- backend live-response содержит новые поля/логику;
- ключевой сценарий подтверждён под нужной ролью пользователя;
- доставка подтверждена в отдельном `job`-чате, если это ожидаемая модель;
- только после этого фиксировать итог в `decision-log`.

# References

- `references/attachment-hardening-and-launcher-env-drift-178.md` — как разделять backend attachment defect и frontend auth-open defect, зачем парсить `/home/hermes/...` и `sandbox:/...` как вложения, и почему после ручного restart обязательно нужен не только `health`, но и живой model-backed probe.
- Session-specific runtime findings сохраняй в `references/` этого skill, если всплывают launcher/mode/storage pitfalls или новые правила проверки.
