[2026-06-17] — Hermes Web user memory must be accumulated as separate interaction memory with periodic backend writeback

Context:
- В live-контуре пользовательская память использовалась только как read-only personalization из профиля (`pinned_json`, `assistant_profile_json`) и не пополнялась по итогам диалогов.
- Это давало ложное ощущение, что агент "помнит", хотя фактически он не фиксировал новые устойчивые предпочтения и договорённости из переписки.
- Пользователь отдельно зафиксировал архитектурное предпочтение: не смешивать автопамять с ручным profile memory и, по возможности, делать накопление через периодическую обработку, а не в синхронном chat-response.

Decision:
- В `services/backend/app.py` добавлен отдельный user-scoped слой автопамяти:
  - `users.interaction_memory_json` — список автонакопленных заметок о пользователе;
  - `users.memory_last_processed_message_id` — курсор последнего обработанного сообщения.
- `build_personalization_block()` теперь читает `interaction_memory` отдельно от `profile_memory`, не смешивая auto-memory с ручным `pinned`.
- Автонакопление реализовано через периодический backend writeback внутри текущего chat processor worker, без новой внешней инфраструктуры:
  - worker периодически ищет пользователей с новыми `user/assistant` сообщениями после курсора;
  - извлекает memory-кандидаты сначала эвристикой, а в `hermes-api` режиме дополнительно через LLM JSON extraction;
  - обновляет `interaction_memory_json` и продвигает `memory_last_processed_message_id`.
- Контур не блокирует обычный chat reply и не требует отдельного демона/cron поверх уже существующего backend runtime.

Verification:
- Локально: `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` — ok.
- Локально: `python3 -m unittest services/backend/test_smoke.py -k memory` — 2 tests OK.
- Локально: `python3 -m unittest services/backend/test_smoke.py -k personalization` — OK.
- На live backend `178.104.207.89`: те же memory-smoke tests прошли через проектный `.venv`.
- Live-smoke на `178.104.207.89` с временным пользователем и тестовым диалогом подтвердил запись `interaction_memory_json` значением `По умолчанию отвечай кратко и не используй английские слова без необходимости` и корректное продвижение `memory_last_processed_message_id` до последнего сообщения.
- `hermes-web-backend-8791.service` после выкладки перезапущен и остался `active`.

[2026-06-17] — Hermes Web jobs: recipient visibility, stale activeJob fallback, and Moscow-time rendering

Context:
- Пользователь зафиксировал три живые регрессии в задачах: экран мог «обнуляться» при `Новая задача`/открытии настроек, назначенный пользователь не видел задачу в своём списке, а время в UI расходилось с текстом агента на +3 часа.
- Разбор показал две отдельные причины доступа и одну frontend-причину UX/runtime: `get_job_role()` и `/api/jobs` не учитывали `job_recipients`, `loadJobs()` жёстко падал на stale/невидимом `activeJobId`, а frontend форматировал timestamps в timezone браузера вместо фиксированной МСК.

Implemented:
- В `services/backend/app.py`:
  - `get_job_role()` теперь считает `fixed_user` и `fixed_thread` получателей валидными viewers с ролью `recipient`;
  - `/api/jobs` больше не собирает роль вручную урезанной логикой, а использует единый `get_job_role()`;
  - fallback timezone для job-нормализации переведён с `UTC` на `Europe/Moscow`, если у владельца timezone пустой.
- В `services/frontend-react/src/App.jsx`:
  - введён единый `MOSCOW_TIMEZONE = 'Europe/Moscow'` для job-draft defaults и форматирования времени;
  - `formatTs`/`formatTsCompact` теперь рендерят время принудительно в МСК;
  - `loadJobs()` теперь мягко переживает `403/404` на сохранённом `activeJobId` и переключается на первую доступную задачу вместо сброса экрана.

Verified:
- `python3 -m pytest services/backend/test_smoke.py -k 'job_display_name_and_fixed_user_recipient or fixed_user_recipient_can_see_assigned_job_in_jobs_list or job_timezone_defaults_to_moscow_when_owner_timezone_missing'` → 3 passed.
- `npm run react:build` в `/home/hermes/workspace/hermes-web-mvp-react-8793` прошёл успешно.
- Полный `npm run ui:smoke` в этой сессии не выполнен: Playwright Chromium не стартует из-за системной зависимости `libnspr4.so`.

[2026-06-18] — Hermes Web prod 178 must reconcile Hermes cron delivery in background, not only on jobs UI/API access

Context:
- На prod `178.104.207.89` cron `ТГ Дайджест` (`64f6e352b557`) 18.06.2026 сгенерировал output вовремя: старт около `06:30:09 UTC`, итоговый markdown-файл `/home/hermes/.hermes/cron/output/64f6e352b557/2026-06-18_06-31-06.md` был готов в `06:31:06 UTC` (`09:31 МСК`).
- Сообщение в web-thread Виктории появилось только в `06:53:20 UTC`, то есть после позднего обновления recipients для Hermes-job около `06:53:33 UTC`.
- Разбор `services/backend/app.py` показал, что `reconcile_hermes_job_delivery()` вызывался только как побочный эффект jobs API (`/api/jobs`, `/api/jobs/<id>`, patch/update, manual run) и не имел автономного фонового цикла.

Decision:
- Доставка Hermes cron output в web-контур не должна зависеть от открытия экранов, чтения jobs API или ручного patch/update задачи.
- В существующий backend `scheduler_worker()` добавлен второй проход: каждые `SCHEDULER_POLL_SECONDS` он делает `list_cached_hermes_jobs(force_refresh=True)` и для каждой Hermes-job вызывает `reconcile_hermes_job_delivery(...)` и `sync_hermes_job_threads(...)`.
- Архитектурно это остаётся local-first решением внутри текущего backend runtime, без отдельного демона, без внешнего scheduler и без привязки к UI-активности.

Verification:
- На prod `178.104.207.89` live-код подтверждён grep-ом: в `app.py` присутствует `for hermes_job in list_cached_hermes_jobs(force_refresh=True):` внутри `scheduler_worker()`.
- `hermes-web-backend-8791.service` после выкладки перезапущен и перешёл в `active (running)`.
- `curl http://127.0.0.1:8791/api/health` после рестарта вернул `status=ok`.
- Полная поведенческая проверка следующего реального cron-tick ещё не зафиксирована; текущая верификация подтверждает внедрение live-фикса и живость runtime.
- Backlog / follow-up: текущий polling-подхват Hermes cron delivery в `scheduler_worker()` считается временным operational fix. Целевая архитектура — event-driven привязка к завершению Hermes cron job, чтобы backend делал reconcile/delivery сразу по факту готового output, без цикла опроса.

[2026-06-18] — Hermes Web chat-to-job must not create recurring monitoring from ordinary research requests without explicit user schedule intent

Context:
- На prod `178.104.207.89` у пользователя Елена (`user_id=8`, `epervyshina@kept.ru`) обычные исследовательские запросы про подбор Telegram-каналов были ошибочно преобразованы в recurring monitoring jobs.
- В переписке были фразы вроде `Подбери перечень телеграмм-каналов...` и `найди перечень каналов крупных вендоров и интеграторов для мониторинга`, но не было явного запроса на регулярность (`ежедневно`, `еженедельно`, `на регулярной основе`, `поставь задачу` и т.п.).
- Разбор `services/backend/app.py` показал, что `maybe_create_recurring_job_from_chat()` классифицировал запрос по `recent_context`, куда попадали и предыдущие ответы ассистента. Это позволяло assistant-side словам про мониторинг/настройку регулярного отслеживания ложно запускать recurring job creation.

Decision:
- Создание recurring job из чата должно опираться только на явный intent в текущем пользовательском сообщении.
- Контекст предыдущих сообщений можно использовать для темы и параметров задачи только после того, как intent на регулярность уже подтверждён самим пользователем.
- Обычные исследовательские формулировки (`подбери`, `найди`, `собери перечень`) без явного schedule-intent не должны порождать recurring jobs.

Implemented:
- В `services/backend/app.py` обновлён `maybe_create_recurring_job_from_chat()`:
  - если `looks_like_recurring_job_request(user_text)` → schedule выводится из текущего пользовательского сообщения;
  - если `looks_like_recurring_job_followup(user_text)` → допускается использование recent context как уточняющего контекста;
  - иначе recurring job не создаётся.
- На prod `178` у Елены принудительно переведены в `paused` ошибочно созданные jobs `id=5,6,7` и очищены их `next_run_at`.

Verified:
- Локально: `python3 -m pytest services/backend/test_smoke.py -q -k 'test_chat_recurring_request_creates_real_job or test_chat_research_request_does_not_create_recurring_job_without_explicit_schedule_intent'` → `2 passed`.
- Локально: `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` → ok.
- На prod `178.104.207.89`: backend `hermes-web-backend-8791.service` перезапущен и `api/health` вернул `status=ok`.
- На prod-коде проверено, что фразы Елены больше дают `request=false`, `followup=false`, а явная фраза `Можешь поставить сбор этой информации на еженедельной основе?` остаётся `request=true`.
- На prod подтверждено, что jobs Елены `id=5,6,7` теперь `paused` и `next_run_at=null`.

[2026-06-18] — Hermes Web admin chat on 178 must not misroute ordinary Telegram-related text into analytics flow or publish non-executable action promises

Context:
- В admin-чате на prod `178.104.207.89:8791` обнаружились два разных ложных generation/runtime симптома: (1) обычные текстовые запросы с упоминанием `Telegram`, `интернет`, `аналитика` воспринимались как special analytics/dashboard intent; (2) обычный chat-ответ мог публиковать фразы вроде `Что я сделаю сейчас` / `Приступаю`, хотя backend не запускал реальный action/file/dashboard path.
- Проверка live runtime показала, что Telegram API-контур физически доступен (`TELEGRAM_API_BASE_URL=http://127.0.0.1:8001`, connector `telegram_api` discoverable и `available=true`), поэтому фразы вида `не могу забрать каналы` не должны объясняться просто отсутствием API.
- Последний admin-кейс в `thread_id=81` подтвердил второй дефект: assistant написал `Приступаю к проверке инфраструктуры`, но это был обычный `downstream=hermes-api-server` ответ без реального action-run; следующий turn `Да, сделай` завершился `chat_task.last_error = timed out`.

Decision:
- Обычный текст с упоминанием Telegram/интернета/аналитики не должен сам по себе включать special dashboard/analytics route; для этого нужен явный intent на дашборд/витрину/сводку.
- Если backend не запускает реальный исполняемый path (file_response, dashboard_result, structured action/clarification path), финальный assistant reply не должен публиковать operational promises вида `Что я сделаю сейчас`, `Проверю`, `Создам`, `Запущу`, `Приступаю`.
- Для generic chat-ответов безопаснее быть описательными и честными, чем имитировать начало действия, которого runtime не выполняет.

Implemented:
- В `services/backend/app.py` сохранена жёсткая логика `is_dashboard_request()`: dashboard route включается только по явным токенам intent (`дашборд`, `dashboard`, `сводк`, `витрин`), а не по словам `Telegram` / `аналитика` в обычном тексте.
- В `services/backend/app.py` добавлен `strip_non_executable_action_promises()` и расширен `postprocess_assistant_reply(...)`:
  - для generic chat-ответов без реального action route вырезаются блоки `Что я сделаю сейчас`, numbered operational steps (`Проверю/Создам/Запущу/...`) и отдельные строки `Приступаю ...`;
  - для реальных action/file/dashboard routes (`file_response`, `dashboard_result`, `clarification_request`, `approval_request`, `generated_from_request`, `downstream=dashboard:*`) этот фильтр не применяется.
- На prod `178` обновлён `services/backend/app.py`, backend `hermes-web-backend-8791.service` перезапущен.

Verification:
- Локально: `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` → ok.
- Локально: целевые регрессии по `is_dashboard_request` и `postprocess_assistant_reply` дали `2 passed` / `OK`; в текущей среде Python-процесс после этого аварийно завершался уже на shutdown, но сами тестовые ассерты успевали пройти.
- На prod `178.104.207.89`: `curl http://127.0.0.1:8791/api/health` после рестарта вернул `status=ok`, systemd-unit остался `active (running)`.
- На prod-коде напрямую проверено:
  - `is_dashboard_request("Проверь общую текстовку письма: ... Telegram ... интернет ... аналитика ...") -> False`
  - `postprocess_assistant_reply(..., {"downstream": "hermes-api-server"})` для ответа с `Что я сделаю сейчас` / `Приступаю` возвращает просто `Да, это возможно.`

[2026-06-18] — Hermes Web admin follow-up `Да, сделай` after long generic assistant plan must use focused context, and generic `timed out` must not masquerade as file-generation failure

Context:
- В том же admin-thread `81` на prod `178.104.207.89:8791` сообщение пользователя `Да, сделай` породило `chat_task id=208` со `status=error`, `last_error=timed out`, при этом `request_policy_json` остался пустым (`explicit_source_ids=[]`, `connector_targets={}`).
- Проверка `process_chat_task()` показала, что этот turn шёл не по dashboard/file/action path, а по обычному `call_hermes_api(...)` для generic chat-turn.
- Отдельно обнаружился второй дефект: `normalize_public_error_text()` превращал любой `timed out` в текст `Не удалось сформировать файл...`, даже если файл вообще не генерировался.

Decision:
- Короткие подтверждения пользователя (`Да, сделай`, `запускай`, `давай`) после длинного содержательного assistant-плана не должны идти в полный chat-history path: для них нужен узкий focused follow-up context, чтобы продолжить ровно последний сценарий, а не перегонять весь чат через общий LLM-route.
- Generic timeout должен показываться как generic upstream-timeout. File-specific текст допустим только для реального message-export / generated-file path.

Implemented:
- В `services/backend/app.py` добавлены helper-ы:
  - `is_short_followup_confirmation()`
  - `latest_substantive_assistant_message_text()`
  - `should_use_focused_followup_context()`
  - `build_focused_followup_messages()`
- `call_hermes_api()` для standard-route теперь перед обычной compaction-подачей проверяет short follow-up и, если это короткое подтверждение после длинного assistant-ответа, отправляет в модель узкий focused follow-up context вместо полного history path.
- `normalize_public_error_text()` больше не возвращает file-specific текст на голый `timed out`; теперь это generic сообщение `Не удалось получить ответ: upstream-источник превысил лимит ожидания. Повторите запрос.`
- Обновлён live backend на prod `178`, `hermes-web-backend-8791.service` перезапущен.

Verification:
- Локально: `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` → ok.
- Локально: целевые регрессии по short follow-up routing, timeout-normalization, dashboard-intent и promise-stripping дали `5 passed`; в этой среде после печати результата сохраняется известный crash Python на shutdown, но сами ассерты завершаются успешно до него.
- На prod `178.104.207.89`: `curl http://127.0.0.1:8791/api/health` после рестарта вернул `status=ok`.
- На prod напрямую проверено:
  - `is_short_followup_confirmation("Да, сделай") -> true`
  - `should_use_focused_followup_context(...) -> true` для сценария с длинным assistant-планом
  - `normalize_public_error_text("timed out") -> Не удалось получить ответ: upstream-источник превысил лимит ожидания. Повторите запрос.`
- Для исторического `chat_task id=208` подтверждено, что на момент сбоя `request_policy_json` был пустым, а `last_error` содержал именно `timed out`, то есть корень был generic follow-up path, а не реальный file/export route.

[2026-06-17] — Hermes Web generation failures for admin on 178:8791 were false postguard blocks, not timeouts; generic-failure detection must only trip on 4+ identical non-benign lines in a row, not on repeated section headings across the whole answer
[2026-06-17] — Hermes Web policy screen on 95:8803 must render from dataPolicyDraft, not admin.dataPolicy

Context:
- После backend-фикса на 178:8791 policy всё равно "стабильно не работал" в UI.
- Симптомы: toggles/выбор типа коннектора/default policy не реагировали, а вход в экран стал дольше.

Decision:
- Корневая причина на frontend: `AdminScreen` прокидывал в `AdminDataPolicySection` не draft-state, а `admin.dataPolicy`, и ещё использовал старое имя callback `onPolicyDraftChange` вместо `onDataPolicyDraftChange`.
- Экран policy должен рендериться из `dataPolicyDraft`, а изменения идти через `handleDataPolicyDraftChange`.
- Повторный вход в `data_policy`/`operations` не должен всегда форсить `loadAdmin(true, ...)`; допустим lazy reload только когда данных ещё нет.

Verification:
- Собран live frontend bundle `index-BQnksONk.js` на 95:8803 после исправления wiring.

[2026-06-17] — Hermes Web policy backend on 178:8791 must preserve explicit empty connector groups

Context:
- В live-контуре 95:8803 frontend проксирует policy API на 178.104.207.89:8791.
- Симптомы: изменение типа коннектора не сохранялось, включение/отключение источников и выбор policy/default источника визуально откатывались.

Decision:
- Причина была в backend normalizer `normalize_dashboard_policy()` на 178:8791: если frontend отправлял пустой список для `internal_connector` или `external_connector`, backend насильно восстанавливал default-group.
- Нормализацию нужно трактовать так: если группа явно передана в payload, даже пустой список считается валидным состоянием и не заменяется defaults.

Verification:
- После фикса backend round-trip возвращает `internal_connector: []` и сохраняет `source_mode`, `allowed_sources`, `default_global_source`, `connector_group_overrides` без насильственного отката.
- Live backend service `hermes-web-backend-8791.service` перезапущен.

# Decision Log

[2026-06-17] — Hermes Web prod 95→178: обычные запросы с упоминанием Telegram/аналитики больше не должны уходить в dashboard/telegram analytics route

Context:
- В prod-контуре `95.182.85.233:8803 -> 178.104.207.89:8791` обычный текстовый запрос вида «Проверь общую текстовку письма: в тексте есть Telegram, интернет и глубокая аналитика, но задача — просто отредактировать письмо» ошибочно уходил в специальные analytics/dashboard маршруты.
- Сначала prod падал с `telegram_analytics_source_missing`, потому что на live backend оставался legacy builder `telegram_digest`.
- После удаления legacy builder запрос всё ещё ошибочно классифицировался как dashboard из-за слишком широкого token-match `"аналит"` в `is_dashboard_request()` на live backend.

Decision:
- На live backend `178.104.207.89` из `dashboard_builder_definitions()` убран legacy `telegram_digest` builder.
- На live backend `178.104.207.89` в `is_dashboard_request()` убран широкий token `"аналит"`.
- В `is_dashboard_request()` добавлены negative phrases (`без дашборда`, `не нужен дашборд`, `не делай дашборд` и т.п.), чтобы отрицательные формулировки не включали dashboard route.

Verification:
- `hermes-web-backend-8791.service` на `178.104.207.89` перезапущен и остался `active`.
- Live-проверка через `http://95.182.85.233:8803/api` под `admin@demo.local` после фикса дала обычный ответ `downstream=hermes-api-server`, `processing_status=completed`.
- Тот же запрос больше не вернулся как `dashboard_result` и больше не упал с `telegram_analytics_source_missing`.


[2026-06-17] — Hermes Web policy toggles/defaults fix on 95:8803

Context:
- После предыдущего policy-cleanup пользователь подтвердил оставшуюся живую регрессию: toggles включения/отключения в `Policy` не работали, визуально всё выглядело включённым, а выбор политики и default external source не давали надёжного round-trip.
- Повторная проверка frontend/backend-контракта показала, что проблема уже не в backend route, а в смешанной frontend-логике нормализации и сохранения policy-state.

Agreed:
- Policy-экран не должен самовольно включать все источники, если backend не дал явный флаг `enabled`.
- Child-коннекторы должны жить в одном контракте групп `internal_connector/external_connector` без подстановки посторонних `source_key`.
- При сохранении frontend должен отправлять не только `connector_targets`, но и `connector_group_overrides`, потому что backend использует этот канал для устойчивого восстановления группировки коннекторов.

Implemented:
- В `services/frontend-react/src/App.jsx`:
  - `normalizeDataPolicyShape()` перестал подставлять `enabled=true` по умолчанию для любого источника; теперь при отсутствии backend-поля используется только membership в `allowed_sources`;
  - `AdminDataPolicySection` переведён на единый контракт для child-коннекторов: checkbox и select читают одно и то же assigned-group состояние, а label больше не показывает ложную группу по fallback;
  - selector `Основной внешний источник` теперь опирается только на реально включённые внешние источники и не держится за невалидное значение;
  - `handleSaveDataPolicy()` теперь дополнительно отправляет `connector_group_overrides`, собранный из текущего `connector_targets`.

Verified:
- `npm run react:build` в `/home/hermes/workspace/hermes-web-mvp-react-8793` прошёл успешно после исправления.
- В исходнике подтверждены новые маркеры: отказ от автоподстановки `enabled=true`, явный `defaultGlobalSource`, и отправка `connector_group_overrides` в PATCH payload.

Open questions:
- Осталась желательной короткая живая ручная проверка в авторизованной сессии на `95:8803`: отдельно toggles источников, default policy mode и default external source после сохранения.

[2026-06-17] — Hermes Web tasks/admin/policy/deep-analysis cleanup on 95:8803 without breaking mobile

Context:
- Пользователь добил второй пакет UI-регрессий после mobile/iPad pass: `Задачи` визуально выбивались по шрифтам и заголовкам, `Операции` в `Управление` жили в отдельном табличном стиле, `Источники`/`Policy` перестали реально менять state, а в `Параметрах` пропали остатки лимитов `Глубокого анализа`.
- Проверка frontend-кода показала конкретную причину поломки `Policy`: `cloneDataPolicyForDraft()` перестал переносить `default_global_source`, `connector_targets` и `notes`, поэтому draft открывался не из реального backend-state, а из урезанного дефолта.
- Live runtime `95:8803` сервится из текущего дерева `/home/hermes/workspace/hermes-web-mvp-react-8793/scripts/serve_frontend_prod.mjs`, поэтому достаточно было собрать свежий `dist` и проверить, что именно он уже отдаётся наружу.

Agreed:
- Раздел должен называться просто `Задачи`; отдельное `Hermes` в заголовке не нужно.
- `Детали задачи`, `Операции`, `Источники` и `Policy` должны использовать тот же визуальный язык, что и остальные panel-card экраны: нормальные отступы, те же заголовки, без отдельной «табличной» стилистики.
- В `Операциях` тип события (`Ответ ассистента / assistant`) должен быть стабильно выровнен, а не плавать внутри строки.
- В `Источники`/`Policy` нужно вернуть настоящую функциональность: изменение `default_global_source`, назначение child-интеграций в connector-группы и сохранение этих значений назад в backend-контракт `connector_targets`.
- В `Параметрах` нужно снова показывать остатки лимитов `Глубокого анализа`, не ломая desktop/mobile composer.
- Параллельно можно расширить словарь inline markdown-символов, если это делается локально в текущем renderer без нового тяжёлого контура.

Implemented:
- В `services/frontend-react/src/App.jsx`:
  - `Задачи Hermes` переименовано в `Задачи`;
  - `Детали задачи` переведены на `head-actions` + служебный подзаголовок, чтобы секция визуально совпадала с другими экранами;
  - `AdminOperationsSection` перестроен на более единый layout с классами `admin-event-main`, `admin-event-type`, `admin-event-time`;
  - `cloneDataPolicyForDraft()` снова копирует `child_connectors`, `default_global_source`, `connector_targets`, `notes`;
  - `handleDataPolicyDraftChange(...)` получил ветку `connector_assignment`, которая собирает backend-совместимый `connector_targets` как `group -> [child_keys]`;
  - `AdminDataPolicySection` снова показывает назначение child-коннекторов по группам и summary этих назначений;
  - в `Параметры -> Модель` возвращён текст с остатками лимитов `Глубокого анализа` из `bootstrap.llm_routing`;
  - markdown normalizer дополнительно расширен символами `\infty`, `\sim`, `\propto`, `\in`, `\notin`, `\subseteq`, `\supseteq`, `\subset`, `\supset`, `\cup`, `\cap`, `\forall`, `\exists`.
- В `services/frontend-react/src/styles.css`:
  - unified active-state распространён и на `sidebar-logout-btn`;
  - добавлены выравнивание и spacing для `admin-event-row`, `admin-source-card`, `connector-choice-card`, `admin-policy-group-value`;
  - добавлен промежуточный iPad-слой `@media (min-width: 821px) and (max-width: 1194px)` плюс более аккуратная сетка при `<=1220px`, чтобы не ломать phone-layout и не оставлять iPad в полудесктопном overflow.

Verified:
- `npm run react:build` в `/home/hermes/workspace/hermes-web-mvp-react-8793` прошёл успешно.
- Live `http://95.182.85.233:8803/` уже отдаёт свежие asset-файлы из собранного `dist`: `index-BrA6gGQy.js` и `index-CPKVmEgx.css`.
- В live bundle подтверждены маркеры новых правок: plain `Задачи`, строка `Лимиты глубокого анализа`, `connector_assignment`, `admin-event-type`, `admin-event-time`, `connector-choice-card`, `admin-event-row`.
- Полноценный Playwright smoke именно в этой сессии не был выполнен: локальный headless Chromium не стартует из-за системной зависимости `libnspr4.so`, а browser-session tool вернул пустой DOM после перехода на live URL. Поэтому live-подтверждение здесь — через успешную сборку и runtime bundle inspection, а не через полный авторизованный click-through.

Open questions:
- Нужна короткая живая приёмка внутри авторизованной сессии на `95:8803`, чтобы глазами подтвердить новые `Источники/Policy` и поведение `Параметров` на iPhone/iPad после выкладки.

[2026-06-16] — Hermes Web mobile/iPad toolbar + params-popover + markdown symbols on 95:8803
- 2026-06-16 — Hermes Web React chat archive semantics + iPhone input zoom + markdown headings: архивный чат должен исчезать с основной страницы и оставаться доступным через `Все чаты`; sidebar теперь показывает только `!archived`, а архивирование активного чата уводит пользователя обратно в активный поток. Для iPhone добавлены CSS anti-zoom guard (`16px`, `-webkit-text-size-adjust`, `translateZ(0)`, `-webkit-appearance: none`) и runtime viewport-focus hook. Markdown headings расширены до `#`...`######`, включая `####` и более глубокие уровни со своими стилями.
- 2026-06-16 — Hermes Web React threads archive semantics: в `Все чаты` убран ложный UX `Скрыть` через неподдерживаемое поле `ui_hidden`; единый контракт теперь только через `archived`, а кнопка в списке чатов переключает `В архив` / `Из архива` тем же PATCH `/api/threads/:id`, что и шапка активного чата.

Context:
- После первого mobile pass пользователь уточнил три дефекта: (1) при открытии `Параметры` скрываются нижние кнопки, а поведение должно быть как у `Файлы`; (2) в одной строке nav/toolbar кнопки визуально разъезжаются по стилям (`Чаты/Профиль/Задачи`, `Управление`, `Выйти`); (3) markdown-символы покрыты слишком узко, минимум нужен `\approx`; дополнительно нужна адаптация не только под iPhone, но и под iPad Pro 11".

Agreed:
- На mobile `Параметры` не должны вести себя как fixed-sheet, если из-за этого исчезают кнопки нижнего ряда; для этого экрана правильный паттерн — anchored popover над своей кнопкой, как у `Файлы`.
- Все кнопки в верхнем mobile/tablet toolbar должны быть в одном визуальном стиле; активный экран подсвечивается текущим `active`-состоянием, а не разнобоем базовых стилей.
- Markdown normalizer должен поддерживать не только стрелки, но и дополнительные часто используемые LaTeX-последовательности.
- Нужен отдельный промежуточный breakpoint для iPad/11" планшетного сценария, а не только phone cleanup на `<=820px`.

Implemented:
- В `App.jsx` popover-anchor для `Параметры` отделён классом `params-anchor`; мобильное поведение `Параметры` возвращено к anchored popover над кнопкой, а не fixed bottom-sheet.
- В `styles.css` для mobile:
  - `composer-params-popover` переведён обратно в absolute anchored overlay, bounded по ширине/высоте как `Файлы`;
  - сохранён `font-size: 16px` для `select`/label внутри `Параметры`, чтобы не вернуть iPhone auto-zoom;
  - `sidebar-logout-btn` выровнен по базовому стилю с `nav-btn`.
- Добавлен отдельный breakpoint `@media (max-width: 1180px)` для iPad Pro 11"/планшетного слоя: более плотный app-shell, toolbar-кнопки одного размера, ужатый sidebar/thread-list и корректный popover width.
- Расширена `normalizeMarkdownText(...)` в `App.jsx`: добавлены `\approx -> ≈`, `\neq -> ≠`, `\geq -> ≥`, `\leq -> ≤`, `\pm -> ±`, `\checkmark -> ✓` плюс уже существующие стрелки/`\times`.

Verified:
- `npm run react:build` прошёл успешно.
- `hermes-web-frontend-8803.service` перезапущен и остался `active`.
- `http://95.182.85.233:8803/` отдаёт новый bundle `index-5q1qhWBL.js` / `index-BGh3R-Li.css`.

[2026-06-17] — Hermes Web desktop/iPad polish on 95:8803: files cleanup, unified controls, visible admin chart

Context:
- После нескольких functional/mobile фиксов пользователь попросил добить desktop-полировку: убрать технический шум из блока `Файлы`, привести вкладки к более единому визуальному языку и отдельно проверить, почему график во вкладке `Управление` выглядит как будто не рендерится.
- Проверка кода показала, что график в `Управление` уже присутствовал в JSX, но для `admin-mini-chart*` отсутствовали CSS-правила, поэтому визуально он распадался на обычные `div` без читаемой геометрии.

Agreed:
- В пользовательском UI не нужно показывать MIME-тип вида `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, если он не помогает принятию решения.
- В блоке `Файлы` нужно убирать дублирующие подписи и объяснения, если смысл и так понятен из структуры экрана.
- Вкладки и служебные кнопки (`Чаты`, `Профиль`, `Задачи`, `Управление`, `Выйти`) должны жить в одном визуальном семействе, а активное состояние должно читаться единообразно.
- Для iPad Pro 11" нужен отдельный desktop/tablet-polish breakpoint выше phone-слоя, чтобы двухколоночные экраны и admin-блоки не выглядели зажатыми.
- График в `Управление` должен быть не просто в DOM, а иметь явные размеры, столбцы и легенду через CSS.

Implemented:
- В `services/frontend-react/src/App.jsx` в composer-блоке `Файлы` убраны дублирующие подписи `Файлы из профиля` / `Можно использовать любой ранее загруженный файл из профиля`; summary упрощён до `Выбрать из профиля`.
- В списках файлов убран вывод MIME-типа из пользовательских строк карточек; оставлены только полезные поля вроде имени, размера, даты и статуса обработки.
- В `services/frontend-react/src/styles.css` унифицирована базовая стилистика `ghost-btn`, `nav-btn` и `sidebar-logout-btn`; активное состояние кнопок сведено к одному паттерну подсветки.
- Для admin overview добавлены стили `admin-chart-card`, `admin-mini-chart`, `admin-mini-chart-col`, `admin-mini-chart-bars`, `admin-mini-chart-bar`, `admin-chart-legend`, `legend-dot`, чтобы график рендерился как читаемый bar-chart, а не как набор незаметных блоков.
- Добавлен промежуточный breakpoint `@media (max-width: 1220px)` для desktop/iPad-polish и отдельная адаптация chart-grid на `@media (max-width: 1024px)`.

Verified:
- `npm run react:build` в `/home/hermes/workspace/hermes-web-mvp-react-8793` прошёл успешно.
- `hermes-web-frontend-8803.service` перезапущен и остался `active`.
- `http://95.182.85.233:8803/` отдаёт новый bundle `index-B6W799wq.js` / `index-Dbo_GHaA.css`.
- Browser snapshot без авторизации вернул пустую страницу, поэтому live-проверка именно авторизованного admin-экрана в этой итерации не подтверждена браузерным smoke; подтверждены сборка, bundle-delivery и наличие новых chart/css-правил в runtime-артефактах.

Open questions:
- Нужна короткая user-level приёмка уже внутри авторизованной сессии: как выглядит `Управление` после новых chart-стилей и остались ли ещё места без единого visual weight.

[2026-06-16] — Hermes Web mobile chat/sidebar on 95:8803: title/actions must not overlap; mobile `Параметры` should behave as a sheet, not a shrinking desktop popover

Context:
- Пользователь прислал мобильный скрин и отдельно подтвердил дефекты: кнопки наезжают на название чата, `Параметры` открываются неполно и визуально «схлопывают» страницу, текст в чате слишком крупный/воздушный, `Выйти` занимает лишнее место и должен стоять рядом с admin-навигацией.
- Live code review показал, что mobile layout всё ещё держал title/actions слишком близко, `Параметры` использовали desktop-style popover с `select`, а на mobile `nav-btn-admin` вообще скрывался CSS-правилом.

Agreed:
- На mobile title и action-кнопки должны жить отдельными строками без перекрытия текста.
- `Параметры` на mobile должны открываться как фиксированный sheet внутри viewport, а не как узкий desktop popover.
- Текст и отступы внутри chat lane должны быть компактнее.
- `Всего чатов` можно убрать, а `Выйти` должен визуально жить рядом с navigation/admin-toolbar.

Implemented:
- В `services/frontend-react/src/App.jsx` chat header перестроен: title и action-row разделены; счетчик `Всего чатов` убран; logout встроен в общий `sidebar-nav-toolbar` рядом с nav-кнопками.
- В `services/frontend-react/src/styles.css` добавлены mobile-правки:
  - `chat-title-row` -> block + safe wrapping;
  - `chat-header-actions` отдельной строкой;
  - компактнее `messages-panel`, `message-bubble`, `message-content`, markdown gaps/headings;
  - `composer-params-popover` на mobile переведён в fixed sheet с bounded height;
  - `select`/`textarea` в mobile composer/params подняты до `16px`, чтобы убрать iPhone auto-zoom;
  - mobile nav-toolbar теперь показывает admin-кнопку и logout в одном верхнем ряду.
- В `services/frontend-react/index.html` viewport расширен до `viewport-fit=cover`.

Verified:
- `npm run react:build` прошёл успешно после правок.
- `hermes-web-frontend-8803.service` перезапущен штатно и остался `active`.
- `http://95.182.85.233:8803/` отдаёт новый bundle с обновлённым viewport/meta и свежими asset-файлами.

Rejected:
- Оставлять `Админ` скрытым на mobile.
- Лечить проблему `Параметры` только косметикой размеров без ухода от desktop-popover поведения.

[2026-06-16] — Hermes Web prod session expiry on 178: причина ложного `Сессия истекла` — `require_auth()` не продлевал `last_seen_at` по умолчанию

Context:
- Пользователя выбросило из admin-контура с сообщением `Сессия истекла`, хотя целевая логика уже была переведена на TTL от `last_seen_at`, а не от момента логина.
- Проверка live Postgres `sessions` на `178` показала, что у свежих admin-сессий `last_seen_at` оставался равен времени логина и не двигался при обычной работе в UI.
- В коде backend `require_auth(*, touch: bool | None = None)` по умолчанию выставлял `touch_session = False if touch is None else touch`, то есть почти все обычные auth-запросы проверяли срок жизни, но не продлевали его.

Agreed:
- Для этого контура обычный авторизованный пользовательский запрос должен продлевать сессию по `last_seen_at`.
- Ограничение на частоту записи остаётся через `SESSION_TOUCH_INTERVAL_SECONDS`, чтобы не писать в БД на каждый single request.
- Отдельные маршруты могут явно оставаться `touch=False`, но дефолт для `require_auth()` должен быть touch-enabled.

Implemented:
- В `services/backend/app.py` дефолт `require_auth()` изменён с `touch_session = False if touch is None else touch` на `touch_session = True if touch is None else touch`.
- В `services/backend/test_smoke.py` добавлен регрессионный тест, что обычный авторизованный запрос (`GET /api/me`) обновляет `last_seen_at`, если с прошлого touch прошло больше интервала.
- Обновлённый backend выкачен на `178` и перезапущен через `hermes-web-backend-8791.service`.

Verified:
- Live `.env` на `178`: `HERMES_WEB_SESSION_TTL_HOURS=1`.
- До фикса recent admin sessions в Postgres имели `last_seen_at == created_at`, и отсюда окно жизни фактически шло от логина.
- После фикса и restart на `178` live-проверка через реальный login + принудительно состаренный `last_seen_at` показала: `GET /api/me` -> `200`, `last_seen_at` изменился.
- `95:8803` и `178:8791` после restart остаются живыми по `service-info`.

Rejected:
- Считать это чисто frontend-проблемой logout/message handling.
- Лечить симптом увеличением TTL без исправления продления `last_seen_at`.

[2026-06-16] — Hermes Web mobile chat on 95:8803: chat-title actions должны жить в одной строке с названием, composer popovers не должны перекрывать кнопки `Файлы`/`Параметры`, warning banner нужен компактный

Context:
- На iPhone в чате заголовочные кнопки `Переименовать` и `В архив` визуально уезжали отдельным блоком под названием чата.
- Мобильные popover-окна `Файлы` и `Параметры` открывались фиксированным слоем поверх нижней панели и фактически перекрывали сами кнопки, из-за чего повторное открытие/закрытие было неудобным.
- Warning про внешнюю LLM занимал слишком много вертикального места для мобильного чата.

Agreed:
- Для mobile-first chat-surface это не отдельный redesign, а точечная адаптация существующего React frontend без изменения backend-контура.
- Заголовочные действия чата должны быть привязаны к строке названия, а не жить отдельной полосой под заголовком.
- Popover-инструменты composer на мобильном должны открываться над своими кнопками в пределах composer-контейнера, а не fixed-overlay на весь низ экрана.
- Warning должен оставаться заметным, но компактным по шрифту и вертикальному ритму.

Implemented:
- В `services/frontend-react/src/App.jsx` кнопки `Переименовать` и `В архив` перенесены внутрь `chat-title-row` рядом с названием чата.
- В `services/frontend-react/src/styles.css` добавлены `chat-header-copy`, `chat-title-row`, обновлена мобильная раскладка `chat-header-actions`.
- Для `composer-popover` и mobile breakpoint убран fixed bottom-sheet паттерн; popover теперь открывается абсолютным блоком над соответствующей кнопкой и не перекрывает `Файлы`/`Параметры`.
- Для warning-баннеров `chat-guide-banner.compact` и `chat-inline-warning` уменьшены `padding`, `font-size`, `line-height`.

Verified:
- `npm run react:build` в `/home/hermes/workspace/hermes-web-mvp-react-8793` -> OK.
- `hermes-web-frontend-8803.service` перезапущен; prod frontend снова слушает `http://0.0.0.0:8803` и проксирует на `http://178.104.207.89:8791`.
- `curl -I http://95.182.85.233:8803/` -> `200 OK`.
- В собранном prod CSS подтверждено наличие новых селекторов/правил: `.chat-title-row`, обновлённый `.chat-header-actions`, mobile `.composer-popover` и компактный `.chat-guide-banner.compact`.
- Live UI после логина рендерится без JS-ошибок; chat screen открывается.

Rejected:
- Делать для этой правки отдельный новый mobile overlay/модальное окно поверх composer.
- Оставлять fixed mobile popover, который съедает доступ к кнопкам повторного открытия/закрытия.

[2026-06-16] — Hermes Web prod contour 95→178: backend должен быть внешне доступен, frontend 8803 проверяется через local user-systemd, длинные чаты и документы закрываются на backend

Context:
- Продовый frontend `95.182.85.233:8803` проксирует API на backend `178.104.207.89:8791`.
- После ручного рестарта backend поднялся на `127.0.0.1:8791`, из-за чего frontend снова начал отдавать `frontend_proxy_upstream_unavailable`.
- В админке после первого исправления обнаружился следующий runtime-дефект: `handleAdminOpenThread is not defined`.
- Пользователь отдельно уточнил, что для длинных чатов нужен не просто storage history, а механизм, который позволяет LLM продолжать диалог после контекстного сброса.
- По документам нужно было закрыть не только `docx`, но и объёмы, таблицы, `pptx` и runtime-зависимости.

Agreed:
- Для этого контура backend на `178` должен слушать `0.0.0.0:8791`, а не loopback, потому что frontend `95` ходит по внешнему адресу.
- Frontend `8803` в этом контуре — локальный `systemctl --user` сервис `hermes-web-frontend-8803.service`; его нужно перезапускать локально после нового prod build.
- Документный ingestion закрывается на backend: повышенные лимиты, полный `docx`, `xlsx`, `pptx`, плюс установленные runtime-зависимости.
- Для длинных чатов нужен backend compaction: summary старой истории + свежий хвост, а не только хранение сырого лога сообщений.
- Для internet research источники обязательны на уровне system prompt, а проблемные LLM-ответы должны блокироваться post-guard'ом до выдачи пользователю.

Implemented:
- На `178` обновлены `services/backend/app.py`, `requirements.txt`, `test_smoke.py`.
- В `requirements.txt` добавлен `python-pptx`; backend venv на `178` обновлён с `openpyxl` и `python-pptx`.
- В backend внедрены:
  - `SESSION_TTL_HOURS=1` по умолчанию и логика от `last_seen_at`;
  - расширенное извлечение `docx` (paragraphs/tables/header/footer), `xlsx`, `pptx` (slide text/table/notes);
  - `TEXT_EXTRACT_CHAR_LIMIT=40000`, `INLINE_ATTACHMENT_PREVIEW_CHARS=4000`, upload limit `15 MB`;
  - mandatory source rule для internet research в system prompt;
  - post-guard publishability check для проблемных LLM-ответов;
  - compaction истории чата для длинных standard-диалогов.
- На `178` исправлен runtime env: в `~/.hermes/.env` зафиксирован `HERMES_WEB_BACKEND_HOST=0.0.0.0`, backend перезапущен и снова стал доступен извне.
- Во frontend `services/frontend-react/src/App.jsx` добавлен `handleAdminOpenThread`; после `npm run react:build` локальный `hermes-web-frontend-8803.service` перезапущен и поднял новый bundle на `95:8803`.
- Временный acceptance-admin использовался только для живой проверки и затем был удалён из prod DB.

Verified:
- `http://178.104.207.89:8791/api/service-info` -> `200` после фикса bind host.
- `http://95.182.85.233:8803/api/service-info` -> `200` после восстановления связки frontend->backend.
- На `178` целевой backend smoke: `Ran 7 tests ... OK`.
- Live UI: логин под временным admin, открытие вкладки `Управление`, переключение на `Операции` — экран рендерится, прежний `handleSaveChatNotice` и новый `handleAdminOpenThread` runtime-blocker сняты.
- Live document runtime smoke через реальный API на `178`:
  - sample `docx` вернул `text_extracted=true`, preview с body + table + header;
  - sample `pptx` вернул `text_extracted=true`, preview со slide text + table + notes.

Rejected:
- Считать `frontend_proxy_upstream_unavailable` чисто frontend-багом без проверки bind host backend после ручных restart'ов.
- Ограничиваться хранением истории в `messages` без compaction-механизма для длинных диалогов.
- Считать поддержку `pptx/xlsx` закрытой только кодом без установки runtime-зависимостей и живой загрузки sample-файлов.

[2026-06-15] — Hermes Web local runtime: login 503 после авторизации оказался не багом boot-flow, а точечной порчей `users.id=2` в DuckDB

Context:
- После логина `admin@demo.local` frontend стабильно оставался на login screen с ошибкой `auth_backend_temporarily_unavailable`.
- Симптом выглядел как дефект boot/auth-path: `POST /api/auth/login` проходил, а затем `/api/me`, `/api/bootstrap`, `/api/files`, `/api/threads`, `/api/jobs/meta` возвращали `503`.
- Проверка прямыми запросами и локальным DuckDB-чтением показала, что проблема не в Promise.all фронта и не в browser/CDP, а в данных: чтение `users where id=2` или `sessions join users on user_id=2` падало с `IO Error: Corrupt database file: computed checksum ...`.

Agreed:
- Для такого класса симптомов сначала отделять startup/UI-гипотезу от data corruption в локальной БД.
- Если login проходит, а почти все auth-protected read-endpoints дают одинаковый `503 auth_backend_temporarily_unavailable`, нужно сразу проверять прямое чтение user/session rows в DuckDB, а не лечить frontend boot-path вслепую.
- В локальном контуре допустим точечный data-repair с обязательным backup исходного `.duckdb` перед заменой.

Implemented:
- Остановлены временные local runtime-процессы `8791/8793`.
- Сделан backup исходной БД: `services/backend/data/hermes_web_app.pre_user2_repair_20260615.duckdb`.
- Поднят свежий schema-compatible repair DB `/tmp/hermes_web_repaired.duckdb`.
- Во временную repaired DB перелито содержимое всех таблиц из исходной БД.
- Запись `users.id=2` пересобрана отдельно валидными значениями вместо чтения повреждённого блока; repaired DB затем подменена на боевой локальный `services/backend/data/hermes_web_app.duckdb`.

Verified:
- До ремонта воспроизведено: `POST /api/auth/login` -> `200`, затем `/api/me`, `/api/bootstrap`, `/api/files`, `/api/threads`, `/api/jobs/meta` -> `503 auth_backend_temporarily_unavailable`.
- До ремонта прямой DuckDB probe на `select * from users where id=2` и на `sessions join users ... user_id=2` воспроизводил `Corrupt database file: computed checksum ...`.
- После ремонта прямой DuckDB probe на repaired DB успешно читает `users.id=2` и `sessions join users`.
- После замены БД локальный runtime снова проходит auth boot:
  - `POST /api/auth/login` -> `200`
  - `/api/me` -> `200`
  - `/api/bootstrap` -> `200`
  - `/api/files?limit=200` -> `200`
  - `/api/threads?include_archived=1` -> `200`
  - `/api/jobs/meta` -> `200`
- Live headless login acceptance подтверждён: app shell открывается, login screen исчезает, вкладка `Задачи` открывается после авторизации.

Rejected:
- Сразу чинить frontend boot/path без проверки локальной БД.
- Считать `503 auth_backend_temporarily_unavailable` чисто сетевым или Promise.all-дефектом, если все protected reads ломаются одинаково после успешного login.

Open questions:
- Если такой тип порчи повторится, следующий уровень — вынести отдельный repair/consistency runbook для локального DuckDB-контура и подумать о более явной offline backup/restore процедуре.

[2026-06-15] — Hermes Web: self-check в backend ужесточён, markdown-renderer расширен стрелками и таблицами

Context:
- Пользователь попросил усилить backend-рамку так, чтобы агент перед ответом сам проверял полноту, отсутствие додумок и ложных claims, особенно про файлы и вложения.
- Параллельно во frontend Hermes Web нужно было расширить безопасный markdown-renderer: поддержать стрелку `$\\to$` и pipe-таблицы вида `|---|---|` без включения raw HTML.
- Browser snapshot/CDP path в этом сеансе оставался нестабильным, поэтому для живой проверки markdown пришлось разделить acceptance на два слоя: реальный backend/build/test и отдельный Playwright DOM-pass для frontend renderer.

Agreed:
- В system prompt Hermes Web нужен явный внутренний self-check перед финализацией ответа: проверить, что ответ закрывает запрос по существу, не пропускает важные части и не превращает гипотезы в факты.
- Агент не должен уверенно заявлять о данных, результатах, ссылках, файлах и вложениях, если они не подтверждены в текущем ответе.
- Markdown-поддержку надо расширять безопасно: без `dangerouslySetInnerHTML`, без raw HTML, через React nodes/text renderer.
- `$\\to$` и `$\\\\to$` должны отображаться как `→`; markdown-таблицы должны рендериться в нормальный `table` с заголовками и ячейками.

Implemented:
- `services/backend/app.py`:
  - в `build_hermes_system_prompt(...)` добавлен явный self-check блок перед финализацией ответа;
  - усилено анти-враньё: если результат не подтверждён, агент должен прямо это сказать и не маскировать пробел уверенным тоном.
- `services/backend/test_smoke.py`:
  - добавлена regression-проверка, что новый self-check текст реально присутствует в system prompt;
  - тест на `download_url` ослаблен до `startswith(...)`, потому что текущий backend по контракту добавляет `access_token` query-param к file download path.
- `services/frontend-react/src/App.jsx`:
  - добавлен `normalizeMarkdownText(...)` для конвертации `$\\to$` / `$\\\\to$` в `→`;
  - добавлен parse/render markdown-таблиц (`thead`/`tbody`) поверх текущего безопасного renderer;
  - paragraph/table cells теперь проходят через тот же inline markdown path.
- `services/frontend-react/src/styles.css`:
  - добавлены стили для markdown-таблиц, включая user-bubble variant.

Verified:
- `python3 -m pytest test_smoke.py` в `services/backend` → `34 passed`.
- `npm run react:build` → OK; собран свежий bundle `dist/frontend-react/assets/index-N-hWZ_VL.js` и `index-CLt3UHPF.css`.
- Live backend/prod-serve health локально:
  - `curl http://127.0.0.1:8791/api/health` → `status=ok`;
  - `curl http://127.0.0.1:8793/` и `curl http://127.0.0.1:8793/api/service-info` → frontend и proxy отвечают.
- Frontend markdown acceptance подтверждён отдельным headless Playwright DOM-pass на изолированном prod-like surface с mock API boot:
  - `arrowPresent=true`
  - `rawArrowTokenPresent=false`
  - `tableCount=1`
  - `thCount=2`
  - `tdCount=4`
  - headers: `Колонка`, `Значение`
  - cells: `alpha`, `1`, `beta`, `2`

Rejected:
- Ослаблять задачу до одной только prompt-формулировки без regression-проверки.
- Добавлять raw HTML / unsafe markdown rendering ради таблиц.
- Считать browser CDP/snapshot нестабильность доказательством поломки самого markdown-renderer.

Open questions:
- Если пользователь захочет следующий уровень защиты, можно добавить уже не только prompt self-check, а backend post-guard, который будет автоматически помечать suspicious assistant-claims про готовые файлы/результаты без attachment/path/download URL.
- Отдельным хвостом остаётся текущий boot/runtime-инцидент local prod-surface: после реального login параллельные `bootstrap/me/files/threads/jobs meta` в UI могли возвращать `503`, поэтому визуальная приёмка шла через изолированный mock-boot, а не через полный живой authenticated flow.

[2026-06-15] — Hermes Web 178: ужесточён file/export contract, чтобы агент не обещал файл без вложения

Context:
- В live-чате пользователя Виктории (`thread_id=21`, `Flatpak`) backend зафиксировал повторяющийся сбой пользовательского опыта: сообщения `115` и `117` содержали обещания вроде «Я приступаю к финальной сборке» и «Я подготовила финальный документ», но `attachment_count=0` и `message_kind` отсутствовал.
- При этом старый export-path в том же треде уже умел отдавать реальные `file_response` с вложением (`message_kind=file_response`, `attachment_count=1` в сообщениях `90/93/95/97`), то есть проблема была не в самом механизме выгрузки, а в том, что generic-фразы вроде «направить мне файл» / «давай файл» не всегда маршрутизировались в export-path.
- Пользователь попросил не просто объяснить сбой, а ужесточить правила на контуре `178`, чтобы агент перестал выдавать намерение за факт.

Agreed:
- Для Hermes Web 178 обещание «файл готов / документ подготовлен / ссылка приложена» допустимо только когда в этом же сообщении реально есть attachment/path/download URL.
- Generic file intent (`давай файл`, `пришли документ`, `направь файл`) нужно трактовать как запрос на реальную выгрузку предыдущего содержательного assistant-ответа в `docx`, а не отдавать это на свободную генерацию модели.
- Когда артефакт фактически не создан, правильное поведение — честно сказать об ограничении, а не имитировать готовый результат.

Implemented:
- `services/backend/app.py`:
  - в `build_hermes_system_prompt(...)` добавлено прямое правило: нельзя заявлять о готовом файле/ссылке/вложении без реального attachment/path/download URL в том же ответе;
  - `detect_message_export_format(...)` расширен generic-маркерами `docx`-выгрузки: `пришли файл`, `пришли документ`, `отправь файл`, `направь файл`, `давай файл`, `давай документ` и смежные варианты;
  - прежний explicit-format path (`pdf/docx/xlsx/...`) сохранён без изменений.
- `services/backend/test_smoke.py`:
  - добавлен regression, что generic user request `Давай файл` после обычного assistant-ответа уходит в реальный `file_response` с `docx`-вложением;
  - добавлена проверка, что новый запрет на ложные file-claims реально присутствует в system prompt.
- Изменённые `app.py` и `test_smoke.py` выложены на `178.104.207.89` в проект `/home/hermes/workspace/hermes-web-mvp-react-8793/services/backend`.

Verified:
- Локально: `python3 -m py_compile app.py test_smoke.py` → OK.
- Локально: `python3 -m unittest ...test_personalization_uses_user_profile_without_default_agent_name ...test_process_chat_task_exports_previous_answer_to_file ...test_process_chat_task_exports_previous_answer_for_generic_file_request ...test_process_chat_task_export_skips_service_messages_and_exports_last_content_answer` → `Ran 4 tests ... OK`.
- На `178`: те же 4 `unittest` под backend `.venv` → `Ran 4 tests ... OK`.
- На `178`: `systemctl --user restart hermes-web-backend-8791.service` под пользователем `hermes` → backend поднялся с новым `MainPID 486163`.
- Live acceptance на `178`: временный пользователь создал тред, получил обычный assistant-ответ, затем отправил `Давай файл`; backend вернул
  - `message_kind=file_response`
  - `export_format=docx`
  - `attachment_count=1`
  - `download_url=/api/messages/121/attachments/0?...`
  - `original_name=generic-export-...docx`
  Это подтвердило, что generic file request теперь создаёт реальный downloadable файл, а не пустое обещание.

Rejected:
- Оставлять generic запросы на файл полностью на усмотрение модели.
- Считать проблему чисто «качеством модели», если корень в отсутствии жёсткого backend-contract для file intent.
- Маскировать дефект инструкцией пользователю «просить точнее» вместо исправления маршрутизации.

Open questions:
- Если понадобится ещё жёстче, следующий уровень — backend-guard, который будет автоматически помечать/блокировать assistant-ответы с claims вида «файл готов» при `attachment_count=0`, даже если модель проигнорировала prompt.

[2026-06-11] — Hermes Web: фронт и бэк разделены по контурам, HTML-ошибки не выдавать пользователю

Context:
- Пользователь явно зафиксировал, что нельзя путать frontend и backend, а также dev и prod контуры.
- Инцидент показал два риска: ошибочное выключение не того контура и утечку HTML-полотна в пользовательскую выдачу при runtime-ошибках.

Agreed:
- Разделение контуров считать жёстким правилом эксплуатации: frontend, backend, dev и prod проверять и менять отдельно.
- Для текущей схемы: `95.182.85.233:8803` — frontend surface; `178.104.207.89:8791` — prod backend; локальные dev-порты `95.182.85.233:8791/8793/8794` не трогать как prod и не смешивать с backend на `178`.
- Пользовательская выдача при runtime-сбое не должна содержать HTML, CSS, raw upstream error или большие технические полотна.

Implemented:
- На `95.182.85.233` остановлен dev-контур `8791/8793/8794`; `8803` оставлен отдельным frontend surface.
- В `~/.config/systemd/user/hermes-web-frontend-8803.service` убраны зависимости `Requires/After` от локальных `8791/8794`, чтобы frontend `8803` не падал вместе с dev-контуром.
- В `services/backend/app.py`:
  - `normalize_public_error_text(...)` усилен: распознаёт HTML и экранированный HTML по типовым маркерам страницы;
  - `finalize_chat_task_error(...)` больше не кладёт `raw_error_text` в пользовательский `message.meta`; сырой текст остаётся только во внутреннем `chat_tasks.last_error`.
- Фикс backend выложен на prod `178.104.207.89`.

Verified:
- `ss -ltnp` на `95.182.85.233` после cleanup показывает только `8803`; `8791/8793/8794` не слушаются.
- `curl -I http://127.0.0.1:8803/` → `200 OK`.
- `curl http://127.0.0.1:8803/api/service-info` → `200 OK`.
- `python3 -m py_compile services/backend/app.py` → OK.
- `python3 -m unittest services/backend/test_smoke.py` → `Ran 24 tests ... OK`.
- На `178.104.207.89`: `curl http://127.0.0.1:8791/api/service-info` → `200 OK` после выкладки и рестарта backend.

Rejected:
- Смешивать frontend-host и backend-host в одном operational-шаге без явной проверки контура.
- Хранить `raw_error_text` в пользовательском сообщении, если там может оказаться HTML или другой сырой upstream output.

Open questions:
- При следующем раунде стоит добавить явную runtime-карту контуров в runbook или startup banner, чтобы роль каждого порта была видна до любых операций.

[2026-06-11] — Hermes Web dashboard grammar: комбинированную диаграмму делать как один общий stacked chart без дублирующих секций

Context:
- Пользователь уточнил, что правило нельзя хардкодить под даты, дни или Telegram-кейс.
- Нужна общая grammar-логика для случаев, где одна ось показывает основные бакеты, а внутри каждого бакета нужно показать состав по категориям.

Agreed:
- Если пользователь просит комбинированную диаграмму, целевой UX — один общий chart-object, а не набор отдельных объектов по каждому бакету.
- Основная ось может быть числовой или категориальной — например даты, периоды, каналы, сегменты, диапазоны.
- Внутри каждого бакета должны отображаться категориальные составляющие как stacked-разбивка.
- Если одна комбинированная диаграмма уже показывает основной сюжет, не нужно оставлять отдельные вспомогательные секции, которые дублируют ту же историю, если их явно не просили.
- Категории вне top-N нельзя обнулять: они должны агрегироваться в `прочее`, чтобы total по бакету оставался честным.

Implemented:
- `services/backend/app.py`:
  - генерация локального Telegram dashboard переведена на `bar_list` c `meta: series=...; total_day=...; raw_day=...` как первый reusable-path для stacked-комбинации;
  - не вошедшие в top-5 типы агрегируются в `прочее`.
- `services/frontend-react/src/App.jsx`:
  - renderer `bar_list` с series/meta-path переведён на единый stacked chart вместо списка отдельных bucket-cards.
- `services/frontend-react/src/styles.css`:
  - добавлены стили для единого вертикального stacked chart.

Verified:
- `python3 -m pytest services/backend/test_smoke.py -q` → `10 passed`.
- `npm run react:build` → OK.

Rejected:
- Хардкодить правило под конкретно дни, даты или Telegram-аналитику.
- Рисовать один объект на каждый бакет вместо одного общего графика.
- Терять хвост категорий вне top-N вместо агрегации в `прочее`.

Open questions:
- Если дальше понадобится richer chart grammar, стоит ли выделить stacked combined chart в отдельный явный chart-kind вместо implicit `bar_list + meta series`.

[2026-06-15] — Hermes browser/Web UI: убрать browser-tool CDP 404, вернуть стабильный preview файлов и починить runtime-пропсы экранов

Context:
- Browser-инструменты несколько раз подряд упирались в `CDP 404`/нестабильный screenshot path при `browser_vision`; параллельно во фронте после cleanup остались runtime-рассинхроны по prop names, из-за которых отдельные экраны и модалки могли ломать web-форму.
- Пользователь отдельно уточнил, что `95` — это frontend surface, а не внешний SSH-объект для каждой проверки; приоритет — чинить сам UI и runtime.

Agreed:
- Для screenshot/vision-path Hermes должен сначала использовать уже живой CDP supervisor/session, а не слепо открывать отдельный CLI screenshot-path.
- Frontend preview файлов из профиля должен открываться в заметно более широком modal-окне и масштабировать изображение по viewport.
- После UI cleanup нельзя оставлять prop-name drift между `App.jsx` и screen/modal компонентами: такие рассинхроны считаются runtime-дефектом даже если сборка проходит.

Implemented:
- В `tools/browser_supervisor.py` добавлен live-CDP path `capture_screenshot(...)` через `Page.captureScreenshot` для reuse текущей browser session.
- В `tools/browser_tool.py`:
  - `browser_vision` сначала пытается снять screenshot через supervisor, и только потом падает обратно в CLI screenshot path;
  - в env browser subprocesses добавлена инъекция локального runtime-tree `~/runtime/browser-libs/root` для fontconfig/fonts-path.
- В `services/frontend-react/src/App.jsx` исправлены runtime prop bindings для `ThreadsModal`, `AdminUserModal`, `InteractionSetupModal`, а также parent→`AdminScreen` binding `onToggleUser`.
- В `services/frontend-react/src/styles.css` расширен `file-preview-modal` и увеличены limits/stage для auto-fit preview изображений.

Verified:
- Hermes browser tools снова отрабатывают без `CDP 404`: `browser_navigate`, `browser_snapshot`, `browser_console`, `browser_vision` возвращают успешный результат.
- `npm run react:build` → OK; собраны `index-gdaXic8M.js` и `index-Okenup__.css`.
- `browser_console` на `http://95.182.85.233:8803` на стартовом экране не показывает JS errors.

Rejected:
- Продолжать диагностировать frontend surface `95` через SSH как основной путь, когда проблема уже локализуется и воспроизводится в коде/UI runtime.
- Считать passed build достаточным доказательством, если после cleanup есть явные runtime prop mismatches.

Open questions:
- В текущем runtime screenshot уже не падает по `CDP 404`, но визуальный capture всё ещё может быть пустым; это отдельный слой рендеринга/browser runtime, который стоит добить отдельным hardening-pass.

[2026-06-15] — Hermes Web UI: вкладка задач не должна падать по runtime-именам, mobile должен показывать навигацию, чат должен сам подтягивать обновления

Context:
- Пользователь сообщил, что вкладка `Задачи` всё ещё не работает, а на mobile без принудительных обновлений новые сообщения в чате не видны.
- Live-проверка локального dev frontend сначала показала, что сама навигация ломалась не только из-за overlay, но и из-за runtime-рассинхронов имён обработчиков: `handleUpdateJobDisplayName`, `handleOpenCreateJob`, `handleOpenEditJob`, `handleOpenRecipientsModal`, `handleOpenAccessModal` отсутствовали в `App.jsx`, хотя именно они пробрасывались в `JobsScreen`.
- Для локальной live-приёмки дополнительно выяснилось, что dev proxy нельзя направлять на `95.182.85.233:8791`: этот порт сейчас не backend и отвечает `Connection refused`; рабочий backend для проверки — `178.104.207.89:8791`, а frontend surface пользователя остаётся `95.182.85.233:8803`.

Agreed:
- Вкладка `Задачи` считается сломанной, если сборка проходит, но runtime падает из-за prop/handler drift при первом переходе на экран.
- Mobile-навигация не должна скрывать кнопку `Задачи`; onboarding-подсказка не должна блокировать pointer events по основным разделам.
- Чатовый экран должен сам подтягивать обновления без ручного refresh, особенно пока в сообщениях есть pending assistant placeholder.
- Preview файлов из профиля считается рабочим только после live-проверки открытия модального preview, а не только по коду.

Implemented:
- В `services/frontend-react/src/App.jsx`:
  - `JobsScreen` переведён на реальные обработчики `handleUpdateDisplayName`, `openCreateJob`, `openEditJob`, `openRecipientsPicker`, `openAccessPicker` вместо несуществующих runtime-имён;
  - `handleNavigate(...)` закрывает onboarding перед переходом между разделами;
  - добавлен polling chat-state: немедленный первый refresh, затем `2500 ms` при pending assistant и `8000 ms` в обычном режиме.
- В `services/frontend-react/src/styles.css`:
  - mobile больше не скрывает `.nav-btn-jobs`;
  - onboarding modal/backdrop переведены в неблокирующий режим;
  - основные контейнеры переведены с `100vh` на `100dvh` для более стабильного mobile viewport.
- Preview файлов из профиля проверен на живом UI-path через отдельного acceptance-пользователя с загруженным PNG.

Verified:
- `npm run react:build` → OK после правок; собран `assets/index-Bq4o1xHs.js`.
- `http://127.0.0.1:4173/api/service-info` при dev-приёмке с backend `178.104.207.89:8791` → `200 OK`.
- Live Playwright-проверка на локальном dev frontend (`127.0.0.1:4173`) подтвердила:
  - `Задачи` открываются без runtime-crash; экран показывает `Задачи Hermes`, список задач и детали выбранной задачи;
  - на mobile кнопка `Задачи` видима, активируется и открывает тот же экран;
  - profile files preview работает end-to-end: `openCount=1`, `modal=1`, `img=1`, preview-ссылка ведёт на `/api/files/3/download?...`.
- Browser runtime path по Hermes Agent отдельно прогнан через `pytest -q tests/tools/test_browser_cloud_fallback.py tests/tools/test_browser_console.py` → `39 passed`.

Rejected:
- Считать проблему вкладки `Задачи` решённой только потому, что JSX собирается без ошибок.
- Держать mobile-ветку с скрытой кнопкой `Задачи` и блокирующим onboarding overlay.
- Опираться на dev proxy к `95.182.85.233:8791`, когда реальный backend для этой схемы живёт на `178.104.207.89:8791`.

Open questions:
- Текущая live-приёмка подтверждена на локальном dev frontend `127.0.0.1:4173`; если нужно закрыть именно пользовательский surface `95.182.85.233:8803`, следующим шагом нужна отдельная выкладка/перезапуск этого frontend-контура и повторная приёмка уже на нём.
- В chat polling-проверке pending placeholder не удалось удержать достаточно долго: backend ответил слишком быстро, поэтому сам механизм подтверждён по коду и по отсутствию ручного refresh в локальном UX, но не длинным live-run с висящим pending.

[2026-06-15] — Hermes Web: export должен брать последний содержательный assistant reply, а не service/error message; стандартный timeout не резать до 60 секунд

Context:
- В треде Виктории/Flatpak проявились два связанных дефекта: export-цепочка могла брать последний assistant message без фильтрации и экспортировать `file_response`/ошибку/служебный ответ, а стандартный Hermes API retry-path фактически работал с 60-секундным окном.
- Пользователь отдельно указал, что такие решения и закрытые инциденты нужно фиксировать в `decision-log.md` по умолчанию.

Agreed:
- Для message export целевым источником считается последний нормальный содержательный assistant reply, а не любой последний assistant message.
- Из export-кандидатов нужно исключать как минимум `processing_status`, `file_response`, пустые/служебные ответы и fallback/error-сообщения вида `Не удалось получить ответ...`.
- Стандартный timeout для Hermes Web chat-task path не должен молча ужиматься до 60 секунд на промежуточной retry-попытке; для обычных model attempts используется полный `HERMES_API_TIMEOUT`.
- Закрытые технические решения такого уровня фиксируются в `decision-log.md` без отдельного напоминания от пользователя.

Implemented:
- В `services/backend/app.py`:
  - `maybe_build_export_reply(...)` переведён с логики "первый попавшийся assistant с конца" на явный отбор через `is_exportable_assistant_message(...)` и `select_export_target_message(...)`;
  - из export path исключены `message_kind=file_response`, `message_kind=processing_status`, error-meta, пустой/service placeholder и ответы с текстом `Не удалось получить ответ...`;
  - `HERMES_API_RETRY_TIMEOUT` по умолчанию больше не вычисляется как `min(HERMES_API_TIMEOUT, 60)`;
  - `call_hermes_messages_timeout(...)` для standard model path возвращает полный `HERMES_API_TIMEOUT`, без урезания первой попытки fallback-цепочки до 60 секунд.
- В `services/backend/test_smoke.py` добавлены и обновлены smoke-проверки под новый export-selection и timeout behavior.
- Фикс выложен на prod backend `178.104.207.89:8791` с рестартом `hermes-web-backend-8791.service`.

Verified:
- Локально: `python3 -m py_compile app.py` → OK.
- Локально: `python3 -m pytest test_smoke.py::HermesWebBackendSmokeTest::test_process_chat_task_exports_previous_answer_to_file test_smoke.py::HermesWebBackendSmokeTest::test_call_hermes_messages_uses_full_timeout_before_last_fallback test_smoke.py::HermesWebBackendSmokeTest::test_process_chat_task_export_skips_service_messages_and_exports_last_content_answer test_smoke.py::HermesWebBackendSmokeTest::test_call_hermes_messages_uses_full_timeout_for_all_standard_attempts -v` → `4 passed`.
- На `178.104.207.89`: `systemctl --user restart hermes-web-backend-8791.service` → сервис поднялся; `curl http://127.0.0.1:8791/api/service-info` → `{"mode":"hermes-api","service":"Hermes Web","status":"ok"}`.
- На `178.104.207.89`: `.venv/bin/python -m unittest ...` по 4 профильным smoke-тестам → `Ran 4 tests ... OK`.
- Изолированная live-проверка export/timeout path локально и на `178` показала одинаковый результат: timeout probe = `[180, 180]`, export probe выбрал именно содержательный ответ, а не error/service message.

Rejected:
- Оставлять export-flow на эвристике "просто последний assistant message".
- Сохранять скрытый 60-секундный retry-timeout как поведение по умолчанию для standard model path.

Open questions:
- Если реальные user-turns всё ещё иногда доходят до timeout уже на полном `HERMES_API_TIMEOUT`, следующий шаг — смотреть не на искусственное ограничение, а на причины долгого ответа upstream/runtime по конкретным model routes.

[2026-06-11] — Hermes Web: старый контур 8791/8793/8794 оставлен как dev, новый frontend поднят отдельно на 8803

Context:
- Пользователь уточнил целевую схему: старое размещение `8791/8793/8794` не выключать, а оставить как dev-контур.
- Для нового серверного входа нужен отдельный frontend на новом порту без ломки текущего dev-runtime.

Agreed:
- `8791/8793/8794` остаётся живым dev-контуром.
- Новый frontend поднимается отдельно на `8803`.
- Backend и CopilotKit runtime для нового frontend пока переиспользуются из текущего контура через proxy `/api`, без лишнего дублирования backend/runtime.

Implemented:
- Создан user-systemd unit `~/.config/systemd/user/hermes-web-frontend-8803.service`.
- Unit запускает тот же проект `/home/hermes/workspace/hermes-web-mvp-react-8793`, но с env:
  - `HERMES_WEB_FRONTEND_HOST=0.0.0.0`
  - `HERMES_WEB_FRONTEND_PORT=8803`
- Unit включён и запущен через `systemctl --user enable --now hermes-web-frontend-8803.service`.

Verified:
- `systemctl --user status hermes-web-frontend-8803.service` → `active (running)`.
- `ss -ltnp` показал listener на `0.0.0.0:8803`.
- `curl -I http://127.0.0.1:8803/` → `HTTP/1.1 200 OK`.
- `curl http://127.0.0.1:8803/api/service-info` через frontend proxy вернул `status=ok`, `service=Hermes Web`, `mode=hermes-api`.
- Одновременно активны оба frontend unit’а: `hermes-web-frontend-8793.service` и `hermes-web-frontend-8803.service`.

Rejected:
- Перетаскивать backend/runtime на отдельные новые порты без явной необходимости.
- Выключать старый контур до подтверждения, что он нужен только как dev.

Open questions:
- Нужен ли следующий шаг с отдельным reverse proxy / доменом для `8803`, или пока достаточно прямого портового входа.


[2026-06-11] — Hermes Web React 8793: bootstrap reference-path ужат перед переходом к новой архитектуре

Context:
- После cleanup health/admin/jobs-paths следующим самым тяжёлым GET оставался `/api/bootstrap`.
- Разбор показал, что его основная цена сидела не в profile/chat_notice/policy, а в сборке runtime reference views.

Agreed:
- До смены плановой архитектуры стоит добирать только низкорисковые улучшения текущего local-first контура.
- `/api/bootstrap` не должен дважды сканировать один и тот же reference-слой ради active/inactive представлений.
- Для reference views допустим revision-aware cache, если он автоматически инвалидируется по изменению `reference_items`/`reference_catalogs`.

Implemented:
- `services/backend/app.py`:
  - `build_runtime_reference_views(...)` перестроен на один `build_reference_payload(include_inactive=True)` с derivation active-items из уже собранного payload;
  - добавлены `get_runtime_reference_views_revision(...)` и `get_cached_runtime_reference_views(...)`;
  - `/api/bootstrap` переведён на revision-aware cache reference views;
  - `normalize_job_payload(...)` тоже переведён на cached runtime refs вместо полной повторной сборки.
- `RUNTIME-RUNBOOK.md`:
  - добавлено правило, что `/api/bootstrap` не должен повторно собирать весь runtime reference payload по два раза.

Verified:
- `python3 -m unittest services/backend/test_smoke.py` → `Ran 10 tests ... OK`.
- `python3 -m py_compile services/backend/app.py` → OK.
- Дополнительная проверка cache invalidation на временной DB: после изменения `reference_items` ответ `/api/bootstrap` отдал новое значение, то есть cache не залипает на старом reference payload.
- `systemctl --user restart hermes-web-backend-8791.service` → сервис поднялся.
- Latency на audit-копии live DB:
  - `/api/bootstrap`: ~223 ms baseline до bootstrap-раунда → ~190 ms после single-pass сборки → ~167 ms на тёплом revision-cache;
  - cold/warm последовательность bootstrap-запросов: первый ~205 ms, повторные ~138–178 ms.

Rejected:
- Вводить новый внешний cache/store только ради bootstrap-path перед архитектурным пересмотром.
- Оставлять двойную сборку reference payload внутри текущего bootstrap-flow.

Open questions:
- После этого `/api/jobs` всё ещё остаётся самым тяжёлым крупным GET; если возвращаться ещё к текущему контуру до переезда, следующий кандидат — уменьшение payload/detail depth или разрезание jobs-list и jobs-detail paths.

[2026-06-11] — Hermes Web React 8793: предмиграционный cleanup hot GET-paths и cron-bridge latency

Context:
- После фикса `/api/health` пользователь попросил добить остальные исправимые до переезда latency-хвосты в backend.
- Аудит на копии live DuckDB показал, что главные дорогие GET-paths были не в frontend shell, а в `/api/jobs`, `/api/admin/user-sources`, `/api/admin/jobs`, `/api/bootstrap`, `/api/jobs/meta`.

Agreed:
- До переезда выгоднее сначала убирать скрытую дорогую работу из hot GET-paths, чем раздувать инфраструктуру или переносить backend раньше времени.
- Нормальные read-paths не должны делать write-on-GET (`sync_data_source_registry`) без явной необходимости.
- Hermes cron bridge нельзя дёргать subprocess-ом на каждый reload overview/jobs/admin-paths; для таких мест допустим только короткий TTL-cache или отдельный dedicated endpoint.
- Узкие endpoint’ы вроде `feedback/reasons` и `jobs/meta` должны собирать только нужный набор reference-данных, а не весь runtime reference payload.

Implemented:
- `services/backend/app.py`:
  - `/api/health` уже ранее переведён на локальные DB-счётчики;
  - добавлен `list_cached_hermes_jobs()` с коротким TTL-cache для Hermes cron bridge;
  - `/api/admin/jobs` переведён с прямого `hermes_list_jobs()` на cache;
  - `/api/admin/user-sources` больше не делает `sync_data_source_registry()` и не тянет cron bridge; `jobs_count` берётся из локальной таблицы `jobs`;
  - `/api/admin/dashboard-policy` больше не делает write-on-GET;
  - `/api/feedback/reasons` сузили до выборки только нужного dataset;
  - `/api/jobs/meta` сузили до выборки только `job_templates` вместо полного runtime reference view;
  - `/api/jobs` убран N+1-path на список локальных jobs: owner/acl/subscriptions/counts подготавливаются батчами, а cron bridge идёт через cache.
- `services/backend/test_smoke.py`:
  - добавлен regression, что `/api/admin/user-sources` остаётся рабочим даже если `hermes_list_jobs` ломается.
- `RUNTIME-RUNBOOK.md`:
  - добавлены правила, что admin GET-paths не должны делать write-on-GET и что cron bridge на overview/admin-paths допускается только через короткий cache.

Verified:
- `python3 -m unittest services/backend/test_smoke.py` → `Ran 10 tests ... OK`.
- `python3 -m py_compile services/backend/app.py` → OK.
- `systemctl --user restart hermes-web-backend-8791.service` → сервис поднялся.
- Повторный latency-аудит на копии live DB:
  - `/api/jobs`: ~864 ms → ~225 ms;
  - `/api/admin/user-sources`: ~675 ms → ~113 ms;
  - `/api/admin/jobs`: ~537 ms → ~57 ms;
  - `/api/jobs/meta`: ~202 ms → ~119 ms;
  - `/api/feedback/reasons`: ~139 ms → ~59 ms;
  - `/api/health`: удержан около ~50–63 ms на audit path.

Rejected:
- Оставлять `sync_data_source_registry()` внутри обычных admin GET-paths.
- Считать медленный `/api/jobs` чисто «проблемой сервера», если внутри есть N+1 и bridge/subprocess cost.
- Возвращаться к прямому `hermes_list_jobs()` на каждый reload jobs/admin overview без новых данных.

Open questions:
- `/api/bootstrap` после cleanup остаётся одним из самых тяжёлых путей из-за большого reference payload; если до переезда понадобится ещё один раунд оптимизации, следующий кандидат — cache/invalidation для runtime reference views без потери консистентности admin-редактирования.

[2026-06-11] — Hermes Web React 8793: backend concurrency и full React smoke закрыты, backlog переведён в hardening-режим

Context:
- После предыдущего цикла оставались два хвоста: нестабильность `/api/admin/chat-notice` под параллельной нагрузкой и flaky full acceptance в `scripts/ui_acceptance_smoke_react.mjs`.
- Пользователь попросил не просто устно зафиксировать, а самостоятельно обновить проектный backlog и документацию под фактическое состояние после добивки.

Agreed:
- Источником истины считается не промежуточная гипотеза, а реальные прогоны regression/build/live smoke.
- Если full acceptance уже проходит, backlog не должен продолжать описывать задачу как «ещё не доведённую».
- Документация должна явно различать продуктовый дефект и testability/hardening-хвосты.

Implemented:
- `services/backend/app.py`:
  - добавлен retry-path на открытии/инициализации DuckDB-соединения, чтобы переживать `Binder Error` / `Unique file handle conflict` / `TransactionContext Error` при конкурентном доступе.
- `services/backend/test_smoke.py`:
  - добавлен конкурентный regression-тест на `/api/admin/chat-notice`.
- `scripts/ui_acceptance_smoke_react.mjs`:
  - admin-часть переведена с `localStorage + reload` на реальные tab-клики по `data-admin-section` и явные ожидания активной секции/модалки.
- Документация:
  - обновлены `docs/BACKLOG.md`, `docs/DEPLOYMENT_GUIDE.md`, `RUNTIME-RUNBOOK.md`.

Verified:
- `python3 -m py_compile services/backend/app.py` → OK.
- `python3 -m unittest services/backend/test_smoke.py` → `Ran 10 tests ... OK`.
- `npm run react:build` → OK.
- `source scripts/runtime_env.sh && ./scripts/browser_runtime_env.sh node scripts/ui_acceptance_smoke_react.mjs` → OK.

Rejected:
- Оставлять в backlog формулировку, что full React acceptance ещё не доведён, после успешного end-to-end прогона.
- Смешивать backend concurrency bug и flaky smoke-script в одну неразличимую проблему.

Open questions:
- Нужен ли отдельный sequence/request-token guard в `loadAdmin()` как профилактический hardening сверх уже рабочего сценария.

[2026-06-10] — Hermes Web React 8793: dashboard_result без псевдо-accordion, с обязательными видимыми визуализациями

Context:
- На live-экране chat-first ответа пользователь увидел только KPI-карточки и набор заголовков вроде «Что можно считать фактом / Оценка рынка 2025 / Топ-5 ОС...», которые визуально выглядели как нерабочие раскрывашки.
- Корень проблемы оказался двойным: backend prompt для external dashboard просил слишком бедную JSON-структуру, а frontend renderer умел показывать только `bar_list` и `post_list`, поэтому текстовые sections без явного renderer превращались в пустые белые плашки.

Agreed:
- В chat-first контуре `dashboard_result` не должен выглядеть как заготовка под будущий UI.
- Для внешних dashboard-ответов нужно требовать не только KPI-карточки, но и минимум две видимые визуальные секции, если есть количественные данные.
- Никаких accordion/details/collapsible-паттернов в сообщении чата: весь смысл должен быть виден сразу без дополнительных кликов.
- Если секция текстовая, она должна рендериться как обычный раскрытый список, а не как пустой заголовок.

Implemented:
- `services/backend/app.py`:
  - prompt `build_global_dashboard_prompt(...)` расширен: теперь требует `subtitle`, `summary_cards.note`, typed `sections` (`text_list`, `bar_list`, `pie_list`, `bubble_list`, `post_list`), минимум две визуальные секции при наличии количественных срезов и прямой запрет на accordion/collapsible/hidden-блоки.
- `services/frontend-react/src/App.jsx`:
  - `DashboardArtifact` переписан так, чтобы поддерживать `text_list`, `pie_list`, `bubble_list` и fallback-рендер обычных текстовых секций;
  - секции теперь всегда показывают содержимое сразу, а не только заголовок.
- `services/frontend-react/src/styles.css`:
  - добавлены стили для bullet-list, pie/donut-рендера и bubble-визуализаций.

Verified:
- `python3 -m py_compile services/backend/app.py` → OK.
- `npm run react:build` → OK.
- `python3 -m unittest services/backend/test_smoke.py` → `Ran 7 tests ... OK`.
- `systemctl --user restart hermes-web-backend-8791.service hermes-web-frontend-8793.service` → оба сервиса поднялись.
- `GET /api/service-info` на `8791` возвращает `mode=hermes-api`.

Limitations:
- Полный live external dashboard round-trip в момент фикса не подтвердился до конца, потому что backend-запрос к Hermes API на большой внешний dashboard ушёл в timeout; значит prompt-усиление и новый renderer проверены сборкой, тестами и runtime-рестартом, но отдельная живая приёмка именно на длинном web-research ответе ещё остаётся хвостом.
- Browser acceptance script для полного UI smoke на этом сервере сейчас не проходит из-за отсутствующей системной зависимости `libnspr4.so` для Playwright Chromium.

Rejected:
- Оставлять sections в виде полупустых белых карточек «на будущее».
- Полагаться только на KPI-карточки как на достаточную визуализацию dashboard-результата.
- Использовать в chat message скрываемые секции, которые без live интерактива выглядят сломанными.

Open questions:
- Отдельно стоит решить, нужен ли дальше ещё один специализированный renderer для richer chart grammar вроде timeline/stacked bars, если Hermes начнёт стабильно возвращать более сложные dashboard payload.

[2026-06-07] — Hermes Web React 8793: headless acceptance quirk записан в backlog, docs/package доведены до фактического runtime

Context:
- После закрытия live round-trip по chat/profile/jobs/admin осталась не продуктовая, а testability-аномалия: в headless Playwright обычный click по admin tabs (`Обзор / Пользователи / Операции / Справочники`) мог не менять `adminSection`, хотя runtime и данные были корректны.
- Пользователь попросил не потерять этот хвост, а явно зафиксировать его в backlog и одновременно довести документацию и deploy-пакет до реального acceptance-path.

Agreed:
- Странность headless admin-tabs не блокирует текущую приёмку, потому что live runtime и все ключевые round-trip сценарии уже подтверждены.
- Аномалию нужно хранить не в памяти разговора, а в проектном backlog, чтобы к ней можно было вернуться как к отдельной UI hardening-задаче.
- Deploy/docs должны описывать не идеализированный путь, а текущий проверенный runtime, включая optional browser acceptance.

Implemented:
- Создан `hermes-web-mvp-react-8793/docs/BACKLOG.md` с отдельной записью про нестабильное переключение admin tabs в headless acceptance.
- Обновлены `hermes-web-mvp-react-8793/README.md`, `hermes-web-mvp-react-8793/docs/DEPLOYMENT_GUIDE.md`, `hermes-web-mvp-react-8793/deploy/package/README.md`.
- `deploy/package/verify-deployment.sh` усилен: теперь при наличии `HERMES_WEB_SMOKE_EMAIL` и `HERMES_WEB_SMOKE_PASSWORD` он умеет дополнительно запускать `scripts/ui_acceptance_smoke_react.mjs`.
- Deploy archive должен собираться заново из актуального `deploy/package/` после этих обновлений.

Verified:
- Live acceptance ранее уже подтвердил `chat/profile/jobs/admin` round-trip.
- Документационные и packaging-изменения отражают фактический runtime `8791/8793/8794` и канонический acceptance-path через `runtime_env.sh` / `browser_runtime_env.sh`.

Rejected:
- Считать headless tab-аномалию backend-проблемой.
- Терять этот хвост в устной договорённости без явной проектной фиксации.
- Оставлять deploy verification только на уровне HTTP/build без опционального UI smoke.

Open questions:
- Отдельной задачей остаётся понять, почему React onClick по admin tabs в headless-сеансе не всегда доходит до state-switch, несмотря на наличие handler и отсутствие overlay.

[2026-06-07] — Hermes Web React 8793: chat policy упрощена до 3 режимов, admin управляет контурами, deploy/docs приведены к каноническому runtime

Context:
- Пользователь потребовал убрать из chat UI админские сущности: обычный пользователь не должен управлять реестром источников, составом коннекторов и внутренним/внешним контуром.
- Дополнительно потребовалось не просто починить UI, а довести весь канонический контур `8793/8791/8794`, подготовить развёртывание на другой сервер, сделать полное системное описание и отдельный сценарий тестирования для роли user.
- Во время проверки был выявлен опасный runtime mismatch: frontend уже шёл из `hermes-web-mvp-react-8793`, а backend на `8791` в ряде запусков продолжал жить из другого каталога, что могло давать ложную приёмку.

Agreed:
- В чате пользователь управляет только режимом обработки запроса: `local_only`, `local_first`, `global_only`.
- Явный файл, ссылка, dataset или connector — это request-level source override, а не новый глобальный режим.
- Состав inventory и принадлежность API/коннектора к внутреннему или внешнему контуру — только admin layer.
- Канонический runtime нужно верифицировать только как единый проектный контур: frontend, backend и CopilotKit runtime должны относиться к одному project root.
- Документация должна быть не в формате changelog, а в формате полного описания системы и эксплуатации.

Implemented:
- Frontend `services/frontend-react/src/App.jsx`:
  - `readChatSourcePolicyFromDom()` упрощён до передачи только `source_mode`;
  - из chat UI убрано ручное управление верхнеуровневыми источниками и дочерними коннекторами;
  - в чате оставлен компактный блок выбора режима и информирующая плашка по разрешённым источникам;
  - admin overview/policy блок переписан под русские прикладные тексты и отдельную классификацию коннекторов;
  - `handleSaveDashboardPolicy(...)` теперь отправляет `connector_group_overrides` в backend.
- Backend `services/backend/app.py`:
  - добавлены `normalize_connector_group_overrides(...)`, `persist_connector_group_overrides(...)`, `apply_connector_group_overrides_to_data_sources(...)`;
  - `dashboard-policy` patch-path теперь принимает admin override классификации коннекторов;
  - bootstrap/data-sources path начал отражать effective contour group поверх discovery.
- Runtime:
  - подтверждён и выровнен канонический user-systemd contour для `8791/8793/8794`;
  - frontend service выведен из restart-loop после устранения ручного конфликта за `8793`.
- Docs/deploy:
  - обновлён `README.md` как короткая точка входа;
  - созданы/переписаны `docs/SYSTEM_OVERVIEW.md`, `docs/DEPLOYMENT_GUIDE.md`, `docs/TESTING_SCENARIO.md`;
  - собран каталог `deploy/package/` с env-example, systemd units, install-script и verify-script.

Verified:
- `python3 -m py_compile services/backend/app.py` → OK.
- `npm run react:build` → OK.
- `python3 -m unittest services/backend/test_smoke.py` → `Ran 7 tests ... OK`.
- Live runtime:
  - `http://127.0.0.1:8791/api/service-info` → `200`;
  - `http://127.0.0.1:8793` → `200`;
  - CopilotKit runtime service на `8794` активен и слушает `/copilotkit`.
- Live admin API:
  - login под admin после локального dev-reset пароля подтверждён;
  - `GET/PATCH/GET /api/admin/dashboard-policy` → `200`;
  - перенос `hermes_api` из `internal_connector` в `external_connector` отражён в `bootstrap.data_sources`, затем состояние восстановлено обратно.

Rejected:
- Возвращать в chat UI чекбоксы inventory и ручной выбор коннекторов.
- Вводить отдельный пользовательский режим вроде `link-only`.
- Считать приёмку валидной, если frontend и backend подняты из разных project roots.
- Оставлять документацию как набор заметок о починках без цельной модели системы.

Reflection:
- Главный риск оказался не только в UI, а в смешанном runtime: без проверки project root легко получить "зелёный" frontend поверх чужого backend.
- Для local-first контура это особенно критично: правильная эксплуатация начинается не с новых сервисов, а с дисциплины вокруг канонического пути, inventory и ролей.

Open questions:
- Если позже понадобится production-grade упаковка, следующий шаг — не новая логика policy, а более строгий процесс поставки: единый install flow, backup policy и formalized smoke for deployment.

[2026-06-07] — Hermes Web React 8793: canonical dashboard policy/inventory и live admin round-trip

Context:
- Пользователь уточнил, что реестр источников не должен сводиться к частному `telegram_digest`: внутри продукта уже есть Google API, Telegram API, procurement/tender API и другие данные за пределами одного дайджеста.
- Требование по приёмке было жёстким: нужна не декларация, а реальное доказательство, что `local_only` отрезает любые внешние источники, `global_only` — любые внутренние, а admin policy/sources блок реально работает в live runtime.
- Ограничение сохранилось прежним: ничего не выносить во внешний SaaS/новую инфраструктуру, а довести текущий local-first контур `8793/8791/8794`.

Agreed:
- Верхний пользовательский policy-слой для dashboard остаётся минимальным: `local_only`, `local_first`, `global_only`.
- Явный файл, ссылка, attachment, dataset или connector — это request-level source override, а не отдельный четвёртый глобальный режим.
- Source registry должен отражать классы источников и connector groups, а не один частный dataset/дайджест.
- Приёмка считается закрытой только если есть и backend-доказательство отсечения local/global, и live admin save/reload/read round-trip.

Implemented:
- Backend `services/backend/app.py`:
  - восстановлен canonical dashboard inventory через живой sync/reactivation path;
  - `setup_status()` защищён от кратких DuckDB lock-конфликтов и больше не валит frontend bootstrap случайным `500`;
  - `require_auth()` получил retry-path для кратких `duckdb.IOException` / `duckdb.BinderException`, чтобы admin save/read paths не падали до бизнес-логики.
- Runtime/admin policy:
  - canonical top-level inventory приведён к модели `user_attachment_dataset`, `local_dataset_registry`, `internal_connector`, `external_connector`, `web_research`;
  - internal connectors подтверждены как `hermes_api`, `copilotkit_runtime`, `telegram_analytics_workspace`;
  - external connectors подтверждены как `telegram_api`, `google_api`, `public_procurement_api`.
- Live acceptance:
  - через UI подтверждён save/reload/read round-trip policy-блока в admin: `global_only -> local_only -> restore`.

Verified:
- Backend smoke: `python3 -m unittest services.backend.test_smoke -v` → `Ran 7 tests ... OK`.
- Live runtime:
  - `http://127.0.0.1:8791/api/service-info` → `200`;
  - `http://127.0.0.1:8791/api/setup/status` → `200`.
- Live admin/UI:
  - policy-блок загружает `5` верхнеуровневых источников и `6` дочерних коннекторов;
  - `PATCH /api/admin/dashboard-policy` после runtime-фиксов возвращает `200`;
  - повторное чтение policy подтверждает изменение режима и успешный restore.
- Contract по policy:
  - `local_only` возвращает только local/internal источники;
  - `global_only` возвращает только external/global источники;
  - `local_first` допускает оба слоя с локальным приоритетом.

Rejected:
- Оставлять registry в продуктовой модели как ссылку на один `telegram_digest`.
- Добавлять новый пользовательский режим вроде `link-only` или смешивать explicit source override с global policy mode.
- Мириться с тем, что краткий DuckDB lock в `setup/status` или `require_auth()` случайно валит весь admin/runtime path.

Reflection:
- Проблема оказалась не в отсутствии Google/Telegram/procurement в коде, а в том, что legacy/sync path раньше деактивировал canonical keys и не возвращал их в active.
- Для local-first контура такие дефекты особенно опасны: UI может выглядеть как «неправильная policy-модель», хотя корень — в runtime/concurrency и деградации auth/bootstrap path.

Open questions:
- Если позже потребуется усилить надёжность под высокой параллельностью, следующий логичный шаг — не новая инфраструктура, а дополнительная дисциплина single-writer/read-retry вокруг DuckDB admin/auth paths.

[2026-06-05] — Hermes Web MVP: устранён backend race в чатах и стабилизирован chat bootstrap

Context:
- В чатах периодически появлялся banner `Часть данных не загрузилась: Сервис вернул не JSON (500)` при параллельной post-login загрузке `/bootstrap`, `/me`, `/threads`, `/jobs/meta` и `/files`.
- Живые и синтетические проверки показали, что корень не во frontend parsing, а в backend auth-path: обычные GET-запросы конфликтовали в DuckDB из-за записи `UPDATE sessions SET last_seen_at = ...` внутри `require_auth()`.
- Дополнительно пользователь попросил слегка затемнить фон зоны переписки, не меняя local-first контур и не добавляя новую инфраструктуру.

Agreed:
- `require_auth()` должен оставаться read-path без write-конфликтов на каждый auth-protected GET.
- Для tunnel/local-web контура признаком исправления считается не только отсутствие traceback в коде, но и чистый живой runtime на `http://127.0.0.1:8790` без banner-ошибки и с корректным `/api` proxy path.
- Визуальный polish области сообщений допустим как точечная frontend-правка внутри текущего `index.html`/`app.js` контура.

Implemented:
- Backend `services/backend/app.py`:
  - из `require_auth()` убран конфликтный `UPDATE sessions SET last_seen_at = ? WHERE token = ?`;
  - auth-path оставлен только на чтение токена и пользователя, без записи в hot-path каждого GET.
- Frontend `services/frontend/index.html`:
  - фон `.chat-conversation` и `.chat-conversation-scroll` затемнён до `#eef2f7`;
  - фон `.message.assistant` смягчён до `#f8fbff`.
- Runtime cleanup:
  - подтверждён один актуальный backend-процесс на `127.0.0.1:8788` и один frontend-процесс на `127.0.0.1:8790`;
  - старые завершившиеся backend sessions не используются как источник истины для приёмки.

Verified:
- `python3 -m py_compile /home/hermes/workspace/hermes-web-mvp/services/backend/app.py` → OK.
- `curl http://127.0.0.1:8788/api/service-info` → `200 OK`.
- Параллельная backend-проверка после фикса: 6 раундов одновременных запросов к `/bootstrap`, `/feedback/reasons`, `/me`, `/threads?include_archived=0`, `/jobs/meta`, `/files?limit=200` → все ответы `200`, без `500`.
- Live browser/runtime на `http://127.0.0.1:8790`:
  - статус `Готово к работе · hermes-api`;
  - banner ошибки пустой;
  - `window.__APP_CONFIG__` использует relative proxy config: `apiBaseUrl: '/api'`, `serviceInfoPath: '/api/service-info'`;
  - фон зоны чата подтверждён как `rgb(238, 242, 247)`;
  - фон assistant-сообщения подтверждён как `rgb(248, 251, 255)`.

Rejected:
- Оставлять `last_seen_at` update внутри `require_auth()` и гасить проблему только try/except вокруг DuckDB conflict.
- Считать HTML `500` в banner frontend-дефектом без проверки backend transaction-path.
- Перестраивать auth/session contour или добавлять новую инфраструктуру только ради снятия этого race.

Reflection:
- Этот дефект выглядел как frontend parse/runtime ошибка, но по сути был backend concurrency bug в read-heavy login bootstrap path.
- Для DuckDB/local-first контура особенно важно не смешивать частые auth-check GET и лишние write-операции в одном пути, иначе даже «безобидное» обновление last_seen начинает ломать пользовательский UI.

Open questions:
- Если `last_seen_at` всё же нужен продуктово, его лучше возвращать отдельным batched/background-механизмом, а не обновлять на каждом auth-protected GET.

[2026-06-06] — Hermes Web MVP: admin overview без session-centric KPI, фильтр/экспорт логов и усиление auth-контура

Context:
- Пользователь попросил довести admin-контур до уровня остальных разделов: сделать `Обзор` прикладным для backend/frontend-эксплуатации, добавить во вкладке логов фильтр по дате-времени и выгрузку по этому фильтру, затем проверить runtime и защитные инварианты.
- Важное ограничение сохранилось: не строить новую инфраструктуру и не уходить во внешний контур, а закрыть задачу внутри текущего local-first frontend/backend стека Hermes Web MVP.
- Отдельно был уточнён вопрос про пользовательское название задачи: нужно было понять, локальное ли оно для одного браузера или хранится как общее backend-поле.

Agreed:
- `Обзор` admin UI не должен быть session-centric: количество сессий убирается из ключевых KPI и из таблицы пользователей.
- Полезными считаются эксплуатационные сигналы backend/frontend-контура: `job_runs`, `job_errors`, `active_users_7d`, TTL сессии, downstream/model, scheduler/import/LDAP readiness, usage tokens.
- Вкладка `Операции` должна поддерживать фильтр `С/По` по date-time и выгрузку тех же отфильтрованных событий в `CSV` и `JSON`.
- Пользовательское название задачи является backend-данными: используется `display_name`, а не чисто локальный alias в браузере.
- Security-path усиливается без перестройки архитектуры: TTL сессий, отзыв старых сессий и self-service смена пароля остаются частью текущего backend-контура.

Implemented:
- Frontend `services/frontend/app.js`:
  - добавлены helpers для `datetime-local` ↔ ISO, query params и download path (`CSV`/`JSON` export);
  - `renderAdmin()` переведён на новые overview-метрики и графики `Запуски задач` / `Ошибки задач`;
  - из users table убран столбец `Сессии`;
  - добавлены `apply/reset/export` handlers для admin events;
  - подключён frontend flow смены пароля через `/api/me/change-password`.
- Frontend `services/frontend/index.html`:
  - задействованы controls для блока `Операции` (`С`, `По`, `Применить`, `Сбросить`, `Выгрузить CSV`, `Выгрузить JSON`);
  - в профиле используется блок `Безопасность` со сменой пароля.
- Backend `services/backend/app.py`:
  - включён TTL сессий через `SESSION_TTL_HOURS` / `SESSION_TTL` и проверка просрочки в `require_auth()`;
  - добавлен `revoke_user_sessions(...)` и отзыв старых сессий при admin reset/self password change;
  - добавлен endpoint `POST /api/me/change-password`;
  - `/api/admin/events` расширен фильтрами `date_from`, `date_to`, `limit` и экспортом `csv/json`;
  - admin health/overview переведены на прикладные сигналы `active_users_7d`, `failed_job_runs_7d`, `session_ttl_hours`, `job_errors`.

Verified:
- Синтаксис:
  - `node --check /home/hermes/workspace/hermes-web-mvp/services/frontend/app.js` → OK.
  - `python3 -m py_compile /home/hermes/workspace/hermes-web-mvp/services/backend/app.py` → OK.
- Backend smoke:
  - `python3 -m unittest /home/hermes/workspace/hermes-web-mvp/services/backend/test_smoke.py` → `Ran 7 tests ... OK`.
- Live browser/runtime на `http://127.0.0.1:8790`:
  - логин и открытие админки успешны, console JS errors не зафиксированы;
  - на вкладке `Обзор` подтверждены новые карточки без session KPI;
  - на вкладке `Пользователи` live подтверждено отсутствие столбца `Сессии`;
  - на вкладке `Операции` подтверждены поля `С` / `По`, кнопки apply/reset/export и runtime-статусы по выгрузке/пустому диапазону;
  - в профиле live подтверждён блок `Безопасность` с полями текущего и нового пароля и кнопкой `Сменить пароль`.
- Contract по имени задачи:
  - `display_name` проходит через backend как source of truth и не является локальным только для одного пользователя.

Rejected:
- Возвращать в admin overview показатели по количеству сессий как ключевую управленческую метрику.
- Делать экспорт логов через отдельный сервис или новый orchestration path вместо текущего frontend/backend контура.
- Считать пользовательское название задачи локальным browser-only полем без backend source of truth.
- Ослаблять auth-path до бессрочных сессий или оставлять смену пароля только через admin reset.

Reflection:
- Это уже не косметический cleanup, а выравнивание admin UI под реальную эксплуатацию: метрики смещены от session vanity к job/runtime health.
- Для local-first контура хорошим компромиссом оказалось не добавлять новые сервисы, а честно дотянуть текущие API и frontend-state до полноценного admin workflow.
- Вопрос про `display_name` важен не только UX-но и архитектурно: теперь это явно backend-сущность, на которую можно безопасно опираться в общем UI-контуре.

Open questions:
- Если позже понадобится deeper audit admin events, следующим логичным шагом будет не новый UI-слой, а уточнение состава экспортируемых колонок и retention-политики событий.

[2026-06-06] — Hermes Web MVP: React 8792 приёмочно близок к parity с legacy 8790, но порог UI 8.5 пока не пройден

Context:
- Пользователь выбрал сценарий 2: довести React-контур `http://127.0.0.1:8792` до корректной работы раньше дальнейшего развития.
- Критерии приёмки были зафиксированы явно: функциональность не хуже legacy `8790`, работающий backend, стабильная одновременная работа нескольких пользователей, UI не ниже оценки `8.5`, результат не должен быть стыдно отдавать на пилот.
- Ограничение сохранялось прежним: не менять архитектуру, не вводить новый внешний контур, а доводить React внутри текущего local-first backend/API слоя.

Agreed:
- React `8792` оценивается отдельно от legacy `8790`, но сравнительно с ним по четырём практическим зонам: `chat`, `profile`, `jobs`, `admin`.
- Приёмка считается честной только при live runtime-проверке, backend smoke и отдельной проверке multi-user сценария, а не по коду или предположениям.
- Если функциональная parity достигнута, но визуальная планка `UI >= 8.5` не набрана, это фиксируется как частичное прохождение: продуктово usable, но не финально pilot-ready по согласованному quality bar.

Implemented:
- Frontend React `services/frontend-react/src/App.jsx`:
  - исправлен chat send-flow через optimistic update: пользовательское сообщение показывается сразу, не ожидая полного backend round-trip и ответа Hermes;
  - сохранён текущий backend `/api` contour без смены API-contract.
- Acceptance/runtime tools:
  - обновлён `scripts/react_targeted_acceptance_v2.mjs`, чтобы backend persistence чата проверялась по реальным thread details, а не по preview-эвристике;
  - сняты live screenshots для `8790` и `8792` по экранам `chat`, `profile`, `jobs`, `admin` в `/home/hermes/workspace/hermes-web-mvp-react/tmp/compare_shots/`.
- Backend `services/backend/app.py`:
  - ужесточён import-update path для существующих пользователей: update теперь выполняется атомарно через `WHERE id = ? AND version = ? RETURNING id`;
  - при конфликте версии импорт не делает silent overwrite, а помечает запись как `skipped_version_conflict`.
- Backend tests `services/backend/test_smoke.py`:
  - добавлена регрессия на повторный import того же пользователя с проверкой `updated = 1`, `skipped = 0` и ростом `version` до `2`.

Verified:
- React targeted acceptance:
  - `HERMES_WEB_FRONTEND_URL=http://127.0.0.1:8792/ node scripts/react_targeted_acceptance_v2.mjs` → все целевые проверки зелёные:
    - `chat.visible_in_ui = true`
    - `chat.persisted_in_backend = true`
    - `chat.file_visible_in_ui = true`
    - `profile.title_visible = true`
    - `profile.file_present = true`
    - `jobs_create.visible_in_ui = true`
    - `jobs_create.visible_in_backend = true`
    - `jobs_update.alias_saved = true`
    - `jobs_update.paused = true`
    - `jobs_update.resumed = true`
    - `admin_users.visible_in_ui = true`
    - `admin_users.visible_in_backend = true`
    - `admin_users.detail_ok = true`
    - `admin_users.history_ok = true`
    - `admin_operations.controls_visible = true`
    - `admin_references.datasets_visible = true`.
- Backend validation:
  - `python3 -m py_compile /home/hermes/workspace/hermes-web-mvp-react/services/backend/app.py` → OK.
  - `PYTHONPATH=services/backend python3 -m unittest services/backend/test_smoke.py -v` → `Ran 7 tests ... OK`.
- Live multi-user scenario:
  - админ создал shared job;
  - второй пользователь увидел задачу в своём `/api/jobs`;
  - self-subscribe прошёл на `200`;
  - у второго пользователя появился job-thread;
  - owner run завершился с `200` без поломки контура.
- Live compare `8790` vs `8792`:
  - по runtime-тексту и экранам React закрывает основные зоны `chat/profile/jobs/admin`;
  - screenshots сохранены как артефакт сравнения.
- Visual review of React screenshots:
  - chat screen: ориентир около `7.2/10`;
  - jobs screen: ориентир около `7.9/10`;
  - admin screen: ориентир около `7.5/10`;
  - честный совокупный вывод: React UI уже аккуратный и пригодный для internal/pilot trial, но до согласованного порога `8.5+` пока не дотягивает.

Decision:
- По функциональности и backend/multi-user устойчивости React `8792` сейчас приёмочно близок к parity с legacy `8790` и может использоваться как рабочий параллельный контур.
- По визуальному quality bar решение отрицательное: критерий `UI >= 8.5` пока не выполнен.
- Следовательно, формулировка `pilot-ready` в полном согласованном смысле пока преждевременна.
- Корректный статус на сейчас: `functional pilot candidate / parallel runtime ready`, но не `final polished pilot UI`.

Rejected:
- Объявлять React полностью готовым к пилоту только потому, что backend и основные user-flows уже работают.
- Подтягивать оценку UI до `8.5+` декларативно, когда live visual review стабильно даёт уровень порядка `7.2–7.9`.
- Возвращаться к архитектурной миграции или внешним сервисам вместо адресного UI-polish внутри текущего React-контура.

Reflection:
- Основной технический риск шага 2 уже не в API и не в shared runtime, а в product-polish самого React surface.
- Это хорошая промежуточная точка: самый дорогой риск — неработающий multi-user/workflow contour — уже заметно снижен, а оставшийся разрыв до желаемого качества в основном UX/UI-характера.
- Для следующего шага нужен не новый стек, а focused UI-polish pass по sidebar density, visual hierarchy, typography/contrast и общему ощущению product maturity.

Open questions:
- Можно ли без отхода от local-first UX аккуратно встроить `CopilotKit` как дополнительный chat-driven слой поверх уже согласованного русского интерфейса и существующего backend/API-контура?
- Где должна проходить граница между обычным Hermes chat UX и action-driven CopilotKit flow, чтобы не получить дублирующиеся сценарии.

[2026-06-06] — Hermes Web React 8793: CopilotKit proxy и Telegram dashboard-контур доведены до живого runtime

Context:
- Пользователь попросил доделать интеграцию с CopilotKit и проверить backend и frontend, отдельно уточнив, что не нужно снова возвращаться к вопросу пользовательского naming.
- Ограничение осталось прежним: не строить новый внешний контур, а довести интеграцию внутри текущего local-first стека `frontend 8793 -> backend 8791 -> local runtime 8794`.
- Важной частью задачи была не только сборка, но и живая runtime-проверка сценария с Telegram dashboard в чате.

Agreed:
- Не уводить frontend на прямой внешний endpoint, если проблему можно закрыть через существующий backend-контур.
- Считать задачу закрытой только после реальной проверки backend route, frontend runtime и пользовательского chat-сценария.
- Naming не пересматривать без новых данных; фокус держать на runtime-интеграции.

Implemented:
- `services/backend/app.py`:
  - добавлен `COPILOTKIT_RUNTIME_BASE_URL`;
  - добавлен proxy helper для passthrough-запросов в локальный CopilotKit runtime;
  - добавлены backend routes `/api/copilotkit` и `/api/copilotkit/<path>`.
- Интеграционный разрыв устранён: frontend по-прежнему использует `VITE_COPILOTKIT_RUNTIME_URL=/api/copilotkit`, а backend теперь реально проксирует этот контур на `http://127.0.0.1:8794`.
- Для live browser acceptance локально подтянут минимальный набор shared libs для Playwright Chromium в user-space под `/home/hermes/workspace/.local-libs`, без системной перестройки и без ухода в новый стек.

Verified:
- Backend smoke:
  - `python3 -m unittest services/backend/test_smoke.py` → `Ran 7 tests ... OK`.
- Живые backend endpoint'ы:
  - `GET http://127.0.0.1:8791/api/health` → `200`;
  - `GET http://127.0.0.1:8791/api/copilotkit/info` → `200`;
  - отдельный runtime `http://127.0.0.1:8794/copilotkit/info` отвечает корректно.
- Frontend runtime:
  - Vite dev-server `http://127.0.0.1:8793/` жив;
  - `npm run react:build` проходит успешно.
- Live user scenario в headless browser:
  - через реальный `textarea` на `8793` отправлен запрос `Построй аналитику Telegram-дайджеста...`;
  - frontend сделал `POST /api/threads/27/messages` и получил `201`;
  - в DOM реально появился dashboard-контур: `dashboardSections = 8`, `messageBubbles = 4`;
  - в page text подтверждены assistant answer и блок `Аналитика Telegram-дайджеста` с карточками/секциями.
- Backend chat route после proxy-фикса не деградировал:
  - assistant metadata по-прежнему содержит `downstream = telegram-digest-dashboard` и `dashboard_kind = telegram_digest_analytics`.

Decision:
- Для текущего local-first контура правильная схема интеграции — не direct frontend-to-runtime, а `frontend -> backend proxy -> local CopilotKit runtime`.
- CopilotKit-интеграцию на `8793/8791/8794` можно считать рабочей для текущего Telegram dashboard-сценария.
- К naming и альтернативным архитектурным обходам возвращаться не нужно, пока не появятся новые требования или новые runtime-данные.

Rejected:
- Перенастраивать frontend на прямой доступ к `8794`, обходя основной backend-контур.
- Тащить внешний SaaS/runtime вместо доведения локальной интеграции в текущем стеке.
- Считать задачу закрытой только по сборке или unit-smoke без реального chat/browser runtime.

Reflection:
- Корневая проблема оказалась не в dashboard-логике и не во frontend naming, а в недоведённой связке маршрутизации: frontend уже смотрел в `/api/copilotkit`, а backend этот маршрут ещё не публиковал.
- После закрытия proxy-разрыва и browser acceptance основной риск сместился из архитектурной зоны в обычную продуктовую эволюцию UI.

Open questions:
- Если CopilotKit будет расширяться дальше, следующим отдельным шагом стоит решить не routing, а продуктовую границу между обычным Hermes chat и action-driven сценариями CopilotKit.

[2026-06-06] — Hermes Web React 8792: быстрый parity-pass по chat/profile/admin/jobs перед переключением на следующий эксперимент

Context:
- После предыдущего цикла React уже был функционально близок к `8790`, но пользователь попросил не останавливаться на промежуточном выводе и быстро добить то, что ещё мешало честно считать контур рабочим для повседневного использования.
- Приоритетом был не полный redesign, а максимально быстрый high-ROI pass по самым заметным просадкам перед переходом к следующей теме, включая потенциальную проверку CopilotKit.
- Ограничение оставалось прежним: ничего не перестраивать архитектурно, а улучшать существующий local-first React runtime `8792` поверх текущего backend/API.

Agreed:
- Закрывать только самые дорогие остатки parity: `chat`, `profile`, `admin users`, `jobs detail`.
- Считать результат по фактическому runtime на `8792`, а не по одной только сборке или по старым acceptance-скриптам.
- Не объявлять идеальную UI-готовность, если визуально ещё остаются зоны для отдельного polish-sprint.

Implemented:
- Frontend React `services/frontend-react/src/App.jsx`:
  - убран основной технический migration-copy из login/sidebar/chat surface;
  - добавлены `Все чаты`, welcome/warning flow и modal полного списка чатов;
  - возвращена секционная модель профиля: `Сводка`, `Личные данные`, `Как отвечать`, `Файлы`;
  - усилен `JobsScreen`: summary/detail-контур, карточка управления задачей, более читаемые блоки `Приватность и доставка` и `История запусков`;
  - усилен `AdminUsersSection`: summary-карточки `Всего / Активны / Выбрано`, табличная шапка `Пользователь / Статус / Нагрузка / Действие`, более управленческий row-contour.
- Frontend React `services/frontend-react/src/styles.css`:
  - добавлены lightweight table-like стили для users/jobs detail, без ввода нового UI-фреймворка и без расширения архитектуры.

Verified:
- Сборка:
  - `npm run react:build` в `/home/hermes/workspace/hermes-web-mvp-react` → `vite build` завершился успешно.
- Live runtime `http://127.0.0.1:8792/`:
  - `chat`: sidebar без migration-copy, есть `Все чаты`, warning/banner и composer;
  - `profile`: подтверждены секции `Сводка / Личные данные / Как отвечать / Файлы`;
  - `admin -> users`: подтверждены summary-карточки, табличная шапка и обновлённый row-contour;
  - `jobs`: подтверждены список задач и detail-контур с блоками `Имя / Статус / Следующий запуск / Последний запуск / Источник / Роль`, действиями `Поставить на паузу / Запустить сейчас / Настроить задачу / Сохранить название`, секцией `Приватность и доставка` и блоком `История запусков`.
- Console:
  - в live-проходах по `admin` и `jobs` критических JS errors не зафиксировано.

Decision:
- Быстрый parity-pass считать успешным: React `8792` больше не выглядит как технически урезанный контур по ключевым зонам `chat/profile/admin/jobs`.
- По функциональному и UX-baseline этот runtime можно считать достаточно рабочим, чтобы не блокировать следующий эксперимент пользователя.
- При этом отдельный visual polish до планки `8.5+` по-прежнему остаётся отдельной темой и не считается автоматически закрытым этим быстрым pass.

Rejected:
- Останавливать пользователя от следующего этапа только потому, что React ещё не прошёл отдельный глубокий visual-polish sprint.
- Раздувать задачу до нового UI-redesign или новой архитектуры вместо адресных правок в текущем React-контуре.

Reflection:
- Самый высокий ROI дал не redesign, а возврат продуктовой структуры: секции профиля, нормальный users contour в админке и читаемый jobs detail.
- На этой стадии React уже достаточно собран, чтобы использовать его как рабочий контур и параллельно идти в следующий продуктовый эксперимент.

Open questions:
- Если React станет основным интерфейсом, следующим отдельным циклом всё ещё нужен focused polish-pass именно на визуальную зрелость и ощущение `8.5+`.

[2026-06-06] — Hermes Web React 8792: chat/profile contour доведён до приёмочного уровня, порог UI 8.5 условно достигнут для этого контура

Context:
- Пользователь попросил не просто проверить React `8792`, а добить фактические хвосты в `chat/profile` и честно довести экранный контур до уровня, после которого можно переходить к другим разделам.
- Критичными были именно runtime-проблемы: открытие файлов, welcome/onboarding, использование runtime-справочников в `Как отвечать`, архив/список чатов, полировка spacing и copy.
- Ограничение сохранилось прежним: без новой архитектуры и без внешних сервисов, только адресные правки внутри текущего local-first React+backend контура.

Agreed:
- Приёмка считается по живому `http://127.0.0.1:8792`, а не по коду на диске.
- Runtime-справочники должны реально использоваться в `Профиль -> Как отвечать` и в onboarding, а не только приходить из `/api/bootstrap`.
- Мелкие UX-хвосты допустимо считать отдельным финализационным шагом; они не должны заново откатывать уже подтверждённую продуктовую функциональность.

Implemented:
- Frontend React `services/frontend-react/src/App.jsx`:
  - исправлен `openFile` flow: убран двойной `/api/api/...` при открытии файлов;
  - исправлен copy раздела чатов: `Рабочий раздел для диалога, файлов и обсуждения.`;
  - добавлен рабочий first-run onboarding modal `Давай настроим, как с тобой взаимодействовать`;
  - `Профиль -> Как отвечать` переведён с plain inputs на runtime-справочники `assistant_tones`, `assistant_answer_depths`, `assistant_interaction_modes`;
  - onboarding modal теперь показывает те же runtime-значения по умолчанию;
  - улучшены sidebar/chat/profile micro-UX: warning separator, compact spacing, disabled/hover states, статусы архивного чата, русская подпись `Ключевые рамки и приоритеты` вместо `Pinned`.
- Frontend React `services/frontend-react/src/styles.css`:
  - уплотнены отступы и кнопочные группы;
  - добавлены стили для `sidebar-actions`, `thread-state-chip`, compact warning/cards и связанных chat/profile элементов.

Verified:
- Сборка:
  - `npm run react:build` в `/home/hermes/workspace/hermes-web-mvp-react` → успешно после финального polish-пакета.
- Live runtime `http://127.0.0.1:8792`:
  - `smoke-note.txt` и route `/api/files/59/download` открываются корректно, без `404`;
  - в `chat` подтверждены сценарии: `+ Новый чат`, welcome-card, starter prompt, отправка по `Enter`, pending-state, финальный ответ Hermes, `В архив` / `Вернуть из архива`, modal `Все чаты`, `Скрыть`;
  - в `profile -> Как отвечать` live подтверждены combobox/select на основе runtime-справочников;
  - onboarding нового пустого пользователя открывается автоматически и ведёт в `Профиль`;
  - status `В архиве` подтверждён в header и списках чатов;
  - console JS errors в финальном runtime-pass не зафиксированы.

Decision:
- Для `chat/profile` контура React `8792` можно считать доведённым до приёмочного product-level baseline.
- Для этого контура порог `UI ~8.5/10` считать условно достигнутым: не как идеальную визуальную витрину, а как честный рабочий уровень без грубых UX-дыр и без стыдных runtime-изъянов.
- Можно переходить к следующим разделам без возврата к этим же проблемам по второму кругу, если не появятся новые данные.

Rejected:
- Считать runtime-справочники "подключёнными", если они только приходят из backend, но не используются в форме.
- Оставлять onboarding нового пользователя скрытым баннером вместо отдельного первого шага настройки.
- Возвращаться к архитектурным перестройкам или новому стеку ради задач, закрываемых точечным React/backend polish внутри текущего контура.

Reflection:
- Самые дорогие риски в этом цикле были уже не архитектурные, а продуктовые: мелкие `404`, onboarding-gap, разъезжающийся copy и несвязанные runtime references.
- Когда эти хвосты закрыты live, React перестаёт выглядеть как "почти рабочий" и начинает вести себя как нормальный продуктовый контур.

Open questions:
- Следующий цикл уже логично вести не по `chat/profile`, а по оставшимся разделам (`jobs/admin` или следующему product surface), пока этот контур не трогать без новой причины.

[2026-06-06] — Hermes Web React `Задачи...[truncated]
[2026-06-06] — Hermes Web React 8792: профиль очищен от лишнего шума и приведён к product-level baseline

Context:
- После приёмки chat/profile пользователь отдельно попросил довести именно экран `Профиль` до уровня `8.5/10`: убрать ненужную информацию, упростить `Как отвечать` и сделать вкладку `Файлы` про весь профильный набор файлов, а не про chat-контекст.
- Ключевой запрос был не про новые функции, а про смысловую чистоту: меньше технички, понятнее подписи, деловой layout без спорных блоков.

Agreed:
- `Профиль` не должен показывать показатели, которые относятся к chat-контексту, а не к самому профилю.
- Во вкладке `Файлы` нужен единый список всех файлов пользователя; фильтр `текущий чат` признан лишним и удалён.
- Формулировки вокруг `text_extracted` должны быть человеческими: `Распознано`, `С распознанным текстом`, `Без распознанного текста`.

Implemented:
- В `services/frontend-react/src/App.jsx`:
  - из `Сводки` убраны шумные показатели (`Файлов в чате`, `Версия профиля`), оставлены только профильные сигналы;
  - убран избыточный блок `Предпросмотр стиля` в `Как отвечать`, вместо него оставлен короткий поясняющий контекстный блок;
  - вкладка `Файлы` перестроена под деловой row-layout: имя/метаданные/summary слева, действие `Открыть` справа;
  - убран фильтр `Область / Текущий чат`; профильные файлы теперь фильтруются только по `Поиск` и `Тип`;
  - переименованы подписи `С текстом` -> `Распознано`, `С извлечённым текстом` -> `С распознанным текстом`, `Без извлечённого текста` -> `Без распознанного текста`.
- В `services/frontend-react/src/styles.css`:
  - добавлены layout-стили под более широкий и спокойный список файлов.

Verified:
- `npm run react:build` в `/home/hermes/workspace/hermes-web-mvp-react` -> успешно после финальных правок профиля.
- Live runtime `http://127.0.0.1:8792` подтвердил:
  - в `Сводке` больше нет показателя `Файлов в чате`;
  - в `Как отвечать` больше нет блока `Предпросмотр стиля`;
  - во вкладке `Файлы` остались только фильтры `Поиск` и `Тип`;
  - live-строка файла подтверждена: имя, размер, MIME, дата, summary и отдельная кнопка `Открыть` справа.

Decision:
- Профильный экран React `8792` считать очищенным от лишней технички и доведённым до рабочего product-level baseline.
- Для профиля порог `UI ~8.5/10` считать практически достигнутым: не как витринный redesign, а как чистый и понятный рабочий экран.

Rejected:
- Оставлять во вкладке `Файлы` chat-зависимый фильтр `Текущий чат`.
- Держать в `Как отвечать` декоративный `Предпросмотр стиля`, который дублирует уже заданные настройки.
- Сохранять расплывчатые формулировки вроде `С текстом`, не объясняющие, что текст был именно извлечён/распознан Hermes.

Open questions:
- Следующий продуктовый цикл уже логично переносить на `Задачи`; к профилю возвращаться только при появлении новых конкретных UX-gap.

[2026-06-06] — Hermes Web React 8793: CopilotKit canonical contour и аудит поднятых версий

Context:
- Нужно было довести интеграцию CopilotKit в контуре `hermes-web-mvp-react-8793` не как preview-демо, а как архитектурно правильный runtime path с понятным каноническим маршрутом.
- Дополнительно требовалось разобраться, зачем поднята версия на порте `8824`, и убрать дублирующие контуры, которые мешают диагностике и создают lock-конфликты на одном DuckDB.

Agreed:
- Канонический путь CopilotKit для React `8793`: `frontend 8793 -> /api/copilotkit -> backend 8791 -> runtime 8794`.
- Frontend больше не должен ходить в runtime sidecar напрямую через отдельный Vite proxy `/copilotkit`; единая точка входа теперь backend API.
- Backend route `/api/copilotkit` больше не считать preview-заглушкой: он должен работать как реальный proxy в runtime contour.
- Порт `8824` не считать отдельной целевой версией продукта: это был лишний Vite dev server того же проекта.

Implemented:
- В `services/backend/app.py`:
  - preview-only route `/api/copilotkit` заменён на runtime proxy в `http://127.0.0.1:8794/copilotkit`;
  - добавлены настройки `HERMES_WEB_COPILOTKIT_RUNTIME_BASE_URL` и `HERMES_WEB_COPILOTKIT_RUNTIME_TIMEOUT`;
  - поддержан passthrough для обычных JSON-ответов и `text/event-stream`.
- В `services/frontend-react/src/App.jsx`:
  - `VITE_COPILOTKIT_RUNTIME_URL` по умолчанию переведён на `/api/copilotkit`.
- В `vite.config.js`:
  - удалён отдельный dev proxy `/copilotkit -> 8794`; оставлен единый контур через `/api`.
- В `run_frontend_react_service.sh`:
  - удалён frontend-side runtime base;
  - runtime URL по умолчанию переведён на `/api/copilotkit`.
- В `run_backend_service.sh`:
  - default backend port приведён к `8791`;
  - добавлен runtime base URL для proxy;
  - CORS заужен до `8793`/`localhost:8793` после снятия лишнего `8824`.
- В `services/backend/test_smoke.py`:
  - добавлен smoke-тест `test_copilotkit_proxy_info_passthrough`.
- Лишние backend-инстансы на `8796`, `8798`, `8800`, держащие тот же DuckDB-файл и вызывавшие lock-конфликты, остановлены.

Verified:
- `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` -> успешно.
- `PYTHONPATH=services/backend python3 -m unittest services/backend/test_smoke.py -v` -> `Ran 8 tests ... OK`.
- `npm run react:build` -> успешно.
- HTTP-проверка через backend proxy:
  - `GET http://127.0.0.1:8791/api/copilotkit/info` -> `200 OK`;
  - `POST http://127.0.0.1:8791/api/copilotkit {"method":"info"}` -> `200 OK`.
- Runtime/process state после cleanup:
  - `8791` слушает backend;
  - `8793` слушает frontend;
  - `8794` слушает CopilotKit runtime;
  - `8824`, `8796`, `8798`, `8800` больше не подняты.

Decision:
- Для React-контура `8793` считать CopilotKit integration-path архитектурно исправленным: runtime подключён не напрямую к frontend, а через backend API contour.
- Версию на `8824` считать не отдельным deployment-контуром, а диагностическим/лишним dev-инстансом, к которому не нужно возвращаться без новой причины.
- Повторно не поднимать параллельные backend-инстансы одного и того же проекта на разных портах поверх общего DuckDB без явного отдельного data-dir/db-path.

Rejected:
- Держать одновременно два канонических пути (`/copilotkit` напрямую во frontend и `/api/copilotkit` через backend).
- Оставлять `/api/copilotkit` в статусе `preview_only` при уже существующем рабочем runtime на `8794`.
- Считать `8824` отдельной версией продукта без отдельного backend/data contour.

Reflection:
- Главный риск здесь был не в CopilotKit как библиотеке, а в размытой topology: несколько frontend/backend инстансов поверх одного storage делали картину ложной и порождали concurrency-ошибки DuckDB.
- После схлопывания контура до `8791/8793/8794` диагностика и дальнейшая runtime-проверка становятся прямыми и воспроизводимыми.

Open questions:
- Если понадобится полноценный multi-version runtime рядом с `8793`, для него нужен отдельный backend port и отдельный DuckDB path, а не только новый frontend port.

[2026-06-06] — Hermes Web React 8793: runbook контура, browser runtime и исправление open-link/file flows

Context:
- Пользователь попросил не просто локально подлечить CopilotKit, а собрать корректный алгоритм запуска/перезапуска всех компонентов, проверить техническое и архитектурное состояние контура `8793/8791/8794`, оценить ключевые вопросы безопасности и убедиться, что ссылки на открытие/привязку работают.
- Дополнительно нужно было прекратить повторный возврат к ручному разбору `libnspr4` и зафиксировать постоянный локальный browser/runtime путь внутри текущего local-first стека.

Agreed:
- Канонический contour для этой ветки: `frontend 8793 -> backend 8791 -> CopilotKit runtime 8794`.
- Для browser/playwright/Hermes browser acceptance канонической точкой входа считать `scripts/browser_runtime_env.sh`, а не временные директории в `workspace/.local-libs`.
- Контракт file/open-link должен быть двухслойным и рабочим в обоих вариантах:
  - список пользовательских файлов через `/api/files` с `download_url`;
  - ссылки вложений из сообщений через `/api/messages/<id>/attachments/<n>`.
- Для этого контура default frontend proxy не должен по умолчанию указывать на legacy backend `8788`.

Implemented:
- Backend `services/backend/app.py`:
  - в сериализацию `user_files` добавлен `download_url: /api/files/<id>/download`;
  - добавлен route `GET /api/files/<int:file_id>/download` с проверкой владельца, нормализацией пути внутри `DATA_DIR` и `send_file(..., as_attachment=True)`;
  - исправлен route `GET /api/messages/<int:message_id>/attachments/<int:attachment_index>`: добавлен fallback с `relative_path`, если в attachment нет `local_path`.
- Backend `services/backend/test_smoke.py`:
  - добавлена проверка `download_url` и живого скачивания файла через `/api/files/<id>/download`.
- Frontend/runtime config:
  - `vite.config.js` по умолчанию переведён с `8788` на `8791` для `/api` proxy;
  - зафиксирован runbook запуска/перезапуска в `hermes-web-mvp-react-8793/RUNTIME-RUNBOOK.md`.
- Browser runtime:
  - подтверждён рабочий user-space runtime через `~/.local/browser-runtime/root` и `~/.hermes/browser-libs/root`;
  - `workspace/.local-libs` оставлен только как legacy/временный след, не как source of truth.

Verified:
- Live ports / processes:
  - `8788` — legacy backend из соседнего дерева `hermes-web-mvp-react`;
  - `8791` — текущий backend из `hermes-web-mvp-react-8793/services/backend`;
  - `8793` — текущий frontend из `hermes-web-mvp-react-8793`;
  - `8794` — текущий CopilotKit runtime sidecar.
- Live health/runtime:
  - `GET http://127.0.0.1:8791/api/health` -> `200`;
  - `GET http://127.0.0.1:8791/api/service-info` -> `200`;
  - `GET http://127.0.0.1:8791/api/copilotkit/info` -> `200`;
  - `GET http://127.0.0.1:8794/copilotkit/info` -> `200`.
- Live security headers / auth basics:
  - preflight `OPTIONS` на backend даёт `204`;
  - CORS allow-origin заужен до `http://127.0.0.1:8793`;
  - unauthenticated `GET /api/files` и `GET /api/me` возвращают `401`;
  - backend отвечает `X-Frame-Options: DENY` и `Referrer-Policy: same-origin`.
- Open-link / export flows:
  - `GET /api/files` возвращает `download_url`;
  - live `GET /api/files/28/download` с авторизацией -> `200`, attachment filename корректен;
  - live `GET /api/messages/106/attachments/0` с авторизацией -> `200` после fallback-фикса;
  - `GET /api/admin/events?export=json` и `?export=csv` -> `200`.
- Backend smoke:
  - `python3 -m unittest services/backend/test_smoke.py` -> `Ran 7 tests ... OK`.

Tech / architecture findings:
- Контур `8793/8791/8794` сейчас живой и связный.
- Главный архитектурный хвост — рядом остаётся legacy backend `8788` из соседнего дерева; он не ломает текущий contour, но создаёт высокий риск путаницы, если запускать frontend не через канонический launcher.
- В `services/backend/data` лежат не только активная `hermes_web_app.duckdb`, но и legacy/backup файлы:
  - `hermes_web_app_8800.duckdb`
  - `hermes_web_app.duckdb.bak_before_hard_cleanup_non_admin`
  - `hermes_web_app.duckdb.bak_pre_non_admin_cleanup`
  - `hermes_web_mvp.sqlite3`
  Их нужно считать неканоническими следами и позже либо архивировать отдельно, либо явно маркировать.
- Browser runtime стабилизирован, но дисциплина запуска должна идти только через wrapper-скрипт, иначе команда легко снова уйдёт в ручной разбор библиотек.

Security findings:
- Хорошо:
  - bearer-auth обязателен для `me/files` и download routes;
  - session TTL/revocation уже присутствуют;
  - file routes проверяют владельца и не позволяют выходить за пределы `DATA_DIR`.
- Хвосты:

[2026-06-06] — Restart-safe контур для Hermes Web / CopilotKit / TG-API

Context:
- Нужно было не просто проверить живой runtime, а довести его до состояния, в котором `frontend + backend + copilot + TG-API + Hermes` переживают рестарт сервера и не зависят от случайно оставленных shell-процессов.

Agreed:
- Канонический runtime-contour остаётся `8793/8791/8794` плюс `TG-API` на `127.0.0.1:8001`.
- Operational defaults не должны вести на legacy `8788/8790/8792`.
- Restart-safe эксплуатация должна идти через `systemd --user`, а не через висящие вручную процессы.
- Telegram API credentials не должны оставаться hardcoded в repo-коде.

Implemented:
- Web/runtime:
  - исправлены operational defaults с legacy `8788/8790` на `8791/8793` в backend/frontend launcher'ах и части smoke/debug scripts;
  - обновлены operational docs (`README.md`, `docker-compose.yml`, `docs/DEPLOYMENT_GUIDE.md`, `docs/FRONTEND_GUIDE.md`, `docs/Hermes-Web-MVP-package.md`, `docs/TESTING_SCENARIO.md`);
  - добавлены user-systemd units:
    - `hermes-web-copilotkit-8794.service`
    - `hermes-web-backend-8791.service`
    - `hermes-web-frontend-8793.service`
- CopilotKit / frontend launchers:
  - добавлен явный `PATH=$HOME/.hermes/node/bin:$PATH`, чтобы `node` и `npm` поднимались из systemd-контекста после рестарта сервера.
- TG-API:
  - `app.py` по умолчанию bind'ится на `127.0.0.1`, а не `0.0.0.0`;
  - из `login.py` убран hardcoded fallback `TG_API_ID/TG_API_HASH`;
  - создан приватный env-файл `~/.hermes/tg-api.env`;
  - добавлены `TG-API/requirements.txt` и restart-safe launcher `run_tg_api_service.sh` с собственным `.venv` и автоустановкой зависимостей;
  - `ensure_api.py` переведён на тот же env-source и launcher;
  - добавлен unit `tg-api.service`.

Verified:
- `systemctl --user` services enabled:
  - `hermes-gateway.service`
  - `hermes-web-copilotkit-8794.service`
  - `hermes-web-backend-8791.service`
  - `hermes-web-frontend-8793.service`
  - `tg-api.service`
- После restart через `systemctl --user restart ...` живо подтверждено:
  - `GET http://127.0.0.1:8791/api/health` -> `200`
  - `GET http://127.0.0.1:8791/api/copilotkit/info` -> `200`
  - `GET http://127.0.0.1:8794/health` -> `200`
  - `GET http://127.0.0.1:8793/` -> `200`
  - `GET http://127.0.0.1:8001/export?profile=profile_1&config=daily&since={}` -> `200`
- `TG-API` после service-старта снова отдаёт export (`count=359`).

Decision:
- Для этого контура canonical operations path — через user-systemd units и loopback-only bind'ы, а не через ручные процессы и внешние bind'ы.
- При будущих обновлениях Hermes не опираться на текущую shell-сессию для поднятия web/TG сервисов.

- Хвосты:

[2026-06-06] — Cleanup legacy data и канонизация Telegram session contour

Context:
- После стабилизации web-контура нужно было убрать legacy data-файлы и выровнять Telegram session storage так, чтобы остался один канонический session path без дублей в корне и зеркальных каталогах.

Agreed:
- В `hermes-web-mvp-react-8793/services/backend/data` каноническими считаются только:
  - `hermes_web_app.duckdb`
  - `uploads/`
- Legacy DB/backup-файлы не удаляются безвозвратно, а выносятся в локальный архив внутри того же проекта.
- Для `TG-API` канонический Telegram session path: `TG-API/session/profile_1.session`.
- Корневые `.session` файлы и дубли из зеркального `workspace/TG-API` считаются legacy и должны архивироваться автоматически.

Implemented:
- Backend data cleanup:
  - создан архив `services/backend/data/archive_legacy_2026-06-06`;
  - туда перенесены:
    - `hermes_web_app_8800.duckdb`
    - `hermes_web_app.duckdb.bak_before_hard_cleanup_non_admin`
    - `hermes_web_app.duckdb.bak_pre_non_admin_cleanup`
    - `hermes_web_mvp.sqlite3`
- `TG-API/app.py`:
  - добавлены `resolve_session_path(...)` и `cleanup_legacy_session_files(...)`;
  - export теперь опирается на канонический session contour и при старте архивирует legacy `.session` файлы.
- `TG-API/login.py`:
  - добавлен такой же cleanup legacy session-файлов перед интерактивным login.
- Telegram session cleanup выполнен физически:
  - в `TG-API/session/_archive_legacy/` перенесены legacy-копии `profile_1.session` из корня и из зеркального дерева `workspace/TG-API`.

Verified:
- В `services/backend/data` после cleanup остались только:
  - `hermes_web_app.duckdb`
  - `uploads/`
  - `archive_legacy_2026-06-06/`
- `TG-API` после cleanup использует канонический session-файл `session/profile_1.session`.
- `TG-API` server поднят на `127.0.0.1:8001`.
- Live проверка `GET /export?profile=profile_1&config=daily&since={}` -> `200`, `count=359`.

Decision:
- Для Telegram monitoring не плодить несколько `.session` контуров: один профиль — один канонический session file в `TG-API/session/`.
- Все future-cleanup по Telegram session storage делать через архивирование legacy-файлов, а не через silent overwrite или удаление.
  - нет подтверждения `Content-Security-Policy` на ответах backend;
  - в process env виден runtime API key, значит надо считать `.env` и process visibility чувствительной зоной;
  - legacy backend `8788` расширяет operational risk, потому что может стать случайным proxy target без явного намерения.

Rejected:
- Возвращаться к ручному временному раскладыванию browser-libs в `workspace/.local-libs` как к основному решению.
- Держать default proxy на `8788`, а run-script отдельно на `8791`.
- Считать file/open-link flow завершённым только по `/api/files`, не проверив links из message attachments.

Open questions:
- Отдельным cleanup-pass стоит решить судьбу legacy backend `8788` и неканонических DB/backup файлов в `services/backend/data`.
- Если нужен строгий security-pass уровня production-hardening, следующим шагом нужно отдельно добавить/проверить `Content-Security-Policy`, политику secrets/env и retention для runtime/process логов.

[2026-06-07] — Hermes Web React: request-level dashboard policy, source trust admin и сохранение дашборда в jobs/cron

Context:
- Пользователь уточнил, что дашборды должны строиться не по абстрактному global registry alone, а под конкретный запрос с выбором контура обработки данных.
- Дополнительно админ должен управлять доверенностью источников и processing policy, а удачный дашборд должно быть можно сохранить для последующего обновления через задачи или Hermes cron.
- Важное ограничение: остаться внутри текущего local-first стека `hermes-web-mvp-react`, не строить новую отдельную систему планировщика и не дублировать runtime-пайплайны.

Agreed:
- Request-level execution policy идёт через уже существующий message POST flow как `request_execution_policy`, без отдельного reply/policy endpoint.
- Источник истины по source trust и processing policy — backend `source_registry` + `processing_policy`; frontend не хардкодит свои словари режимов сверх runtime-полей.
- Для UX сценария “понравившийся дашборд” нужно переиспользовать уже существующий jobs/cron контур: из chat message с `dashboard_artifact` открывается prefilled job draft, а не создаётся новая сущность dashboard subscription.
- Hermes cron остаётся admin-контуром через `source_of_truth = hermes_cron`; встроенные local jobs продолжают быть дефолтом для обычного сценария.

Implemented:
- Frontend `services/frontend-react/src/App.jsx`:
  - в composer добавлен request-level policy UI: выбор режима обработки, `force_refresh`, `save_results_locally`, выбор разрешённых источников;
  - `MessageBubble` теперь показывает `request_execution_policy` и `dashboard_artifact`, а для assistant dashboard message — кнопку `Сохранить как задачу`;
  - добавлен prefilled flow `buildDashboardJobDraft(...)` для сохранения удачного дашборда в recurring job;
  - job modal расширен выбором execution contour (`local_jobs` / `hermes_cron`) и доставкой результата для cron;
  - send-flow отправляет `request_execution_policy` и в JSON, и в multipart.
- Frontend `services/frontend-react/src/styles.css`:
  - добавлены стили для policy strip, artifact box, policy card, source picker и admin source rows.
- Backend `services/backend/app.py`:
  - `POST /api/jobs` теперь умеет создавать Hermes cron job при `source_of_truth = hermes_cron`;
  - добавлены helpers для сборки cron schedule из job draft payload;
  - сохранён existing local jobs flow без отдельной новой инфраструктуры.
- Backend `services/backend/test_smoke.py`:
  - добавлены smoke-тесты на admin update data policy и на создание Hermes cron job через jobs API.

Verified:
- `npm run react:build` в `/home/hermes/workspace/hermes-web-mvp-react` → OK.
- `python3 -m py_compile services/backend/app.py services/backend/hermes_cron_bridge.py` → OK.
- `PYTHONPATH=/home/hermes/workspace/hermes-web-mvp-react/services/backend python3 -m unittest services/backend/test_smoke.py` → `Ran 9 tests ... OK`.
- Во время проверки уточнён фактический backend-словарь processing modes: `registered_only`, `registered_plus_external`, `external_allowed`. Предположение про `internal_preferred` отвергнуто как не соответствующее runtime-контракту.

Rejected:
- Делать отдельную сущность вроде `dashboard_subscription` вне текущего jobs/cron контура.
- Хардкодить frontend-режимы обработки вне backend runtime policy.
- Переходить на внешний scheduler/SaaS или строить новый orchestration layer для обновления дашбордов.

Reflection:
- Самая важная архитектурная точка здесь — не source registry сам по себе, а связка `request-level policy override + local runtime registry + reusable jobs/cron contour`.
- Сценарий recurring dashboard лучше работает как сохранение удачного запроса и его policy в существующий execution contour, чем как отдельный dashboard-продукт внутри MVP.

[2026-06-07] — Hermes Web React 8793: канонический runtime-контур и поведение dashboard source policy

Context:
- Нужно было прекратить путаницу между legacy/runtime-портами и одновременно проверить, как chat/dashboard реально ведёт себя при `local_only`, `local_first` и global fallback.
- Отдельный продуктовый риск: чат не должен зависать в режиме «у меня нет данных», если может либо сам уйти во внешний маршрут, либо хотя бы честно предложить пользователю следующий ход.

Agreed:
- Для текущего CopilotKit/React-контура канонический runtime: frontend `8793`, backend `8791`, sidecar `8794`, дерево `/home/hermes/workspace/hermes-web-mvp-react-8793`.
- Legacy backend `8788` и старый React `8792` не использовать как источник истины для этого контура без новых данных и явной цели.
- `local_first` должен вести себя не как глухой local-only режим: если запрос общий или явно внешний, backend сам уходит в global route; если локальный запрос не уточнён, чат должен предложить и локальное уточнение, и внешний обзор.
- `local_only` остаётся жёстким ограничением: внешний маршрут не используется, а ответ должен явно сигнализировать, что global path policy-запрещён.

Implemented:
- Backend `services/backend/app.py`:
  - подтверждён и оставлен request-level routing через `source_mode` + `allowed_source_ids` в существующем `POST /api/threads/<id>/messages`;
  - исправлен ранний выход в `maybe_build_dashboard_reply(...)`: `clarification_request` от local-router больше не считается достаточным завершением `local_first`-маршрута;
  - `build_dashboard_clarification_reply(...)` расширен: при разрешённом global fallback чат предлагает два хода — уточнить локальный источник или переключиться на внешний обзор;
  - конкретные `clarification_actions` и готовые prompts убраны: backend больше не подставляет за пользователя частные сценарии вроде LegalAI или Telegram-дайджеста;
  - в clarify явно зафиксировано, что пользователь не обязан заранее знать, есть ли локальные данные: система должна либо помочь уточнить источник, либо честно сказать, что локальных данных не хватает и нужен поиск по открытым источникам.
- Backend smoke `services/backend/test_smoke.py`:
  - обновлены проверки на новый `clarification_request` UX без `clarification_actions`;
  - добавлена проверка, что clarify прямо объясняет сценарий «пользователь не знает, есть ли локальные данные»;
  - сохранены проверки `global_only` и `local_only` routing.
- Документация:
  - `REACT_MIGRATION_STATUS.md` внутри канонического дерева переведён на актуальный контур `8793/8791/8794` вместо устаревших ссылок на `hermes-web-mvp-react` и `8792`;
  - в ключевых legacy-документах соседних деревьев добавлены явные баннеры, что они не являются текущим runtime-источником и должны переадресовывать в `hermes-web-mvp-react-8793`.

Verified:
- `python3 -m unittest services.backend.test_smoke -v` в `/home/hermes/workspace/hermes-web-mvp-react-8793` → `Ran 7 tests ... OK`.
- `npm run react:build` в `/home/hermes/workspace/hermes-web-mvp-react-8793` → сборка успешна.
- Live contour выровнен на каноническое дерево: frontend `8793` остаётся из `/home/hermes/workspace/hermes-web-mvp-react-8793`, stale backend на `8791` из `/home/hermes/workspace/hermes-web-mvp` остановлен и заменён запуском `./run_backend_service.sh` из канонического дерева.
- `curl http://127.0.0.1:8791/api/admin/dashboard-policy` без токена после выравнивания контура возвращает `401 auth_required`, а не `404`.
- Авторизованный backend-pass через `app.test_client()` подтвердил `GET /api/admin/dashboard-policy`, `PATCH` в `global_only` и обратный restore в `local_first`.
- В React admin добавлены API/UI-опоры без дублирующего CRUD: policy редактируется отдельной карточкой в admin overview, а состав/статус источников остаётся источником истины в existing references dataset `data_sources`.
- Изолированный backend probe на временной DuckDB подтвердил:
  - общий внешний запрос (`LegalAI`, `CRM`) при `local_first` возвращает `dashboard_result` через `web_research`;
  - локально-неуточнённый запрос возвращает `clarification_request` с вариантами `локально уточнить` / `сразу внешний обзор`;
  - `local_only` для внешнего запроса возвращает `clarification_request` с `policy_blocked_global = true` и без скрытого ухода во внешний маршрут.

Rejected:
- Автоматически превращать любой расплывчатый local-запрос в внешний обзор без сигнала от пользователя.
- Продолжать держать внутри канонического дерева документы, которые отправляют в промежуточный runtime `8792` как будто он остаётся базовым.

Open questions:
- Отдельным docs-cleanup проходом стоит дочистить не только каноническое дерево `hermes-web-mvp-react-8793`, но и соседние legacy-деревья `/home/hermes/workspace/hermes-web-mvp` и `/home/hermes/workspace/hermes-web-mvp-react`, где ещё остаются старые порты `8788/8790/8792` и прежние инструкции.

[2026-06-07] — Фронтэнд-задача временно закрыта, возврат к повседневной работе

Context:
- После серии frontend/runtime-доработок по Hermes Web пользователь попросил считать тему фронтэнда на текущем этапе завершённой.
- Приоритет смещён обратно в обычный рабочий режим без продолжения frontend-хвостов в фоне.

Agreed:
- Фронтэнд-задачу считать завершённой на текущий момент.
- Не продолжать её по инерции без нового явного запроса или новых данных.
- Возвращаться к обычной повседневной работе как к базовому режиму.

Rejected:
- Держать frontend-тему как молча активную незавершённую задачу.
- Продолжать крутить тот же трек без отдельного сигнала от пользователя.

Open questions:
- Если позже появится новый frontend-контекст или отдельный хвост, тема поднимается заново уже как новая явная задача.

[2026-06-10] — Hermes Web React 8793: adaptive dashboard grammar v1 вместо одного жёсткого шаблона

Context:
- По dashboard_result стало ясно, что «канонический дашборд» как один фиксированный шаблон будет слишком узким и начнёт ломаться на разных классах запросов.
- Цель сместили с одного hand-made layout на grammar-подход: стабильный envelope + библиотека типизированных sections + policy выбора по intent и форме данных.

Agreed:
- Для внешних dashboard-ответов базовой моделью становится не один template, а adaptive grammar v1.
- Стабильным должен оставаться внешний контракт (`kind`, `title`, `subtitle`, `summary_cards`, `sections`, `sources`, `notes`), а набор секций может меняться по смыслу задачи.
- Выбор секций должен идти от intent и data shape, а не от привычки всегда строить один и тот же dashboard.
- Если модель возвращает бедный или кривой payload, backend обязан нормализовать его и достраивать минимально полезный визуальный каркас, а не отдавать пустые секции во frontend.

Implemented:
- `services/backend/app.py`:
  - добавлены `EXTERNAL_DASHBOARD_GRAMMAR_VERSION = adaptive_v1` и policy-слой выбора по intent (`trend`, `segmentation`, `comparison`, `market_overview`, `evidence_board`);
  - prompt `build_global_dashboard_prompt(...)` переписан под grammar-подход: stable envelope, typed section grammar и selection policy вместо одного универсального шаблона;
  - добавлена backend-нормализация внешнего payload: unknown kinds приводятся к допустимым section types, summary/sources чистятся, а при бедном ответе достраиваются fallback sections и минимальная визуализация;
  - в `meta` добавлен явный маркер `dashboard_grammar`, а в `dashboard` — `grammar_version`, `intent`, `selection_policy`.
- `services/frontend-react/src/App.jsx`:
  - `DashboardArtifact` расширен новыми section types `timeline_list` и `matrix_list`.
- `services/frontend-react/src/styles.css`:
  - добавлены стили под timeline/matrix rendering.
- Создан user-local skill `adaptive-dashboard-grammar`, который фиксирует тот же подход на уровне Hermes skill-инструкции.
- `services/backend/test_smoke.py`:
  - добавлены проверки на `adaptive_v1`, `selection_policy` и минимальное число sections для external dashboard flows.

Verified:
- `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` → OK.
- `npm run react:build` → OK.
- `python3 -m unittest services/backend/test_smoke.py` → `Ran 7 tests ... OK`.

Rejected:
- Продолжать проектировать dashboard_result как один жёсткий hand-made template для всех аналитических задач.
- Полагаться только на prompt без backend-нормализации payload.
- Оставлять frontend зависимым от узкого списка section kinds, если backend уже начинает говорить более богатой grammar-моделью.

Open questions:
- Следующий логичный шаг — решать по реальным кейсам, нужны ли ещё richer section types вроде stacked comparison, geo view или richer evidence cards, но уже как расширение grammar, а не новый «канонический дашборд».

[2026-06-11] — TG-API: cron-контур в Hermes закреплён и подготовлен к полному копированию

Context:
- Пользователь попросил добить TG-API-контур и отдельно закрепить cron-функционал в новом Hermes без ручной пересборки по памяти.
- Нужно было не просто описать схему, а реально проверить runtime, admin auth-link endpoint, текущие jobs и сделать переносимый способ восстановить тот же контур.

Agreed:
- Базовый TG-контур в Hermes состоит из трёх jobs: daily collector, daily digest, weekly QA.
- Для TG web-auth admin endpoint loopback-доступа недостаточно, если задан `TG_AUTH_ADMIN_TOKEN`: в этом режиме создание auth-link должно идти с токеном.
- Копирование в новый Hermes лучше делать не как устную инструкцию, а как проверяемый manifest + installer, которые восстанавливают wrappers и cron jobs idempotent-способом.

Implemented:
- Проверен текущий Hermes-профиль: активен `default`, TG jobs живут в `~/.hermes/cron/jobs.json`.
- Проверены и синхронизированы существующие jobs:
  - `daily-telegram-it-consulting-collector`
  - `daily-telegram-it-consulting-digest`
  - `weekly-telegram-it-consulting-qa`
- В проект `TG-API` добавлены:
  - `/home/hermes/workspace/TG-API/hermes_tg_cron_manifest.json`
  - `/home/hermes/workspace/TG-API/install_hermes_tg_cron.py`
- Installer восстанавливает wrapper-скрипты в `~/.hermes/scripts/`, создаёт или обновляет три TG cron jobs через `hermes cron create/edit` и затем доводит `enabled_toolsets` до текущего рабочего состояния.

Verified:
- `python3 /home/hermes/workspace/TG-API/collect_daily_pipeline.py` → `status=ok`, создан новый report `collect_2026-06-11_13-22-40.json`, получено `6` непустых сообщений.
- `python3 /home/hermes/workspace/TG-API/build_digest_context.py` → собраны актуальные `digest_payload_path` и `csv_path`, `requires_review_count=1`.
- `curl -X POST http://127.0.0.1:8001/auth/telegram/admin/create_link` с `X-Auth-Token` → `201/ok`, создана рабочая ссылка авторизации для `profile_private`.
- `python3 /home/hermes/workspace/TG-API/weekly_monitor_qa.py` → weekly QA report собран без ошибок.
- `python3 /home/hermes/workspace/TG-API/install_hermes_tg_cron.py` → все три TG jobs успешно `updated` в текущем Hermes.
- `hermes cron status` подтвердил, что gateway running и TG jobs присутствуют в активном расписании.

Rejected:
- Оставлять восстановление TG cron-контура только в текущем `jobs.json` без project-local manifest/install слоя.
- Считать admin create_link «неработающим», не учитывая обязательный токеновый режим при включённом `TG_AUTH_ADMIN_TOKEN`.

Open questions:
- Если появится отдельный Hermes-профиль или второй серверный Hermes-home, installer стоит прогнать уже в том целевом контуре и отдельно проверить delivery/origin semantics именно там.

[2026-06-11] — Hermes Web: канонические dev/prod контуры

Context:
- Зафиксировали разделение dev и prod по разным серверам и портам, чтобы не путать, где именно править и проверять frontend/backend.

Agreed:
- Dev-контур целиком живёт на 95.182.85.233: backend 8791, frontend 8793, auxiliary 8794.
- Prod backend живёт на 178.104.207.89: 8791 и 8794.
- Prod frontend живёт на 95.182.85.233:8803.
- Для prod фронтовые правки нужно вносить и проверять на 95.182.85.233:8803, а backend-правки — на 178.104.207.89.

Rejected:
- Не считать frontend на 178.104.207.89 целевой prod-поверхностью.
- Не смешивать frontend/runtime-проверки prod с dev-контурами без явной оговорки.

Reflection (agent’s view):
- Для Hermes Web порт и сервер являются приёмочным инвариантом, а не справочной деталью.

[2026-06-12] — Hermes Web prod backend 178: LLM routing переведён в free-first с fallback на платные модели

Context:
- Пользователь попросил не только проверить, но и реально довести prod backend routing на `178.104.207.89`.
- Нужно было отдельно настроить reasoning-цепочку и обычную LLM-цепочку так, чтобы бесплатные модели шли первыми, а платные использовались как fallback.

Agreed:
- Для reasoning first-hop должен быть `nvidia/nemotron-3-ultra-550b-a55b:free`, а `deepseek/deepseek-r1-0528` — fallback на первый `runtime_error`.
- Для обычного режима default model должна быть free-first, а `openrouter/owl-alpha` должен уходить в хвост цепочки как платный fallback.
- Лимит reasoning per user на prod backend `178` фиксируется как `10` запросов в день.

Implemented:
- На `178.104.207.89` обновлён runtime-источник `~/.hermes/.env`.
- Для reasoning выставлены:
  - `HERMES_WEB_REASONING_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free`
  - `HERMES_WEB_REASONING_MODEL_CANDIDATES=nvidia/nemotron-3-ultra-550b-a55b:free,deepseek/deepseek-r1-0528`
- Для обычного режима выставлены:
  - `HERMES_WEB_HERMES_API_MODEL=google/gemma-4-31b-it:free`
  - `HERMES_WEB_STANDARD_MODEL_CANDIDATES=google/gemma-4-31b-it:free,meta-llama/llama-4-maverick:free,qwen/qwen3-235b-a22b:free,nvidia/nemotron-3-super-120b-a12b:free,openrouter/owl-alpha`
- User-unit `hermes-web-backend-8791.service` перезапущен от пользователя `hermes`.

Verified:
- Живой backend-процесс на `178:8791` после рестарта поднялся успешно и слушает `0.0.0.0:8791`.
- `/api/health` на `178:8791` отдаёт:
  - `default_model = google/gemma-4-31b-it:free`
  - `reasoning_model = nvidia/nemotron-3-ultra-550b-a55b:free`
  - `per_user_requests_per_day = 10`
- Runtime-проверка deployed `app.py` в service-env пользователя `hermes` подтвердила цепочки:
  - standard: `google/gemma-4-31b-it:free -> meta-llama/llama-4-maverick:free -> qwen/qwen3-235b-a22b:free -> nvidia/nemotron-3-super-120b-a12b:free -> openrouter/owl-alpha`
  - reasoning: `nvidia/nemotron-3-ultra-550b-a55b:free -> deepseek/deepseek-r1-0528`
- Симуляция первого `runtime_error` в reasoning-flow подтвердила фактический fallback:
  - первая попытка: `nvidia/nemotron-3-ultra-550b-a55b:free`
  - вторая попытка: `deepseek/deepseek-r1-0528`
  - `fallback_used = true`

Rejected:
- Оставлять prod reasoning на схеме `deepseek` first / `nvidia` second, если целевая политика — free-first.
- Оставлять обычный prod default model на `openrouter/owl-alpha`, если бесплатные модели достаточны как первая линия.
- Проверять systemd user-unit от `root` как будто это тот же user-session, что и у runtime `hermes`.

Reflection (agent’s view):
- Для split-runtime конфигураций важно проверять не только файл на диске, но и живое окружение процесса после рестарта.
- В этой схеме порядок primary model и candidate-chain является частью продуктовой политики, а не просто технической деталью.
[2026-06-14] — Hermes 178 internal agent jobs: global fallback chain restored, self-learning jobs switched to reasoning model

Context:
- Пользователь попросил не только добавить внутренние agent self-learning/self-development cron-задачи на `178`, но и довести общую LLM fallback-логику Hermes до рабочего состояния.
- Дополнительно пользователь уточнил, что для таких внутренних задач имеет смысл брать reasoning-модель сразу, а не обычный default-маршрут.

Agreed:
- Для Hermes profile `default` на `178.104.207.89` нужно вернуть согласованную global fallback-цепочку free-first для обычных запросов, а не оставлять одиночный `openrouter/owl-alpha`.
- Для внутренних job `agent-self-learning-daily` и `agent-self-development-weekly` primary model должна быть reasoning-ориентированной, чтобы они не зависели от обычного lightweight-маршрута.
- Доставка внутренних отчётов остаётся `local`, без внешнего спама.

Implemented:
- В `~/.hermes/config.yaml` на `178` выставлен default model `google/gemma-4-31b-it:free` через `openrouter`.
- В `fallback_providers` на `178` записана цепочка: `meta-llama/llama-4-maverick:free -> qwen/qwen3-235b-a22b:free -> nvidia/nemotron-3-super-120b-a12b:free -> openrouter/owl-alpha`.
- Для job `7814864147e0` (`agent-self-learning-daily`) и `d282ba63b693` (`agent-self-development-weekly`) в `~/.hermes/cron/jobs.json` выставлены `provider=openrouter` и `model=deepseek/deepseek-r1-0528`.
- Состояние `429` на единственном `openrouter` credential было сброшено через `hermes auth reset openrouter`.
- В текущем профиле `default` добавлены аналогичные локальные задачи: `eva-agent-self-learning-daily` (`319fed30bd3b`) и `eva-agent-self-development-weekly` (`6dfe0d3e6fa0`).

Verified:
- `hermes fallback list` на `178` показывает primary `google/gemma-4-31b-it:free` и цепочку из 4 fallback entries в согласованном порядке.
- JSON-проверка `~/.hermes/cron/jobs.json` на `178` подтвердила model override `deepseek/deepseek-r1-0528` для обеих внутренних agent-jobs.
- `hermes cron status` на `178` подтверждает, что cron gateway запущен и active jobs зарегистрированы.

Blocked:
- На `178` доступен только один credential `openrouter`; других провайдерских credential для реального cross-provider failover сейчас нет.
- Из-за этого fallback now restores model chain semantics, но не устраняет системный риск, когда сам единственный `OPENROUTER_API_KEY` снова упрётся в provider-level `429`.
- Ручной re-trigger self-learning job не дал нового completed run в доступном окне проверки; последнее зафиксированное выполнение по-прежнему осталось с `RuntimeError: HTTP 429: Provider returned error`.

Rejected:
- Оставлять global Hermes config на `178` в состоянии `openrouter/owl-alpha` без fallback chain.
- Пускать внутренние self-learning job по обычному default-маршруту, если пользователь отдельно попросил reasoning-first поведение.
[2026-06-14] — Hermes Web prod contour: personalization/password/jobs/cron delivery verified live on 178, but productive rollout still limited by dev-mode frontend on 8803

Context:
- Пользователь попросил довести и live-проверить prod-контур Hermes Web по критичным продуктовым сценариям: персонализация, пароль, задачи, cron-вывод и доставка результатов добавленному пользователю.
- Дополнительно нужно было понять, можно ли уже отдавать контур пользователям в реальную работу.

Agreed:
- Проверка должна идти по каноническому split-контуру: `95.182.85.233:8803` — user-facing frontend, `178.104.207.89:8791` — prod backend.
- Для cron/job сценария критично подтвердить не только успешный run, но и то, что fixed recipient получает результат в отдельный job-thread, а не в общий чат.
- Итоговая оценка готовности к productive rollout должна опираться на live runtime, а не только на локальные патчи и тесты.

Implemented:
- На backend `178.104.207.89:8791` выложены и перезапущены изменения по:
  - персонализации только через frontend/backend user memory без file-based persona;
  - удалению default agent name из backend prompt-paths;
  - минимальной длине пароля 8 символов;
  - job display name / fixed_user recipient path;
  - очистке технического хвоста из cron/job delivery текста.
- На acceptance-проверке временно создавались admin/user/job сущности, затем были удалены после проверки.

Verified:
- `systemctl --user status hermes-web-backend-8791.service` на `178` → `active (running)`; backend слушает `0.0.0.0:8791`.
- `curl http://127.0.0.1:8791/api/service-info` на `178` → `{"status":"ok","service":"Hermes Web","mode":"hermes-api"}`.
- Целевые backend regression-тесты на `178` прошли: personalization / password(8) / job display+recipient.
- Live acceptance cron/job сценарий на `178` прошёл:
  - `run_status = success`;
  - `result_has_technical_footer = false`;
  - `message_has_technical_footer = false`;
  - у владельца создан job-thread `id=20`;
  - у добавленного получателя создан отдельный job-thread `id=21`;
  - `separate_thread_ids = true`.
- После cleanup в prod DB не осталось временных `accept-*` пользователей.
- Текущее состояние prod backend DB после cleanup:
  - `users = 2`;
  - `jobs = 0`;
  - `threads = 12`;
  - `job_runs = 0`.
- User-facing frontend `95.182.85.233:8803` отвечает `200 OK`, а `/api/service-info` через него возвращает `status=ok`.

Diagnostic conclusion:
- Backend-контур на `178` по ключевым продуктовым сценариям готов к рабочему использованию.
- Главный оставшийся риск productive rollout — frontend `8803` работает как Vite dev server, а не как production build:
  - systemd unit `hermes-web-frontend-8803.service` запускает `npm run react:dev`;
  - в unit явно стоит `NODE_ENV=development`;
  - в логах видны HMR updates.
- Поэтому текущая честная оценка: контур годится для controlled pilot / ограниченной рабочей эксплуатации, но не выглядит как полностью упакованный production frontend для широкого пользовательского запуска.

Rejected:
- Считать контур полностью production-ready только потому, что backend healthchecks и cron/job acceptance уже зелёные.
- Игнорировать факт, что user-facing frontend на `8803` остаётся dev-mode runtime.

Next checkpoint:
- Перед полноценной выдачей пользователям перевести `8803` с `react:dev`/Vite HMR на стабильный production frontend serving path и затем повторить короткую live-приёмку на том же split-контуре.

[2026-06-14] — Hermes Web 8803 переведён с Vite dev server на production frontend serving path

Context:
- После предыдущей приёмки главным blocker для полноценного productive contour оставался user-facing frontend `95.182.85.233:8803`, который жил как `react:dev`/Vite HMR.
- Backend `178.104.207.89:8791` уже был live-подтверждён по ключевым продуктовым сценариям, поэтому следующий шаг был именно про frontend-serving contour.

Agreed:
- `8803` больше не должен зависеть от dev server/HMR.
- Split-контур сохраняется прежним: `95.182.85.233:8803` как frontend и `178.104.207.89:8791` как backend через `/api` proxy.
- Перевод считается завершённым только если проверены: static asset serving, `/api` proxy, auth/read/write path и cleanup временных acceptance users.

Implemented:
- Добавлен production frontend server `scripts/serve_frontend_prod.mjs`:
  - раздаёт `dist/frontend-react` как статический SPA bundle;
  - проксирует `/api` на `HERMES_WEB_FRONTEND_BACKEND_BASE`;
  - даёт SPA fallback на `index.html`.
- `run_frontend_react_service.sh` переведён на режимный запуск:
  - `HERMES_WEB_FRONTEND_MODE=dev` → старый `npm run react:dev`;
  - `HERMES_WEB_FRONTEND_MODE=prod` → `node scripts/serve_frontend_prod.mjs`.
- В `package.json` добавлен script `react:serve-prod`.
- User-systemd unit `~/.config/systemd/user/hermes-web-frontend-8803.service` переведён на:
  - `NODE_ENV=production`;
  - `HERMES_WEB_FRONTEND_MODE=prod`.

Verified:
- `npm run react:build` → OK.
- Локальный test-start prod server на `8813` успешно обслуживал HTML и `/api/service-info` через proxy.
- После `daemon-reload`/restart `hermes-web-frontend-8803.service`:
  - unit `active (running)`;
  - main process = `node /home/hermes/workspace/hermes-web-mvp-react-8793/scripts/serve_frontend_prod.mjs`;
  - listener на `0.0.0.0:8803` подтверждён через `ss -ltnp`.
- `curl http://127.0.0.1:8803/` и `curl http://95.182.85.233:8803/` отдают production HTML со статическим bundle (`/assets/index-*.js`, `/assets/index-*.css`).
- `curl http://127.0.0.1:8803/api/service-info` и `curl http://95.182.85.233:8803/api/service-info` → `status=ok`.
- Acceptance через user-facing contour `8803/api` прошла:
  - `POST /api/auth/login` → `200`;
  - `GET /api/me` → `200`;
  - `GET /api/jobs/meta` → `200`;
  - `POST /api/threads` → `201`;
  - `GET /api/threads` показал созданный thread (`thread_visible_in_list = true`).
- После cleanup в prod DB не осталось временных `accept-8803-*` пользователей.

Diagnostic conclusion:
- User-facing frontend contour `8803` больше не работает как dev/HMR runtime.
- Текущий split-контур теперь выглядит как нормальный production-like runtime для рабочей эксплуатации: статический frontend + backend proxy + подтверждённый auth/read/write flow.
- Снят именно blocker уровня serving contour; дальнейшие риски уже относятся не к dev-server режиму, а к общей продуктовой зрелости и будущим сценариям приёмки.

Rejected:
- Оставлять `8803` на Vite dev server только потому, что он уже был доступен снаружи.
- Считать простой `200 OK` на `/` достаточным без проверки `/api` proxy и auth/read/write round-trip.

[2026-06-14] — Hermes Cron задачи в Web API должны поддерживать админскую маршрутизацию по пользователям с отдельными job-чатами

Context:
- Выяснилось, что старая трактовка Hermes Cron задач была слишком узкой: UI показывал только исходный `deliver`, а не продуктовую модель назначения получателей.
- Пользователь уточнил целевой образ: расписание и базовая конфигурация живут в Hermes Cron, но администратор внутри Web API должен иметь возможность назначать нужных получателей, и каждому результат должен приходить в отдельный чат.
- В текущем local-first контуре не хотелось вводить новый внешний оркестратор или отдельный SaaS-слой доставки.

Agreed:
- Hermes Cron остаётся source of truth для schedule/prompt/base deliver.
- Hermes Web становится слоем маршрутизации и fan-out по пользователям.
- Для Hermes Cron нужен отдельный overlay получателей в backend, не завязанный на сырой `deliver`-target как единственный механизм UX.
- Доставка результата должна раскладываться в отдельные job-чаты пользователей, а не в один общий чат.
- Минимально рабочая реализация должна опираться на уже существующие локальные артефакты Hermes: `~/.hermes/cron/output/...`.

Implemented:
- В `services/backend/app.py` добавлены:
  - `hermes_job_recipients` — overlay-таблица для админского назначения получателей Hermes Cron задач;
  - `hermes_job_delivery_state` — состояние последнего доставленного output-файла;
  - `threads.external_job_id` — привязка отдельных job-чатов к текстовому Hermes job id.
- Реализована backend-логика:
  - `fetch_hermes_job_recipients(...)`;
  - `replace_hermes_job_recipients(...)`;
  - `resolve_hermes_job_recipient_user_ids(...)`;
  - `ensure_hermes_job_thread_for_user(...)`;
  - `sync_hermes_job_threads(...)`;
  - `reconcile_hermes_job_delivery(...)`.
- Для Hermes Cron результат теперь может забираться из `~/.hermes/cron/output/<job_id>/*.md`, извлекаться из блока `## Response` или script-output tail и раскладываться в отдельные job-чаты назначенных пользователей.
- `GET /api/jobs`, `GET /api/jobs/<id>`, `PATCH /api/jobs/<id>`, `POST /api/jobs/<id>/run` обновлены так, чтобы Hermes Cron задачи в Web UI:
  - были админски редактируемыми по recipients;
  - показывали overlay-получателей;
  - синхронизировали отдельные threads;
  - подхватывали свежие cron outputs для fan-out.
- В `services/backend/hermes_cron_bridge.py` `to_web_job(...)` расширен параметрами `recipients` и `read_only`, чтобы Web backend мог отдавать не только сырой Hermes `deliver`, но и продуктовую маршрутизацию.
- Во frontend `services/frontend-react/src/App.jsx` снова включено редактирование получателей для `source_of_truth = hermes_cron` и обновлено пояснение блока «Кто получает результат» под новую модель.
- На prod backend `178.104.207.89` выложены `app.py` и `hermes_cron_bridge.py`, backend перезапущен вручную через `waitress-serve` на `8791`.

Verified:
- `python3 -m py_compile services/backend/app.py services/backend/hermes_cron_bridge.py` → OK.
- Добавлен и пройден smoke-тест `test_hermes_cron_job_admin_recipients_create_separate_thread_and_deliver_output`:
  - admin назначает `fixed_user` для Hermes Cron job;
  - создаётся отдельный thread по `external_job_id`;
  - результат из mock `cron/output` попадает в отдельный чат пользователя.
- `npm run react:build` в корне репозитория → OK.
- На `178.104.207.89`: `waitress-serve` после выкладки поднят, `curl http://127.0.0.1:8791/api/service-info` → `{"status":"ok"...}`.

Constraints / unresolved:
- SSH-доступ к frontend-хосту `95.182.85.233` по-прежнему отсутствует (`Permission denied`), поэтому frontend-правка пока подтверждена локальной сборкой, но не выкачена мной на этот внешний хост в рамках текущей сессии.
- Live round-trip через реальный prod login/admin UI ещё требует отдельной пользовательской или штатной runtime-проверки с действующей авторизацией.

Rejected:
- Считать Hermes Cron задачи по определению «нередактируемыми» для продуктовой маршрутизации только потому, что их schedule живёт вне local jobs.
- Пытаться решать fan-out новой внешней инфраструктурой, когда можно использовать текущий Hermes Cron output и существующую web-модель threads/messages.
- Оставлять UX, где UI обещает назначение получателей, а backend умеет только raw `deliver` target.

[2026-06-15] — Hermes Web chat: не сбрасывать прокрутку вниз при фоновом refresh без новых сообщений

Context:
- После включения polling для чата пользователь получил новый UX-дефект: при попытке подняться к ранним сообщениям экран через несколько секунд снова сбрасывался вниз, даже когда переписка уже не менялась.
- Причина оказалась во frontend, а не в backend: polling раз в 8 секунд подменял `appState.messages` новым массивом, и `ChatScreen` безусловно делал `scrollTop = scrollHeight` на любое обновление `messages`.

Agreed:
- Автопрокрутка вниз допустима только в двух случаях: при смене активного чата или когда реально изменился хвост сообщений и пользователь уже находится у нижней границы.
- Фоновый refresh без новых сообщений не должен ломать чтение истории и возвращать пользователя вниз.

Implemented:
- В `services/frontend-react/src/App.jsx` логика `ChatScreen` переведена с безусловного `scrollTop = scrollHeight` на guarded auto-scroll:
  - введён `shouldStickToBottomRef`, который отслеживает, находится ли пользователь у нижней границы;
  - добавлены `previousThreadIdRef`, `previousMessageCountRef`, `previousMessageTailRef`, чтобы отличать реальное изменение хвоста сообщений от простого refresh того же содержимого;
  - автопрокрутка выполняется только при смене треда или при изменении хвоста сообщений, если пользователь не уходил вверх по истории.
- Frontend пересобран и перевыложен на боевой surface `95.182.85.233:8803`.

Verified:
- `npm run react:build` → OK.
- На изолированном local-first acceptance-контуре (`127.0.0.1:8891` backend `mock-hermes`, `127.0.0.1:8893` frontend) Playwright-проверка подтвердила регрессию закрытой:
  - перед ожиданием: `distanceFromBottom = 900`, `scrollTop = 3404`;
  - после `9.5s` idle polling: `distanceFromBottom = 900`, `scrollTop = 3404`;
  - `jumpedToBottom = false`, `scrollDelta = 0`.
- Боевой frontend `95.182.85.233:8803` после рестарта user-unit отдаёт свежий bundle `assets/index-CDUNU_Pl.js`; новый `MainPID` frontend-сервиса — `220564`.

Rejected:
- Возвращать безусловную автопрокрутку на любое обновление `messages` только ради простоты кода.
- Лечить симптом отключением polling целиком: проблема была в scroll-policy, а не в самом refresh-механизме.

[2026-06-15] — Hermes Web chat: базовая безопасная поддержка markdown во frontend

Context:
- Боевой Hermes на `178` активно отдаёт ответы с markdown-разметкой, а web-frontend до этого показывал всё как плоский `pre-wrap` текст.
- Из-за этого терялись структура ответа и читаемость: заголовки, списки, inline/code blocks, ссылки и цитаты.

Agreed:
- Не отключать markdown на backend/агенте только ради Web.
- Добавить во frontend минимальный безопасный markdown-rendering без raw HTML и без отдельного параллельного формата ответов для web-контура.

Implemented:
- В `services/frontend-react/src/App.jsx` добавлен локальный renderer для базового подмножества markdown:
  - headings `#`–`###`;
  - unordered/ordered lists;
  - blockquote;
  - fenced code blocks;
  - inline code;
  - `**bold**`, `*italic*`;
  - markdown links `[label](https://...)` и `mailto:`.
- Рендер сделан безопасным: raw HTML не интерпретируется, ссылки ограничены `http/https/mailto`, контент проходит как React text/nodes без `dangerouslySetInnerHTML`.
- В `services/frontend-react/src/styles.css` добавлены базовые стили для markdown-блоков внутри message bubble.
- Frontend пересобран и перевыложен на боевой surface `95.182.85.233:8803`.

Verified:
- `npm run react:build` → OK.
- На изолированном acceptance-контуре (`127.0.0.1:8891` backend `mock-hermes`, `127.0.0.1:8893` frontend) Playwright-проверка подтвердила реальный render markdown-сообщения:
  - `heading=true`;
  - `listItems=2`;
  - `strong=true`;
  - `linkHref=https://example.com`;
  - `inlineCode=true`;
  - `codeBlock=true`;
  - `quote=true`.
- Боевой frontend после рестарта user-unit отдаёт свежие bundle-артефакты:
  - JS: `assets/index-Cm08P9bU.js`;
  - CSS: `assets/index-CfEiDXM5.css`.

Rejected:
- Отдельно упрощать/отключать markdown на стороне Hermes только для Web.
- Тащить полноценный HTML-render path с `dangerouslySetInnerHTML` ради быстрого эффекта.

[2026-06-15] — Hermes Web 178: export-path должен пропускать apology/limitation-сообщения про `.docx` и брать последний содержательный ответ

Context:
- Пользователь указал на live-дефект в переписке Виктории (`thread_id=21`, `Flatpak`): backend уже умел отдавать реальный `file_response`, но при запросе `Так дай файл в docx` экспортировал не содержательный ответ, а предыдущее apologetic-сообщение модели о том, что она якобы не умеет создавать `.docx`.
- Проверка продовой БД на `178.104.207.89` подтвердила root cause: сообщение `125` было `file_response` с `exported_message_id=123`, а `preview_excerpt` вложения начинался с текста `Я приношу вам свои глубочайшие извинения... не могу создавать бинарные файлы .docx...`.
- Это означало, что backend export-route выбирал просто последний assistant-message, если он не был `processing_status`/`file_response`, и не отличал содержательный ответ от служебной apology/limitation-реплики.

Agreed:
- Для export-path недостаточно пропускать только `processing_status`, `file_response` и явные error-сообщения.
- Assistant-реплики, в которых модель рассуждает про собственные ограничения создания `.docx`/файлов, не должны становиться target-сообщением для экспорта.
- В таком случае backend обязан откатиться к последнему содержательному assistant-ответу до apology/limitation-реплики.

Implemented:
- В `services/backend/app.py` добавлен список `MESSAGE_EXPORT_NON_CONTENT_MARKERS` для характерных limitation/apology-маркеров вроде `не могу создавать бинарные файлы`, `инструмент для генерации бинарных файлов`, `пытался создать текстовые файлы`, `присвоить им расширение`, `ошибочными обещаниями`, `вставить в word`, `прикрепить файл`.
- `is_exportable_assistant_message(...)` ужесточён: такие limitation/apology-сообщения теперь исключаются из выбора export-target так же, как `processing_status` и явные error-path сообщения.
- Изменённый `app.py` выложен на `178.104.207.89` в `/home/hermes/workspace/hermes-web-mvp-react-8793/services/backend/app.py`.
- `hermes-web-backend-8791.service` перезапущен через `systemctl --user restart`.

Verified:
- Локально: `python3 -m pytest services/backend/test_smoke.py -k "export_skips_docx_limitation_apology or export_skips_service_messages" -q` → `2 passed`.
- Локально: `python3 -m pytest services/backend/test_smoke.py -k "message_export or export_" -q` → `3 passed`.
- На `178`: backend после рестарта активен, новый `MainPID=541334`, `waitress` снова слушает `0.0.0.0:8791`.
- Live acceptance на `178` проведён на отдельном acceptance-user (`user_id=4`) в контролируемом треде `export-regression-check`:
  - в тред заранее записаны два assistant-сообщения: содержательный ответ и limitation/apology про `.docx`;
  - `POST /api/threads/28/messages` с `Так дай файл в docx` вернул `file_response`;
  - итоговый `exported_message_id=130` указывает на содержательный ответ, а не на limitation/apology;
  - `preview_excerpt` вложения = `Вот содержательный ответ про Flatpak`.

Rejected:
- Считать этот дефект чисто модельным, если фактическая ошибка сидит в backend-логике выбора export-target.
- Экспортировать любой последний assistant-text без попытки отличить содержательный ответ от apology/limitation-пояснения о невозможности создать файл.

Open questions:
- Если похожие limitation-сообщения начнут приходить в других формулировках, следующий уровень — выделить более общий classifier для non-content assistant-messages, а не расширять только marker-list.

[2026-06-15] — Hermes Web 178: file-request contract ужесточён; generic 'Отправь мне файл' теперь детектируется как export-route, при отсутствии предыдущего содержательного assistant-answer backend возвращает короткую file-specific ошибку вместо LLM-apology, а live DOCX-выдача подтверждена по HTTP (`Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`, zip magic `PK\x03\x04`).
Context:
- На проде у Виктории historical failure состоял из двух частей: сначала export-route взял неправильный assistant-message, затем запрос `Отправь мне файл` ушёл в обычный LLM-path и завершился `timed out`.
- Проверка на 178 показала, что backend не зависит от `execute_code`/установки библиотек во время запроса: `.docx` собирается локально через `python-docx`, пакет установлен в backend `.venv`.
Decision:
- Расширить generic file-intent detection: если в запросе есть action-marker (`отправ`, `пришл`, `дай`, `сформир`, `выгруз` ...) и target-marker (`файл`, `документ`, `docx`, `word`), считать запрос export-request даже без явного `docx`.
- Для export-request без пригодного предыдущего assistant-answer не отправлять запрос в LLM вообще: backend возвращает короткую file-specific ошибку `Не удалось сформировать файл по предыдущему ответу...`.
- Если export-intent всё же дошёл до LLM и модель начала рассказывать про ограничения/Markdown/установку библиотек, backend гасит такой ответ и переводит задачу в короткую file-specific ошибку вместо apology-полотна.
Rejected:
- Лечить проблему только повышением timeout: это уменьшает часть `timed out`, но не исправляет неверную маршрутизацию generic file-request.
- Верить тексту модели про `system security blocked library install`: live-проверка на 178 показала, что это не реальный backend constraint, а ложное self-explanation модели.

[2026-06-15] — Hermes Web 178: file-request разделён на два корректных режима — export existing answer и generate new content + attach.
Context:
- После первого fixes backend перестал уходить в Markdown/apology-ответы, но всё ещё ошибочно трактовал содержательные запросы вроде `Пришли мне полноценный концепт ... в виде файла` как `export previous answer`, из-за чего повторно выгружал старый assistant-message (`exported_message_id=129`).
Decision:
- Ввести явное разделение режимов:
  - короткий generic file-intent (`Отправь мне файл`, `Пришли файл`, `Сохрани это в docx`) => export existing answer;
  - содержательный file-intent с собственной задачей (`... концепт презентации ... в виде файла`) => сначала генерация нового ответа через LLM, затем упаковка именно этого нового ответа в attachment.
- Для generate-and-attach backend создаёт `message_kind=file_response` с `source=generated_file_response`, `generated_from_request=true`, без `exported_message_id`.
Verification:
- Regression tests локально: `7 passed` по export/file-request набору.
- Live 178: controlled thread `file-mode-live` (`thread_id=31`, `task_id=72`, `message_id=149`) завершился `completed` с `source=generated_file_response`; attachment скачивается по HTTP как настоящий `.docx` (`Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`, magic `PK\x03\x04`), preview_excerpt начинается с нового сгенерированного концепта, а не со старого черновика.

[2026-06-15] — Hermes Web 178: backend timeout для Hermes API и reasoning поднят с 180s до 300s

Context:
- После разбора треда Виктории стало видно, что одна из финальных попыток `Отправь мне файл` завершилась не export-дефектом, а отдельной backend-ошибкой `timed out`.
- В `services/backend/app.py` текущий продовый backend по умолчанию использовал `HERMES_WEB_HERMES_API_TIMEOUT=180`, а `HERMES_WEB_HERMES_API_RETRY_TIMEOUT` и `HERMES_WEB_REASONING_TIMEOUT` наследовали то же значение.
- Пользователь попросил не обсуждать это абстрактно, а сразу реально расширить timeout на контуре `178`.

Agreed:
- Для продового backend `178.104.207.89:8791` разумный первый шаг — поднять timeout'ы Hermes API/retry/reasoning до `300` секунд, не меняя пока остальную routing-логику.
- Такое изменение должно снижать число ложных `timed out` на длинных генерациях и file-oriented ответах, но не считается полным лечением upstream-зависаний.

Implemented:
- На `178` добавлен systemd user drop-in `/home/hermes/.config/systemd/user/hermes-web-backend-8791.service.d/timeout.conf`.
- В drop-in выставлены:
  - `HERMES_WEB_HERMES_API_TIMEOUT=300`
  - `HERMES_WEB_HERMES_API_RETRY_TIMEOUT=300`
  - `HERMES_WEB_REASONING_TIMEOUT=300`
- Выполнены `systemctl --user daemon-reload` и `systemctl --user restart hermes-web-backend-8791.service`.

Verified:
- `systemctl --user show hermes-web-backend-8791.service -p Environment -p MainPID` после рестарта показывает новые значения timeout и новый `MainPID=565968`.
- Прямое чтение `/proc/565968/environ` на `178` подтверждает:
  - `HERMES_WEB_HERMES_API_TIMEOUT=300`
  - `HERMES_WEB_HERMES_API_RETRY_TIMEOUT=300`
  - `HERMES_WEB_REASONING_TIMEOUT=300`
- Live health после рестарта:
  - `http://178.104.207.89:8791/api/health` → `200`
  - `http://95.182.85.233:8803/api/health` → `200`
  - `http://178.104.207.89:8791/api/service-info` → `200`

Rejected:
- Оставлять timeout на `180` и объяснять user-facing file-failures только качеством модели.
- Сразу делать более агрессивные изменения в routing/worker-архитектуре до проверки простого timeout-расширения на целевом продовом контуре.

Open questions:
- Если даже при `300s` в этом сценарии будут повторяться `timed out`, следующий уровень — смотреть не только timeout, но и разносить генерацию файлов/длинных ответов по отдельному async/queue-path или менять модель/маршрутизацию под тяжёлые запросы.

[2026-06-15] — Hermes Web 178: generate-and-attach file mode отделён от обычного chat-route и защищён от tool/apology transcript
Context:
- В продовом треде Виктории backend после предыдущего разделения режимов начал использовать `source=generated_file_response`, но последний live-артефакт (`message_id=151`) всё равно оказался неверным: в `.docx` ушёл не концепт, а tool/apology transcript модели (`I apologize... missed the required 'path' parameter ... <tool_code> write_file(...)`).
- Это показало, что одной только маршрутизации `generate new content + attach` недостаточно: generate-and-attach нельзя строить на обычном chat-path без отдельного output-contract.
Decision:
- Для содержательных file-request backend должен использовать отдельный generate-and-attach prompt-contract: модель возвращает только финальное содержимое документа, без tool chatter, apology, Markdown fences, XML/JSON и без разговоров о создании файла.
- Перед упаковкой ответа в attachment backend обязан валидировать generated text и отклонять tool/service transcript (`<tool_code>`, `write_file(...)`, служебные ошибки про параметры/ретраи) как непригодный для документа.
- Ошибка такого класса должна превращаться в короткий file-specific user-facing текст, а не в успешный `.docx` с мусором и не в общий `Не удалось получить ответ`.
Implemented:
- `services/backend/app.py`:
  - добавлен отдельный path `build_generated_file_messages(...)` + `call_generated_file_content(...)` для режима generate-and-attach;
  - generate-and-attach больше не использует обычный `call_hermes_api(...)` как есть, а даёт модели жёсткий контракт вернуть только текст документа;
  - добавлен guard `response_looks_like_tool_transcript(...)` по маркерам tool/service transcript;
  - добавлен `preferred_model_for_generated_file(...)`, чтобы generate-and-attach корректно уважал ручной выбор модели без сломанного `resolve_requested_model` path;
  - `normalize_public_error_text(...)` расширен отдельной user-facing ошибкой для `message_export_unfulfilled_by_model`.
- `services/backend/test_smoke.py`:
  - обновлён regression на generate-and-attach path;
  - добавлен отдельный тест на rejection tool transcript вместо успешного `.docx`.
- Новый `app.py` выложен на `178`, backend `hermes-web-backend-8791.service` перезапущен.
Verified:
- Локально: `python3 -m pytest services/backend/test_smoke.py -q` → `39 passed`.
- На `178`: backend после выкладки и рестарта отвечает `200` на `http://178.104.207.89:8791/api/health`; proxy `95.182.85.233:8803/api/health` тоже отвечает `200`.
- Live acceptance на `178` через реальный login пользователя `acceptance178@demo.local`:
  - создан thread `generated-file-live-check`, `thread_id=32`;
  - запрос `Пришли мне полноценный концепт презентации по Flatpak в виде файла` создал `task_id=75`, `message_id=155`;
  - результат `processing_status=completed`, `message_kind=file_response`, `source=generated_file_response`, `generated_from_request=true`;
  - attachment скачивается по HTTP как настоящий `.docx` (`Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`, magic `PK\x03\x04`);
  - `preview_excerpt` начинается с содержательного концепта презентации про Flatpak и больше не содержит `I apologize`, `<tool_code>` или `write_file(...)`.
Rejected:
- Считать проблему закрытой только потому, что `.docx` физически создаётся.
- Оставлять generate-and-attach на обычном chat-route без отдельного output-contract и без backend-валидации результата.

[2026-06-15] — Hermes Web 178: long-history generate-and-attach в треде Виктории переведён на focused context, timeout на реальном thread_id=21 снят

Context:
- После отделения generate-and-attach path от обычного export-route мусорный `.docx` был устранён, но именно в живом треде Виктории `thread_id=21` оставался второй дефект: повторный запрос `Пришли мне полноценный концепт презентации по Flatpak в виде файла` больше не создавал bad attachment, но завершался `task_id=74 -> status=error -> last_error=timed out`.
- История треда к этому моменту разрослась до 56 сообщений / ~45k символов, а прошлые assistant-ответы уже показывали взрыв prompt size до `75k` токенов (`message_id=151`) и длинную техническую шелуху про файлы, retries и инструменты.
- Значит корень проблемы был уже не в file-contract как таковом, а в том, что generate-and-attach продолжал тащить в модель весь thread целиком, включая старые file-failure loops и несодержательные сервисные хвосты.

Agreed:
- Для long-history file-generation backend не должен слепо скармливать модели весь тред.
- Generate-and-attach должен собирать focused context: брать только содержательные assistant-блоки и связанные с ними пользовательские запросы, а file-request chatter, `file_response`, `processing_status`, apology/service loops и короткие техсообщения отбрасывать.
- Критерий закрытия инцидента — не только успешный acceptance на новом чистом thread, а успешная генерация на реальном проблемном `thread_id=21` без timeout и без transcript leakage.

Implemented:
- На `178.104.207.89` в `services/backend/app.py` добавлены helper'ы:
  - `is_substantive_generated_file_context_row(...)`;
  - `select_generated_file_context_rows(...)`.
- `build_generated_file_messages(...)` переведён с full-thread path на focused context path.
- Focused context отбирает последние содержательные assistant-ответы (с отсечением коротких/технических/ошибочных file-loop сообщений) и ближайшие релевантные user turns вместо всей истории чата.
- Backend на `8791` перезапущен после правки; новый runtime pid поднялся уже с этим кодом.

Verified:
- До фикса на реальном треде Виктории: `task_id=74`, `message_id=153` -> `processing_status=error`, public error `Не удалось сформировать файл: upstream-ответ превысил лимит ожидания.`
- После фикса live rerun на том же `thread_id=21`:
  - создан новый `task_id=77`, `message_id=159`;
  - `status=completed`, `source=generated_file_response`, `generated_from_request=true`;
  - usage упал до `prompt_tokens=18642`, `total_tokens=21779` вместо прежних ~`75k` total tokens на плохом path;
  - attachment `Flatpak-2026-06-15_19-54-27.docx` сохранён как настоящий `.docx` (`41428 bytes`, magic `PK\x03\x04`);
  - `preview_excerpt` начинается уже с содержательного стратегического концепта по Flatpak и не содержит `I apologize`, `<tool_code>` или `write_file(...)`.
- Дополнительно подтверждено, что previous timeout больше не воспроизводится именно на исходном проблемном треде, а не только на отдельном acceptance thread.

Rejected:
- Лечить `timed out` простым дальнейшим поднятием timeout поверх уже раздутого prompt.
- Считать новый acceptance-thread достаточным доказательством, если реальный thread с длинной историей всё ещё падает.
[2026-06-17] — Hermes Web file-intent on 178:8791 hardened: direct export requests ("собери файл", "пришли файл", "выдай итоговый файл") must resolve to deterministic message_export attachments; discussion of file-generation bugs/logging must not trigger generated_file_response, and bare words like "экспорт"/"выгруз" inside ordinary text are not enough to enter file-flow
[2026-06-17] — Hermes Web assistant replies on 178:8791 must scrub leaked local filesystem paths like /home/hermes/... and /tmp/... from user-facing text unless delivered as real attachments
[2026-06-17] — Hermes Web summary-intent replies on 178:8791 must stay as summaries: strip follow-up consulting tails like "Рекомендация по реализации", "Рекомендация по следующему шагу", and "Следующий шаг" from final user-facing output
[2026-06-17] — Hermes Web file-generation routing on 178:8791 hardened: requests like "Собери один файл, где будет суммаризация" must go through generated_file_response with attachment delivery, not fall back to plain chat text or local markdown-path narration- 2026-06-17: Hermes Web 8803 user-task modal: root cause treated as frontend jobs-meta hydration race, not backend endpoint absence. Fix in services/frontend-react/src/App.jsx: ensureJobsContextLoaded() before openCreateJob/openCreateJobForUser, plus non-empty loading fallback in JobDraftModal while jobsMeta is still loading. Built live dist assets index-D7BTBwaS.js / index-DJBU-2ni.css for 8803.


[2026-06-17] — Hermes Web 8803 recipients/access modal must preload jobs context before opening

Context:
- На live frontend `95.182.85.233:8803` пользователь сообщил, что при клике `Добавить получателя` экран обнуляется.
- Backend smoke на jobs/recipients на контуре кода проходил, значит проблема была не в `178:8791`, а во frontend runtime-потоке открытия модалки.

Decision:
- Потоки `openRecipientsPicker` и `openAccessPicker` должны работать через тот же защитный async-path, что и создание задачи: сначала `ensureJobsContextLoaded()`, потом открытие modal.
- `JobMembersModal` не должен пытаться рисовать selector-контент в момент, когда `jobsMeta` ещё не готовы; вместо этого нужен безопасный loading-state.

Implemented:
- В `services/frontend-react/src/App.jsx`:
  - `openRecipientsPicker` и `openAccessPicker` переведены на `withAsync(async ...)` + `await ensureJobsContextLoaded()`;
  - в `JobMembersModal` добавлен `jobsMetaReady`;
  - при отсутствии метаданных показывается fallback `Загружаю список пользователей и чатов…`.

Verification:
- `npm run react:build` завершился успешно.
- Live `8803` отдаёт новый bundle `assets/index--zqScvDT.js`.
- Стартовый экран `95.182.85.233:8803` открывается без JS-ошибок в browser console.

Open question:
- Полная click-through проверка самой модалки на live UI всё ещё требует валидной авторизованной admin-сессии.


[2026-06-17] — Hermes Web 8803 recipients/access editing switched from per-click writes to draft + explicit save

Context:
- После устранения white screen на live frontend `95.182.85.233:8803` пользователь подтвердил, что добавление пользователей работает, но ощущается «дико тормознуто».
- Причина оказалась не в backend `178:8791`, а в UX-потоке frontend: каждый клик по пользователю сразу делал `getJob -> updateJob -> loadJobs -> loadJob`.

Decision:
- Модалки `Получатели` и `Доступ` должны работать в draft-режиме.
- Любые выборы внутри модалки меняют только локальный state.
- Backend вызывается один раз по явной кнопке `Сохранить`.

Implemented:
- В `services/frontend-react/src/App.jsx`:
  - `JobMembersModal` переведена на локальные `draftRecipients` / `draftAccess`;
  - добавлен индикатор несохранённых изменений;
  - добавлены кнопки `Сохранить` и `Отменить`;
  - старые per-click handlers заменены на единый `handleSaveJobMembers(...)`.
- В `services/frontend-react/src/styles.css`:
  - добавлен sticky footer для действий модалки.

Verification:
- `npm run react:build` прошёл успешно.
- Live `8803` отдаёт bundle `assets/index-DNOhiQXA.js` и `assets/index-BXgAFgkw.css`.
- Стартовый экран 8803 открывается без JS-ошибок.

[2026-06-17] — Hermes Web dashboard-building: Telegram analytics scenario removed from routing

Context:
- В prod-чате `Новый чат` на `95:8803` обычный запрос на правку письма падал мгновенно, хотя задачи по аналитике не было.
- Проверка live thread под `admin@demo.local` показала точную причину: backend ошибочно маршрутизировал текст в Telegram analytics path и возвращал `telegram_analytics_source_missing`.
- Корень был в слишком широком dashboard-trigger (`аналит*`) и в живом локальном builder-е `telegram_digest`, который больше не соответствует продуктовой модели.

Agreed:
- Сценарий Telegram-аналитики в части дашбордостроения считается отменённым и не должен участвовать в runtime-маршрутизации.
- Наличие слов `Telegram`, `интернет`, `аналитика`, `глубокая аналитика` внутри обычного текста не должно само по себе переводить запрос в dashboard-route.
- Явные dashboard-запросы и dashboard по пользовательским файлам должны остаться рабочими.

Implemented:
- В `services/backend/app.py`:
  - из `is_dashboard_request()` убран слишком широкий trigger `аналит`;
  - добавлен явный anti-trigger для отрицательных формулировок вроде `без дашборда`, `не нужен дашборд`, `не делай дашборд`, чтобы простое упоминание dashboard в отрицательном контексте не включало сценарий;
  - `dashboard_builder_definitions()` очищен: локальный builder `telegram_digest` удалён из runtime;
  - удалены helper'ы локальной Telegram analytics сборки и ошибка `telegram_analytics_source_missing` вместе с этим path;
  - из `LEGACY_DASHBOARD_SOURCE_ALIASES` убран alias `telegram_digest`;
  - из dashboard connector discovery убран `telegram_analytics_workspace`.
- В `services/backend/test_smoke.py`:
  - убран тестовый сценарий локального dashboard по Telegram-дайджесту;
  - добавлена регрессия на запрос вида `Проверь общую текстовку письма... Telegram ... глубокая аналитика`, который теперь обязан идти в обычный chat path, а не в dashboard.
  - обновлена проверка policy normalization без `telegram_digest`.

Verified:
- `python3 -m py_compile services/backend/app.py` и `python3 -m py_compile services/backend/test_smoke.py` проходят.
- По узкому backend probe через штатный test harness:
  - явный запрос `Построй дашборд по локальной аналитике.` по-прежнему даёт `clarification_request`;
  - запрос на правку текста с упоминаниями `Telegram` и `глубокая аналитика` больше не получает `dashboard_result` и не несёт `dashboard` в meta;
  - его downstream теперь обычный `mock-hermes`;
  - PATCH dashboard-policy с `allowed_sources=['google_api_connector','web_research']` сохраняется как `['external_connector','web_research']`, без возврата `telegram_digest/local_dataset_registry`.

Rejected:
- Сохранять в коде полуживой Telegram analytics route «на всякий случай».
- Считать слово `аналитика` достаточным trigger-ом для dashboard-routing без явного запроса на дашборд.

[2026-06-17] — Cons-project должен хранить combined backup контура 95+178 вместе с TG API

Context:
- Для агента на 178 было решено вести отдельный GitHub backup в `git@github.com:Roshmial/Cons-project.git`.
- Выяснено, что production frontend `8803` физически живёт на сервере 95, но является неотъемлемой частью контура 178.
- Дополнительно пользователь потребовал включить в этот же backup и operational функционал `TG-API`.

Agreed:
- `Cons-project` хранит не snapshot одного сервера, а curated combined backup общего рабочего контура.
- В backup обязательно входят: frontend `8803` с 95, backend/runtime/deploy-контур 178 и локальный `TG-API` контур на 95.
- Для weekly refresh используется один центральный механизм на текущем сервере, потому что только он видит одновременно и локальные компоненты 95, и remote-контур 178.
- Еженедельное обновление должно идти в окне `03:00–06:00 МСК`; зафиксирован слот `04:00 МСК` (`0 1 * * 1` UTC).

Implemented:
- Обновлён скрипт `~/.hermes/scripts/cons_project_backup_weekly.py`:
  - добавлено копирование `local-95/tg-api/**`;
  - добавлены фильтры, исключающие TG API secrets, session/runtime/raw/export data, generated analytics, `.venv`, логи и state-файлы;
  - исключение runtime DB расширено до `.db`.
- В `Cons-project` автоматически генерируются и коммитятся описательные файлы:
  - `README.md`;
  - `BACKUP_SCOPE.md`;
  - `CONTOUR_MAP.md`;
  - `DEPLOYMENT_AND_BACKUP_LOGIC.md`;
  - `TG_API_SCOPE.md`.
- Backup заново собран и запушен в `origin/main`.

Verified:
- Ручной запуск `python3 /home/hermes/.hermes/scripts/cons_project_backup_weekly.py` прошёл успешно.
- GitHub backup обновлён commit-ом `ba0a7f4 Weekly curated backup refresh`.
- В HEAD подтверждено наличие новых root-docs и содержимого `local-95/tg-api/`, включая `app.py`, `telegram_monitor_pipeline.py`, `collect_daily_pipeline.py`, `telegram_web_auth.py`, `install_hermes_tg_cron.py`, `hermes_tg_cron_manifest.json`.

Rejected:
- Вести backup только по 178 и не включать production frontend `8803`.
- Хранить TG API отдельно от `Cons-project`, если он является operational частью того же рабочего контура.
- Тянуть в GitHub TG API runtime/session/export артефакты и чувствительные локальные state-файлы.

[2026-06-17] — Eva-project должен включать TG API и Hermes transfer kit; Cons-project должен хранить архитектурную и логическую схему prod-контура

Context:
- После включения TG API в `Cons-project` пользователь отдельно потребовал добавить TG API и в `Eva-project`.
- Дополнительно нужен комплект того, что потребуется для переноса Евы на чистый сервер после установки Hermes.
- Для `Cons-project` потребовалось не только хранение кода и runtime-артефактов, но и явное описание архитектурной и логической схемы prod-контура.

Agreed:
- `Eva-project` хранит не только skills и заметки, но и curated operational snapshot `TG-API` плюс Hermes transfer kit.
- В `Eva-project` должны лежать: `~/.hermes/config.yaml`, `~/.hermes/cron/jobs.json`, `~/.hermes/scripts/*` и bootstrap-документы для чистого Linux-сервера без secrets.
- `Cons-project` должен содержать отдельные root-docs, которые объясняют prod-контур не по коду, а по архитектурной и логической модели.
- Для `Cons-project` нужен отдельный zero-start runbook именно под развёртку с нуля, а не только под аварийное восстановление state.

Implemented:
- Обновлён `~/.hermes/scripts/eva_github_backup_weekly.py`:
  - добавлен curated backup `tg-api/**`;
  - добавлен раздел `hermes-runtime/` с `config/config.yaml`, `cron/jobs.json`, `scripts/*` и `transfer-kit/**`;
  - добавлены root-docs `HERMES_TRANSFER_AND_RESTORE.md` и `TG_API_SCOPE.md`.
- Обновлён `~/.hermes/scripts/cons_project_backup_weekly.py`:
  - добавлены root-docs `PROD_CONTOUR_ARCHITECTURE.md` и `PROD_CONTOUR_LOGIC.md`;
  - добавлен `DISASTER_RECOVERY_RUNBOOK.md` как zero-start runbook для развёртки с нуля;
  - в runbook добавлены минимальная командная шпаргалка и логика model fallback;
  - добавлен `MODEL_FALLBACK_LOGIC.md` как отдельное описание primary/auxiliary inference маршрутов;
  - `README.md` дополнен указанием, что в backup входят архитектурные, логические и deployment-описания prod-контура.
- Оба backup-репозитория пересобраны и запушены.

Verified:
- `Eva-project` обновлён commit-ом `a96f754 Weekly curated backup refresh`.
- В `Eva-project` подтверждено наличие `tg-api/**`, `hermes-runtime/config/config.yaml`, `hermes-runtime/cron/jobs.json`, `hermes-runtime/scripts/*`, `hermes-runtime/transfer-kit/**`, `HERMES_TRANSFER_AND_RESTORE.md`, `TG_API_SCOPE.md`.
- В `Cons-project` обновлён commit-ом `7d9f5e8 Weekly curated backup refresh`.
- В `Cons-project` подтверждено наличие `PROD_CONTOUR_ARCHITECTURE.md`, `PROD_CONTOUR_LOGIC.md`, `DISASTER_RECOVERY_RUNBOOK.md`, `MODEL_FALLBACK_LOGIC.md`, `CONTOUR_MAP.md`, `DEPLOYMENT_AND_BACKUP_LOGIC.md`.

Rejected:
- Держать переносный Hermes-kit только в голове или только в runtime, без Git backup.
- Ограничивать `Cons-project` только файловым snapshot без явного объяснения архитектуры split-host контура.

[2026-06-17] — Для сервера 178 нужен отдельный standalone backup под ключ, без смешения с combined backup 95+178

Context:
- Пользователь попросил сделать для 178 «аналогичное всё»: полноценный backup под ключ и со всеми артефактами.
- На 178 уже существовал локальный backup-скрипт, но он покрывал только project + systemd и был привязан к `Cons-project/main`, что конфликтовало бы с combined backup с 95.

Agreed:
- Для 178 нужен отдельный standalone backup-контур.
- Он должен включать не только web-project, но и `TG-API`, `Hermes runtime`, architecture docs, logic docs, zero-start runbook и model fallback logic.
- Публиковать standalone backup 178 нужно в тот же GitHub repo `Cons-project`, но в отдельную ветку `standalone-178`, чтобы не перезаписывать combined backup в `main`.
- На 178 должен быть собственный weekly refresh job, запускаемый локально на этом сервере.

Implemented:
- Создан новый скрипт `~/.hermes/scripts/cons_project_178_backup_weekly.py` на сервере 178.
- Скрипт собирает curated snapshot в `/home/hermes/workspace/cons-github-backup-178` со структурами:
  - `project/**`
  - `tg-api/**`
  - `runtime-systemd/**`
  - `hermes-runtime/**`
- Добавлены root-docs:
  - `PROD_CONTOUR_ARCHITECTURE.md`
  - `PROD_CONTOUR_LOGIC.md`
  - `DISASTER_RECOVERY_RUNBOOK.md`
  - `MODEL_FALLBACK_LOGIC.md`
  - `TG_API_SCOPE.md`
  - `HERMES_RUNTIME_SCOPE.md`
- Создан weekly cron job на 178:
  - `cons-project-178-backup-weekly`
  - schedule `30 1 * * 1`
  - mode `no-agent`
  - script `cons_project_178_backup_weekly.py`
  - workdir `/home/hermes/workspace`

Verified:
- На 178 создан и запушен standalone backup commit `8f61722 Weekly standalone 178 backup refresh`.
- Подтверждено, что текущая ветка backup-репозитория на 178 — `standalone-178`.
- Подтверждено наличие в backup `README.md`, `PROD_CONTOUR_ARCHITECTURE.md`, `PROD_CONTOUR_LOGIC.md`, `DISASTER_RECOVERY_RUNBOOK.md`, `MODEL_FALLBACK_LOGIC.md`, `TG_API_SCOPE.md`, `HERMES_RUNTIME_SCOPE.md`, `runtime-systemd/tg-api.service`, `hermes-runtime/config.yaml`.
- Подтверждено создание cron job `0eaf635c638e` на 178 для weekly refresh.

Rejected:
- Пушить standalone backup 178 в `Cons-project/main`, ломая combined backup 95+178.
- Ограничиваться только snapshot проекта без TG-API и Hermes runtime слоя.

[2026-06-19] — Hermes Web prod 178 chat runtime must reject fake structured file outputs, retry non-Russian chat answers, and catch weekly media-monitoring intents

Context:
- На prod `178.104.207.89` в chat-контуре подтвердились три реальные регрессии: агент уходил в португальский/английский, запросы на `csv`/`xlsx` могли завершаться ложным `file_response` из текста assistant-сообщения, а фразы про еженедельный сбор из СМИ не всегда распознавались как создание recurring job.
- Live-разбор по Postgres `hermes_web` и `services/backend/app.py` показал, что `process_chat_task()` после обычного LLM-path мог публиковать `generated_file_response` для `csv/xlsx/json/xml`, хотя backend не строил структурированный dataset, а только экспортировал текст ответа в message-export файл.
- Для language drift в publish-path не было backend-guard-а: даже явно не-русский ответ мог быть сохранён как финальный assistant message.

Decision:
- Backend не должен считать текстовый ответ валидным структурированным артефактом для `csv/xlsx/json/xml`; в таких случаях нужен честный error-path, а не псевдо-файл.
- Для пользователей с `language=ru` backend должен делать повторный LLM-вызов с жёстким требованием русского языка, если первичный ответ ушёл в иностранный язык.
- Chat-detection recurring jobs должна шире ловить явные weekly/media-monitoring формулировки (`еженедельный сбор`, `СМИ`, `обзор`, `дайджест`, `новости`) и более мягкие follow-up фразы.

Implemented:
- В `services/backend/app.py`:
  - `build_generated_file_reply()` теперь отклоняет `csv/xlsx/json/xml` через `structured_generated_file_not_supported` вместо публикации fake structured export;
  - добавлены `text_cyrillic_ratio()`, `reply_violates_expected_language()` и `enforce_russian_retry()`; `call_hermes_api()` теперь делает retry, если ответ для русского профиля вышел не-русским;
  - `normalize_public_error_text()` получил явные user-facing тексты для `structured_generated_file_not_supported` и `llm_reply_language_guard_failed`;
  - расширены `looks_like_recurring_job_request()` и `looks_like_recurring_job_followup()` для weekly/media-monitoring сигналов.
- На prod live `app.py` выложен с backup, backend `hermes-web-backend-8791.service` перезапущен.

Verification:
- Локально: `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` — ok.
- Локально: targeted smoke tests по language guard, fake structured export и recurring detection прошли (`4 tests OK` через `unittest`; `pytest` тоже показал `4 passed`, хотя раннер аварийно завершился уже после отчёта).
- На prod `178.104.207.89`: `curl http://127.0.0.1:8791/api/health` после рестарта вернул `status=ok`.
- На prod через прямой backend runtime test (`enqueue_chat_task` + `process_chat_task`) подтверждено:
  - weekly media request → `message_kind=job_created`, создан job `id=54`;
  - `csv` request → task завершается error-path с честным текстом `Не удалось сформировать файл: для CSV/XLSX/JSON/XML нужен структурированный набор данных...`, без attachments и без fake file success.
- На prod backend helper `reply_violates_expected_language()` подтверждён на реальных regression strings: Portuguese=`True`, English=`True`, Russian=`False`.

Follow-up:
- В live-окружении остаётся отдельный технический дефект: короткие python-скрипты с `import app` периодически завершаются `Aborted/Segmentation fault` уже после полезного результата. Это не помешало текущему fix/restart, но требует отдельной диагностики рантайма/нативных зависимостей backend `.venv`.

[2026-06-19] — Hermes Web должен переводить запросы вида `собери данные из источника X по формату Y` в backend collection contract до обычного chat/export path

Context:
- После фикса fake structured exports оставалась системная дыра: запросы вида `собери данные ... в csv` всё ещё могли уйти либо в общий LLM chat-path, либо в file/export-ветку, хотя для них нужен сначала формальный контракт сбора.
- Пользователь прямо потребовал «живой алгоритм», по которому можно реализовывать задачи формата `собери данные из источника X по формату Y`, а не только общий ответ модели.

Decision:
- Для collection-задач backend должен сначала фиксировать `collection_contract`, а не пытаться сразу отвечать обычным текстом или файлом.
- Контракт должен включать минимум: `source_kind/source_label`, `subject`, `output_format`, `fields`.
- Если данных для контракта не хватает, backend должен вернуть `clarification_request`.
- Для `csv/xlsx/json/xml` список полей результата обязателен.
- Этот route должен жить раньше общего export/file-path и раньше обычного LLM-path.

Implemented:
- В `services/backend/app.py` добавлены:
  - `infer_collection_output_format()`
  - `looks_like_collection_request()`
  - `infer_collection_source()`
  - `infer_collection_subject()`
  - `infer_collection_fields()`
  - `build_collection_contract_meta()`
  - `build_collection_clarification_or_contract_reply()`
- В `process_chat_task()` новый `collection_reply` включён раньше `maybe_build_export_reply()` и общего chat-path.
- Для complete-case backend теперь возвращает `message_kind=collection_contract` и кладёт execution steps в `meta.collection_contract`.
- Для incomplete-case backend теперь возвращает `message_kind=clarification_request` с downstream `chat:data_collection_clarification`.
- В `postprocess_assistant_reply()` `collection_contract` добавлен в actionable routes, чтобы backend не срезал такой ответ как «план без действия».
- Алгоритм сохранён отдельным артефактом: `/home/hermes/workspace/source-collection-algorithm.md`.

Verification:
- Локально: `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` — ok.
- Локально: unit tests прошли:
  - `test_collection_request_without_source_and_fields_returns_clarification`
  - `test_collection_request_with_source_format_and_fields_returns_contract`
- На prod `178.104.207.89` после деплоя и `systemctl --user restart hermes-web-backend-8791.service`:
  - `curl http://127.0.0.1:8791/api/health` вернул `status=ok`;
  - те же 2 теста прошли в боевом `.venv` через `./.venv/bin/python -m unittest ...` — `OK`.

Do not revisit without new data:
- К старому поведению, где `собери ... в csv` трактуется как попытка сделать файл из текста assistant-ответа.
- К схеме, где backend пропускает collection-requests напрямую в общий chat-path без фиксации source/subject/format/fields.

[2026-06-19] — Tender collection business prompt must be parsed as a complete collection contract

Context:
- Пользователь дал реальную постановку про выгрузку закупок с набора тендерных площадок, с формулировками `excel (csv)`, `по закупкам в части ИТ-деятельности` и многострочным блоком `Нужна информация:`.
- Живая проверка показала, что предыдущая версия route этот prompt не распознавала как collection-request: `looks_like_collection_request=false`, `subject=''`, `output_format=''`, `fields=[]`.

Decision:
- Такой prompt должен считаться complete collection contract без лишнего clarification.
- `excel` в business-формулировках нужно нормализовать в `csv` как рабочий spreadsheet-friendly structured output.
- Многострочный блок после `Нужна информация:` должен извлекаться как список полей результата.
- Формулировки вида `по закупкам в части ...` должны извлекать предмет сбора как `subject`.

Implemented:
- В `services/backend/app.py`:
  - `infer_collection_output_format()` расширен на `excel/эксел -> csv`;
  - `infer_collection_subject()` расширен на шаблоны `по закупкам в части ...`, `по закупкам в сфере ...`, `по закупкам по ...`;
  - `infer_collection_fields()` расширен на многострочный блок после `Нужна информация:`.
- В `services/backend/test_smoke.py` добавлен regression test `test_collection_request_with_real_tender_prompt_returns_contract`.

Verification:
- Локально: `python3 -m unittest -q test_smoke.HermesWebBackendSmokeTest.test_collection_request_with_real_tender_prompt_returns_contract` — сам тест `OK`.
- На prod `178.104.207.89`: после деплоя и `systemctl --user restart hermes-web-backend-8791.service` тест через боевой `.venv` тоже прошёл — `Ran 1 test ... OK`.
- На prod прямой runtime probe подтвердил итоговый контракт:
  - `source_kind=tenders`
  - `output_format=csv`
  - `subject=ИТ-деятельности`
  - `missing_fields=[]`
  - fields = 8 строк из блока `Нужна информация:`.

Do not revisit without new data:
- К старому выводу, что такой tender-prompt «слишком общий» и обязан уходить в clarification.
- К старому парсингу, где `excel (csv)` и многострочные поля не извлекаются.

[2026-06-19] — Collection requests must continue into executable downstreams, not stop at contract-only chat replies

Context:
- Пользователь отдельно потребовал убрать «вакуум» после `collection_contract` и довести контур до рабочего downstream.
- Для Telegram-каналов нужно, чтобы запросы не терялись в chat-логике, а шли через существующий `TG-API` с созданием отдельного списка каналов под задачу.
- Для тендеров в local-first контуре нужно хотя бы создавать отдельный source-list/task artifact с явным статусом активных и placeholder-источников, а не заканчиваться только текстовым контрактом.

Decision:
- `collection_request` после полного контракта больше не должен останавливаться на `chat:data_collection_contract`.
- Для `source_kind=telegram` обязательный downstream — `task-specific channel list` + live вызов `TG-API /export`.
- Для `source_kind=tenders` обязательный downstream — `task-specific tender source list` с честным `source_status` по локальному registry, без fake file export.

Implemented:
- В `services/backend/app.py` добавлены:
  - `source_items` и `since_date` в `collection_contract`;
  - `maybe_execute_collection_request()` как второй этап после контракта;
  - `materialize_telegram_task_config()` и `execute_telegram_collection_contract()`;
  - `materialize_tender_task_sources()` и `execute_tender_collection_contract()`.
- В `TG-API` task-config теперь создаётся как отдельный `channels_task_<...>.yml` рядом с `app.py`.
- На prod дополнительно доложен `/home/hermes/workspace/tenders/it_tender_sources.json`, потому что без него tender source matching был пустым.
- В `services/backend/test_smoke.py` добавлены регрессии:
  - `test_maybe_execute_collection_request_runs_telegram_api_with_task_channel_list`
  - `test_execute_tender_collection_contract_creates_task_source_list`

Verification:
- Локально: 3 целевых теста прошли (`tender contract`, `tender execution-plan`, `telegram task-channel-list`).
- На prod `178.104.207.89`:
  - backend на `8791` поднят и `/api/health` отвечает `200`;
  - live Telegram probe с реальными каналами `@b1_news`, `@Axenix_Ru` создал отдельный config `channels_task_...yml` и вернул `count=142` через `TG-API /export`;
  - live tender probe создал файл `/home/hermes/workspace/tenders/tasks/tender_sources_...json` и вернул `source_status`: active=`zakupki.gov.ru`, `B2B-Center`; placeholder=`Fabrikant`, `Bidzaar`, `Roseltorg`.

Do not revisit without new data:
- К старому поведению, где collection-request заканчивается только `collection_contract` без downstream execution/plan.
- К варианту, где Telegram collection живёт без отдельного task-specific channel list.
- К варианту, где tender source-status скрывает, какие источники реально активны, а какие пока placeholders.

[2026-06-19] — Prod 178 web collection requests with explicit URLs now continue into real artifact delivery

Context:
- Пользователь потребовал, чтобы запросы вида `собери информацию из источников в интернете и дай в таком-то виде` доходили до реального результата, а не оставались на уровне контракта.
- Для `telegram` и `tenders` downstream уже был частично доведён; не хватало универсального `web/url` execution path с реальным файлом.

Decision:
- Для `source_kind in {web, url, media}` backend должен после полного контракта сам:
  1) собрать страницы по URL,
  2) извлечь видимый текст,
  3) структурировать строки через Hermes API только по извлечённому контенту,
  4) сгенерировать `csv/json/xlsx`,
  5) отдать файл как message attachment через стандартный message-attachment route.
- Если контракт неполный, должен возвращаться честный `clarification_request`, а не fake file.

Implemented:
- В `services/backend/app.py` добавлены:
  - `extract_web_sources()`;
  - расширение `build_collection_contract_meta()` для `web/url/media` + обязательный `список URL / сайтов`;
  - `normalize_web_source_url()`, `html_to_visible_text()`, `fetch_web_source_document()`;
  - `build_web_collection_rows_prompt()` и `structure_web_collection_rows()`;
  - `build_collection_artifact_attachment()`;
  - `execute_web_collection_contract()`;
  - расширение `maybe_execute_collection_request()` на `web/url/media`;
  - нормализация attachments в `serialize_message()` с автогенерацией `download_url` вида `/api/messages/<id>/attachments/<index>`.
- В `services/backend/test_smoke.py` добавлены регрессии:
  - `test_execute_web_collection_contract_creates_real_csv_artifact`
  - `test_serialize_message_injects_attachment_download_url`

Verification:
- Локально: `python3 -m py_compile app.py test_smoke.py` и 4 целевых теста (`web artifact`, `attachment url`, `telegram`, `tender`) прошли `OK`.
- На prod `178.104.207.89`: те же 4 теста через боевой `.venv` прошли `OK`.
- Live HTTP verification на prod через реальный chat-flow:
  - неполный prompt с URL вернул честный `clarification_request` с `missing_fields=["что именно собирать"]`;
  - полный prompt `Собери данные с https://example.com и https://example.org в csv по теме example domains. Нужны поля title, summary` вернул `message_kind=collection_execution_result`;
  - создан attachment `collection_example-domains_20260619_143400.csv`;
  - download через `/api/messages/467/attachments/0?...` отдал реальный CSV со строками для `example.com` и `example.org`.

Do not revisit without new data:
- К старому состоянию, где `web/url` collection на prod останавливался на контракте без файла.
- К fake-export логике для explicit URL sources, когда реальный attachment не создаётся.
- К отдельному нестандартному download route для collection artifacts: использовать обычный message attachment flow.

[2026-06-20] — Live prod token-accounting verification requires backend restart because imported probe workers can fake freshness

Context:
- Пользователь попросил добить именно живую верификацию логирования токенов по реальному prod-user path.
- На `178.104.207.89:8791` код `attach_assistant_token_accounting()` уже лежал на диске, но публичный live ответ пользователя сначала приходил без `meta.token_accounting`.
- Отдельный probe, который импортировал `services/backend/app.py` напрямую на сервере, неожиданно видел `token_accounting`, но это было ложноположительное подтверждение.

Decision:
- Для live-проверки token-accounting нельзя импортировать `app.py` на prod без отключения chat processor: импорт сам стартует background worker и может обработать pending `chat_tasks` уже новым кодом, пока основной running service ещё старый.
- Истинным критерием считать только публичный user path через `http://178.104.207.89:8791/api`, а DB inspection делать отдельным off-process probe с `HERMES_WEB_CHAT_PROCESSOR_ENABLED=0`.
- Если публичный path не содержит `token_accounting`, а файл на диске уже содержит код, это rollout gap: нужен restart боевого `hermes-web-backend-8791.service`.

Implemented:
- Подтверждено расхождение между live public path и imported local probe:
  - public reply `assistant_id=574` содержал `usage`, но без `token_accounting`;
  - imported probe reply `assistant_id=568` содержал `token_accounting` и `timeout_seconds=180`, что выдало отдельный ad-hoc worker, а не основной prod service.
- Перезапущен боевой user-systemd backend `hermes-web-backend-8791.service` после server-side `py_compile services/backend/app.py services/backend/test_smoke.py`.
- После restart live public probe повторён по реальному user path.

Verification:
- До restart: public live reply `assistant_id=574` возвращал `downstream=hermes-api-server`, `usage={prompt_tokens: 16591, completion_tokens: 287, total_tokens: 16878}`, но `token_accounting=null`.
- После restart: public live reply `assistant_id=578` вернул `meta.token_accounting` с exact usage:
  - `prompt_tokens=16626`
  - `completion_tokens=294`
  - `total_tokens=16920`
  - `response_text_tokens_estimated=293`
  - `llm_usage_exact=true`
- Отдельная DB-проверка с `HERMES_WEB_CHAT_PROCESSOR_ENABLED=0` подтвердила, что `messages.meta_json` для `assistant_id=578` действительно хранит тот же `token_accounting`, а не только сериализует его в HTTP-ответе.

Do not revisit without new data:
- К live-верификации через импорт `app.py` без отключения chat processor: это может запускать ложного второго worker-а.
- К выводу «код на диске уже новый, значит prod уже обновлён»: для backend с in-memory workers это неверно без restart и public-path probe.

[2026-06-19] — Universal collection/composition contour must use one selected route, task-specific source manifests, and analog-backed proposal estimation

Context:
- Пользователь зафиксировал целевой класс задач шире простого web scraping: `источник -> обработка -> файл`, где источником может быть один файл, несколько файлов, API или открытый web, а итогом может быть не только dataset, но и проект КП / оценка стоимости / модель ресурсов.
- Отдельное требование — agent не должен путаться между route-ветками, игнорировать чёткую постановку или одновременно пытаться идти в несколько специальных путей.

Decision:
- Для data-driven запросов нужен единый universal pipeline: `intake/contract -> selected route -> task-specific source manifest -> raw ingest -> normalization -> analog search -> estimation/composition -> artifact delivery`.
- Верхний routing в chat backend должен оставаться взаимоисключающим: `collection_execution > collection_contract > message_export > dashboard > recurring_job > generic_chat`.
- Для proposal-like задач analog stage обязателен: при отсутствии прямых совпадений система должна использовать partial/component analogs и явно разделять факт, аналог и гипотезу.

Implemented:
- В проект добавлен документ `docs/UNIVERSAL_DATA_COLLECTION_AND_COMPOSITION.md` с единым алгоритмом для `attachment / attachments / api / web / telegram / tenders / mixed` и с фазами до proposal/cost/resource outputs.
- В `services/backend/app.py` расширено распознавание generic web-source формулировок (`интернете`, `веб...`) и subject extraction для конструкций вида `в csv по теме ... с полями ...`.
- В `services/backend/test_smoke.py` добавлены регрессии:
  - `test_process_chat_task_collection_route_preempts_dashboard_and_recurring`
  - `test_generic_web_collection_contract_does_not_require_explicit_urls`

Verified:
- Локально: `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` — OK.
- Локально: `python3 -m pytest services/backend/test_smoke.py -q -k 'collection_route_preempts_dashboard_and_recurring or generic_web_collection_contract_does_not_require_explicit_urls or execute_web_collection_contract_creates_real_csv_artifact or chat_research_request_does_not_create_recurring_job_without_explicit_schedule_intent or execute_tender_collection_contract_creates_task_source_list or maybe_execute_collection_request_runs_telegram_api_with_task_channel_list'` — `6 passed`.

Open questions:
- Full execution for `attachment/attachments` as first-class collection source is still not finished.
- Full arbitrary `api` collection executor with task-specific config manifest is still not finished.
- Analog corpus and cost/resource estimation layer for proposal drafting are designed, but not yet implemented end-to-end.

[2026-06-20] — Tender collection through prod-user must treat «настрой выгрузку» as real collection intent and must return a file even when some procurement sources time out

Context:
- При live-проверке через prod-user запрос на вчерашнюю тендерную выгрузку сначала не уходил в deterministic collection-path, хотя по смыслу это был ровно запрос на выгрузку.
- Корень №1: collection intent не срабатывал на формулировке «настроил/настрой выгрузку», а bare mention `csv` внутри длинного контракта не считалась output-format.
- Корень №2: tender pipeline падал целиком на timeout одного источника (`zakupki.gov.ru`) вместо partial-source tolerance, поэтому пользователь оставался без файла вообще.

Decision:
- Расширить collection-action routing на wording `настро*` и `организ*` для задач класса data collection.
- Считать bare mentions `csv/xlsx/json/xml` валидным output-format внутри collection contract даже без явной file-export фразы.
- Для tender contour сохранить принцип partial-source tolerance: timeout/ошибка одного источника не должна валить весь run, если можно отдать хотя бы пустой/частичный CSV плюс status CSV.
- Через prod-user deliverable считается выполненным только если backend реально возвращает attachment с выгрузкой, а не текстовый план.

Live verification:
- На prod `178.104.207.89` через прод-пользователя `admin@demo.local` повторно отправлен вчерашний tender prompt.
- После фикса backend вернул `message_kind=collection_execution_result`, `downstream=chat:tender_collection_result` и два реальных attachment-файла:
  - `it_tenders_2026-06-01.csv`
  - `tender_sources_status_2026-06-01.csv`
- Первый CSV скачан live по `download_url`, HTTP 200, файл реально существует и содержит header-строку выгрузки.
- Фактический результат по текущему локальному contour: `0` строк данных; активные источники — `zakupki.gov.ru`, `B2B-Center`; `zakupki.gov.ru` дал timeout как source error, `B2B-Center` вернул `0 строк`; placeholders остаются `Fabrikant`, `Bidzaar`, `Roseltorg`.

Implication:
- Корневой remaining issue по вчерашнему tender кейсу был не в file delivery, а в связке `collection intent phrasing + output-format detection + partial-source tolerance`.
- Теперь через prod-user система отдает реальный файл даже при пустом результате и отдельно показывает status CSV по источникам.

[2026-06-20] — Tender collection on prod must interpret `с 01.06.2026` as a range start, not as one exact publication day

Context:
- После доведения file delivery и partial-source tolerance prod-user path всё ещё возвращал формально успешный CSV, но с `0` строками.
- Живое воспроизведение показало, что запрос пользователя `нужны все закупки с 01.06.2026` ошибочно трактовался как `ровно 01.06.2026`, а не как диапазон `с 01.06.2026 по дату запуска`.
- На prod `zakupki.gov.ru` из контура `178` по-прежнему недоступен по timeout, но `B2B-Center` остаётся живым и даёт релевантные строки за диапазон. Поэтому ошибка именно в интерпретации периода напрямую обнуляла полезный результат для пользователя.

Decision:
- Для tender contour wording `с <date>` считать нижней границей периода, а верхней — датой текущего запуска, если пользователь явно не задал другую.
- Имена итоговых файлов и summary должны отражать диапазон (`since` + `until`), а не один день.
- Если один источник недоступен, но другой в том же диапазоне даёт строки, prod-user deliverable считается выполненным только при реальном непустом CSV attachment.

Implemented:
- В `/home/hermes/workspace/eva-github-backup/hermes-runtime/scripts/it_tender_pipeline.py` добавлены range-aware фильтры по дате для `zakupki.gov.ru` и `B2B-Center`, параметр `--until-date`, новый filename suffix `YYYY-MM-DD_YYYY-MM-DD` и summary с `since_date` / `until_date`.
- В `services/backend/app.py` `run_tender_pipeline_snapshot()` теперь передаёт в pipeline не один `--date`, а диапазон `--date` + `--until-date`; пользовательский reply показывает период `с ... по ...`.
- Skill `research/it-tender-csv-collection` обновлён: формулировка `с 01.06.2026` закреплена как range-start semantics; отдельно зафиксировано, что при недоступном `zakupki.gov.ru` run остаётся валидным, если `B2B-Center` дал строки и status CSV честно описывает недоступный источник.

Verification:
- Локально patched script дал непустой результат за диапазон `01.06.2026 — 20.06.2026`: `208` строк (`zakupki.gov.ru = 202`, `B2B-Center = 6`).
- На prod `178.104.207.89` direct pipeline run через backend `.venv` дал `6` строк (`B2B-Center = 6`, `zakupki.gov.ru = 0` из-за source timeout) и корректные файлы:
  - `it_tenders_2026-06-01_2026-06-20.csv`
  - `tender_sources_status_2026-06-01_2026-06-20.csv`
- Через временного prod-user live round-trip повторно отправлен вчерашний tender prompt. Backend вернул:
  - `message_kind=collection_execution_result`
  - `downstream=chat:tender_collection_result`
  - непустой main CSV attachment (`6` строк, HTTP 200)
  - отдельный status CSV attachment с честным `zakupki.gov.ru = ошибка источника`, `B2B-Center = собрано`
- После проверки временный prod-user и probe-thread'ы удалены с prod.

Do not revisit without new data:
- К старой трактовке `с 01.06.2026` как запроса на один календарный день.
- К варианту, где tender delivery считается успешным при `0` строках только потому, что файл технически приложился.

[2026-06-20] — Short complaint follow-ups on prod must not be blocked by empty request-policy envelopes

Context:
- При live-воспроизведении исходных пользовательских косяков на prod `178.104.207.89` были повторно прогнаны короткие follow-up паттерны: `где файл`, `непонятно`, `не работает`, плюс один и тот же weekly monitoring request в разных thread-ах.
- После предыдущих фиксов routing больше не путал one-shot collection с recurring monitoring, `where file` path отдавал реальное вложение, а duplicate recurring request не плодил второй job.
- Но обнаружился отдельный живой дефект recovery-path: короткая проблемная реплика `не работает` после короткого содержательного ответа всё ещё уходила в слишком общий LLM-ответ и подтягивала лишний контекст вроде названия thread-а.
- Корневая причина оказалась не в intent-detection, а в том, что runtime передавал `request_policy` как формально непустой dict с пустыми/default полями (`source_mode=''`, `model_preference='auto'`, пустые `explicit_source_ids` / `allowed_source_ids` / `connector_targets`). Из-за простого truthy-check это ошибочно отключало focused follow-up path.

Decision:
- Empty/default `request_policy` envelope должен трактоваться как отсутствие реального override и не должен отключать focused complaint-recovery path.
- Focused follow-up для коротких проблемных реплик должен включаться уже при наличии любого достаточно содержательного последнего assistant-ответа, не только длинного плана.

Implemented:
- В `services/backend/app.py` добавлен helper `request_policy_has_explicit_constraints()`.
- `build_hermes_system_prompt()` и `should_use_focused_followup_context()` переведены с простого `if request_policy` на проверку только реальных policy constraints.
- Для problem-followup lowered threshold: короткие реплики типа `не работает` / `непонятно` теперь могут использовать focused context и после короткого предыдущего ответа.
- В `services/backend/test_smoke.py` добавлена регрессия `test_should_use_focused_followup_context_for_problem_reply_after_short_answer`, включая вариант с пустым/default request_policy envelope.
- Skill `software-development/chat-runtime-reply-routing` обновлён: зафиксирован guard, что empty/default policy envelope не должен отключать short complaint recovery.

Verification:
- На prod `178.104.207.89` через боевой `.venv` прошли targeted tests:
  - `test_short_problem_followup_detection`
  - `test_should_use_focused_followup_context_for_short_problem_reply`
  - `test_should_use_focused_followup_context_for_problem_reply_after_short_answer`
- После деплоя и рестарта backend live probe подтвердил:
  - `не работает` больше не уходит в thread-title confusion;
  - `непонятно` и `не работает` получают `focused_followup_context=true` в message meta;
  - ответ явно опирается на предыдущий assistant plan и честно объясняет, что фактический запуск ещё не производился.
- Временный probe-user и созданные probe-thread/job после проверки удалены с prod, чтобы не оставлять мусор в рабочем контуре.

Do not revisit without new data:
- К старому truthy-check по `request_policy`, который считал пустой envelope реальным policy override.
- К варианту, где `не работает` после короткого предыдущего ответа уходит в generic LLM response и теряет рабочий контекст.

[2026-06-19] — Prod 178 universal collection contour now executes not only Telegram/tenders/explicit web, but also generic web-search, user attachments, and explicit API endpoints

Context:
- Пользователь отдельно дожал тему `источник -> обработка -> файл` и потребовал не оставлять universal collection contour на уровне документа/контракта.
- До этой доработки в runtime уже работали `telegram`, `tenders` и explicit `web/url`, но оставались реальные дыры: generic web without URLs, collection из приложенных файлов и explicit API endpoints.

Decision:
- Collection contour на prod 178 должен исполнять ещё три класса запросов:
  - generic `web` без явных URL через search-stage -> source manifest -> fetch -> artifact;
  - `attachment/attachments` через отдельный attachment bundle -> text extraction reuse -> artifact;
  - explicit `api` через task-specific API config -> live JSON fetch -> artifact.
- Верхний route-selection остаётся взаимоисключающим: collection-path не должен конкурировать с dashboard / recurring-job ветками.

Implemented:
- В `services/backend/app.py` добавлены:
  - `api` в `infer_collection_source()`;
  - `extract_attachment_source_items()` и fallback `infer_attachment_subject()`;
  - `materialize_web_search_task_sources()`, `search_web_source_candidates()`, `resolve_web_collection_sources()`;
  - `build_attachment_collection_documents()`, `materialize_attachment_task_bundle()`, `execute_attachment_collection_contract()`;
  - `fetch_api_source_payload()`, `normalize_api_payload_rows()`, `materialize_api_task_config()`, `execute_api_collection_contract()`;
  - расширение `build_collection_contract_meta()` и `maybe_execute_collection_request()` под `attachment` и `api`.
- В `services/backend/test_smoke.py` добавлены регрессии:
  - `test_execute_web_collection_contract_searches_sources_when_urls_not_provided`
  - `test_execute_attachment_collection_contract_creates_real_csv_artifact`
  - `test_execute_api_collection_contract_creates_real_csv_artifact`

Verified:
- Локально: `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` — OK.
- Локально: 8 целевых smoke-тестов прошли `OK`.
- На prod `178.104.207.89`:
  - файлы `app.py` и `test_smoke.py` скопированы в `/home/hermes/workspace/hermes-web-mvp-react-8793/services/backend/`;
  - `services/backend/.venv/bin/python -m py_compile ...` — OK;
  - `unittest` по 8 целевым проверкам — `OK`;
  - backend 8791 перезапущен через `scripts/runtime_env.sh` + waitress в корректном `hermes-api` env;
  - `/api/health` после перезапуска снова вернул prod-state: `mode=hermes-api`, `users_count=22`, `threads_count=70`.

Open questions:
- Proposal composition layer как end-to-end `requirements -> analogs -> cost/resource estimate -> project KP artifact` пока ещё не реализована.
- Generic API branch сейчас рассчитан на explicit JSON endpoints; connector-auth / arbitrary non-JSON APIs остаются отдельным следующим слоем.

[2026-06-19] — Proposal composition on prod 178 must trigger only on explicit КП / estimate intent, not on any awkward collection phrasing

Context:
- После добивки universal collection contour появилась новая зона риска: composition-layer для `КП / стоимость / ресурсы` не должен вызываться на обычных сборочных запросах, где `КП` встречается только как тема/поле, а не как явная команда подготовить proposal.
- На локальной регрессии это проявилось так: формулировка `в csv по теме проект КП ...` ошибочно включала composition-mode вместо обычного dataset-path.

Decision:
- Proposal composition должен запускаться только по явному intent, а не по одному упоминанию `КП` в теме.
- Явный trigger теперь требует action + explicit proposal phrase, например `подготовь КП`, `сформируй проект КП`, `коммерческое предложение`, либо явную оценку стоимости/ресурсов как отдельную задачу.
- Для explicit proposal-intent default output format должен быть `md`, и этот выбор должен иметь приоритет над generic message-export heuristics.

Implemented:
- В `services/backend/app.py` добавлены:
  - `infer_composition_mode()`;
  - `looks_like_proposal_composition_request()`;
  - `build_proposal_composition_prompt()`;
  - `compose_proposal_payload()`;
  - `render_proposal_markdown()`;
  - `build_proposal_artifact_attachment()`;
  - `maybe_attach_proposal_artifact()`.
- `build_collection_contract_meta()` теперь хранит `composition_mode` и `request_text`.
- `execute_web_collection_contract()`, `execute_attachment_collection_contract()`, `execute_api_collection_contract()` теперь умеют по explicit intent собирать composition artifact, а не только rows/file.
- Intent сужен так, чтобы голое `проект КП` в теме не запускало composition-layer.

Verified:
- Локально: `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` — OK.
- Локально: `7 passed` по целевым regression tests, включая guard against false trigger.
- На prod `178.104.207.89`:
  - `services/backend/.venv/bin/python -m py_compile ...` — OK;
  - `unittest` по 7 целевым проверкам — `OK`;
  - backend 8791 перезапущен в `hermes-api` env;
  - `/api/health` после перезапуска снова вернул `mode=hermes-api`, `users_count=22`, `threads_count=70`.

[2026-06-19] — Proposal composition completed as backend runtime + reusable skill layer; anti-hang check separated runtime health from test-process teardown noise

Context:
- Пользователь попросил добить proposal/cost/resource слой до более прикладного состояния, проверить на зависание после выкладки и отдельно прояснить, это backend-логика или skill.
- На этом этапе runtime уже умел dataset/file path и guarded proposal intent, но ещё не тащил ограничения запроса (`budget/timeline/team`) в composition artifact.

Decision:
- Финальная схема — гибрид:
  - backend — реальный routing/execution/runtime;
  - skill — повторно используемые правила, guard-ы и verification pattern.
- Не переносить executor-логику целиком в skill, чтобы не плодить второй движок рядом с backend.
- Для anti-hang считать главным критерием живость backend runtime после рестарта и под нагрузкой health/probe, а не только устойчивость отдельного unittest-процесса при teardown.

Implemented:
- В `services/backend/app.py` добавлены extraction helpers:
  - `infer_budget_hint()`;
  - `infer_timeline_hint()`;
  - `infer_team_constraints()`.
- `build_collection_contract_meta()` теперь хранит:
  - `budget_hint`;
  - `timeline_hint`;
  - `team_constraints`.
- Proposal composition prompt и markdown artifact теперь получают и отображают эти ограничения.
- Создан user skill `software-development/collection-proposal-routing` как слой правил поверх backend-runtime.

Verified:
- Локально:
  - `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` — OK;
  - `pytest` по 8 целевым проверкам — `8 passed`.
- На prod `178.104.207.89`:
  - `services/backend/.venv/bin/python -m py_compile ...` — OK;
  - `unittest` по 8 целевым проверкам — `OK`;
  - backend 8791 перезапущен в `hermes-api` env;
  - 20 подряд вызовов `/api/health` после рестарта — все `ok`, `mode=hermes-api`, `threads_count=70`.
- Отдельно зафиксировано:
  - повторный `unittest` в shell-loop дал `terminate called without an active exception` / `Aborted` уже после `Ran 1 test ... OK`;
  - при этом живой backend не упал: process остался активен, повторные `/api/health` продолжили возвращать `ok`.
  - Значит, это выглядит как teardown/runtime-noise отдельного test-process на сервере, а не как зависание или падение prod backend 8791.

[2026-06-19] — Repeated request classes should be captured as full skills, not rediscovered ad hoc from chat phrasing

Context:
- Пользователь указал на повторяющийся паттерн сбоев: когда запрос формулируется «как попало», система то уходит в хардкод под частный кейс, то теряет intent altogether.
- Особенно болезненные классы уже проявились на практике: file delivery / export, recurring monitoring, universal source->processing->artifact with proposal/composition branch.

Decision:
- Повторяющиеся классы задач больше не оставлять только как частные backend-фиксы или устные договорённости в чате.
- Для таких классов нужен явный skill-layer с полной процедурной формулировкой: triggers, route rules, anti-patterns, verification checklist, boundary between skill policy and backend execution.
- При этом runtime/executor-логика остаётся в backend; skill не должен становиться вторым скрытым движком.

Implemented:
- Обновлён user skill `collection-proposal-routing` до полноценного формата с metadata, route model, contract fields, failure patterns и verification checklist.
- Создан user skill `monitoring-request-routing` для loosely phrased recurring-monitoring requests: recurring intent, schedule/source extraction, anti-loss guard against `chat_task completed != job delivered`.
- Создан user skill `file-artifact-intent-routing` для запросов на файл/документ/export: file intent, deterministic export path, artifact-evidence contract.

Verified:
- Все три skills созданы/обновлены через `skill_manage` и повторно прочитаны через `skill_view`.
- Проверено, что у новых skills есть полноценный `SKILL.md` с usable content, а не пустой stub.

Open questions:
- Следующий слой — по мере накопления новых повторяющихся кейсов не плодить узкие skills на каждый баг, а держать компактный каталог skills по классам задач.

[2026-06-20] — Prod 178 Telegram export must serialize backend calls because TG API is single-threaded and overlapping exports destabilize user-path delivery

Context:
- Пользователь отдельно уточнил operational constraint: локальный TG API фактически однопоточный; пока предыдущая выгрузка не завершена, новый export-запрос может срываться или уходить в ошибку.
- Это хорошо совпало с уже воспроизведённым user-path симптомом: двухшаговый Telegram export (`запрос -> clarification -> конкретизация каналов`) раньше мог закончиться timeout/error even when routing was semantically correct.
- Нужно было чинить не только phrasing/contract, но и сам execution-path между backend 8791 и `TG-API /export`.

Decision:
- Для `source_kind=telegram` backend должен выполнять singleflight-сериализацию вызовов TG API: одновременно активен только один живой export-запрос в runtime-контуре.
- Если второй Telegram collection приходит, пока первый ещё не закончился, backend не должен слать второй параллельный `/export` в TG API; он должен дождаться освобождения singleflight-lock в пределах контролируемого timeout.
- В meta результата нужно явно оставлять след этой сериализации (`execution_lock.kind`, `wait_seconds`, `timeout_seconds`), чтобы дальше было видно, что runtime учёл однопоточность TG API.

Implemented:
- В `services/backend/app.py` добавлен backend-level singleflight lock для Telegram collection execution и timeout `HERMES_WEB_TELEGRAM_COLLECTION_LOCK_TIMEOUT`.
- `execute_telegram_collection_contract()` теперь:
  - ждёт освобождения Telegram singleflight lock;
  - только после этого вызывает `TG-API /export`;
  - пишет в result meta блок `execution_lock={kind=telegram_collection_singleflight,...}`.
- `normalize_public_error_text()` дополнен отдельным публичным текстом для случая, когда Telegram export не дождался окна выполнения.
- В `services/backend/test_smoke.py` добавлены регрессии:
  - `test_execute_telegram_collection_contract_waits_for_singleflight_lock`
  - `test_normalize_public_error_text_for_telegram_busy_timeout`

Verified:
- Локально:
  - `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` — OK.
  - 4 целевых теста (`telegram task-channel-list`, `telegram singleflight lock`, `telegram busy timeout text`, `dashboard output path`) — OK.
- На prod `178.104.207.89`:
  - обновлённые `app.py` и `test_smoke.py` скопированы в боевой проект;
  - `python -m py_compile services/backend/app.py services/backend/test_smoke.py` — OK;
  - те же 4 server-side `unittest` — OK.
- Live backend probe через реальный public API-path:
  - создан временный пользователь для smoke-проверки и потом удалён;
  - запрос `Собери данные из Telegram-каналов @b1_news, @Axenix_Ru по теме ИТ-консалтинг в csv ... с 19.06.2026` вернул `message_kind=collection_execution_result`, `downstream=chat:telegram_collection_result`, `count=5`, `processing_status=completed`.
  - в `meta` подтверждён `execution_lock.kind=telegram_collection_singleflight`, `wait_seconds=0.0`, `timeout_seconds=540`.
- Live two-step round-trip для исходного класса сценария:
  - шаг 1: `Выгрузи данные из ТГ по новым каналам с 15.06 в файл` -> честный `clarification_request` с `missing_fields=[список Telegram-каналов, что именно собирать]`;
  - шаг 2: конкретизация с каналами и полями -> успешный `collection_execution_result`, `count=37`, `processing_status=completed`, `config=task_ит-консалтинг_20260620_114930`, `since_date=2026-06-15`.

Do not revisit without new data:
- К прямым параллельным вызовам `TG-API /export` из backend без сериализации.
- К интерпретации TG export timeout как исключительно проблемы weak LLM: здесь root cause был operational/runtime.
- К user-path, где Telegram clarification-поток формально корректен, но execution срывается из-за overlap в однопоточном TG API.

[2026-06-19] — Chat routing phrase-rules moved from scattered backend hardcode into a declarative policy layer backed by skills

Context:
- Пользователь прямо потребовал две вещи одновременно: оформить повторяющиеся сценарии как полноценные skills и убрать phrase-level backend hardcode, который расползался вокруг collection / monitoring / file-export routing.
- Практический риск уже был подтверждён прежними сбоями: file delivery, weekly monitoring intent, proposal false-trigger и generic collection phrasing.

Decision:
- Правильный паттерн для повторяющихся request-классов — трёхслойный:
  - skill layer: правила, guardrails, verification;
  - policy layer: декларативные trigger/extraction rules в data-file;
  - backend runtime: execution, artifacts, jobs, attachments, delivery.
- Phrase-rules больше не должны жить как россыпь локальных regex прямо в backend-функциях, если это можно выразить через policy-file без изменения execution semantics.

Implemented:
- В backend-проект добавлен policy-file `services/backend/policies/chat_routing_policy.json` с секциями:
  - `message_export`;
  - `collection`;
  - `monitoring`.
- В `services/backend/app.py` backend переведён на загрузку routing-политик из этого policy-file для:
  - export/file intent markers и request patterns;
  - proposal / estimate trigger patterns;
  - collection action/data-target/source/subject/field extraction rules;
  - budget/timeline/team hint extraction;
  - recurring monitoring / schedule / follow-up patterns.
- Создан новый user skill `chat-request-routing-policy` и reference `references/policy-schema.md` как явный skill-layer для policy-driven routing.
- Обновлены skills `collection-proposal-routing`, `monitoring-request-routing`, `file-artifact-intent-routing`, чтобы они ссылались на policy-layer, а не только на backend behavior.

Verified:
- Локально: `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` — OK.
- Локально: `pytest` по целевому набору regressions для export / monitoring / collection / proposal / route-priority — `8 passed`.
- Отдельно поймана и исправлена регрессия policy-decoding в `field_trim_chars`, из-за которой `title/name` теряли первую букву; после фикса тот же regression set снова прошёл полностью.

Do not revisit without new data:
- К возврату phrase-rules обратно в хаотичные backend regex без policy-file.
- К модели, где skill и backend дублируют одну и ту же intent-логику разными словами.

[2026-06-19] — Policy-layer rollout to prod 178 verified the old routing/file/monitoring failure classes, but generic web search-stage still has no live candidates

Context:
- После локального refactor пользователь попросил не ограничиваться кодом и выкатить изменения на prod `178.104.207.89`, затем перепроверить именно те классы кейсов, которые раньше ломались.
- Целевой набор включал: false dashboard routing на словах `Telegram/интернет/аналитика`, recurring monitoring intent, file/export routing, universal collection routing, proposal false-trigger и проверку на зависание.

Implemented:
- На prod `178.104.207.89` обновлены:
  - `services/backend/app.py`;
  - `services/backend/test_smoke.py`;
  - `services/backend/policies/chat_routing_policy.json`.
- На сервере был досоздан каталог `services/backend/policies/`, которого раньше не было в live tree.
- Backend unit `hermes-web-backend-8791.service` (user-systemd) перезапущен после выкладки.

Verified:
- На prod compile прошёл: `services/backend/.venv/bin/python -m py_compile services/backend/app.py services/backend/test_smoke.py` — OK.
- На prod целевой regression set по `unittest` прошёл `13/13 OK` для кейсов:
  - research request не создаёт recurring job без явного schedule intent;
  - weekly media collection intent детектируется как recurring;
  - generic file request export path;
  - docx filename сам по себе не trigger;
  - fake structured export reject;
  - collection route preempts dashboard/recurring;
  - generic web contract without explicit URLs;
  - web-search source materialization path;
  - Telegram channel-list collection path;
  - tender collection path;
  - proposal false-trigger guard;
  - budget/timeline/team extraction;
  - explicit attachment -> proposal artifact path.
- Дополнительно на prod прошли ещё 2 targeted tests:
  - explicit dashboard intent required;
  - non-executable `Приступаю / Что я сделаю сейчас` strips for generic chat.
- Live round-trip через prod API подтвердил:
  - обычный текст с `Telegram, интернет, глубокая аналитика` больше не уходит в dashboard-route; ответ вернулся как обычный `downstream=hermes-api-server` без dashboard metadata;
  - фраза `Поставь еженедельный сбор информации из СМИ в чате` реально создаёт job (`message_kind=job_created`, `created_job_id=9`);
  - explicit web collection с `https://example.org` + `https://example.com` реально создаёт CSV artifact и возвращает `message_kind=collection_execution_result` с attachment.
- Anti-hang soak после rollout: 20 подряд вызовов `/api/health` вернули `status=ok`; backend после рестарта остался жив.

Open questions:
- Live generic web request без URL (`Собери информацию из источников в интернете ...`) на prod сейчас доходит до collection route, но падает на source-stage с `web_collection_sources_not_found`.
- Дополнительная runtime-диагностика показала, что `search_web_source_candidates(contract)` в live env возвращает `candidate_count=0`; это уже не routing-баг, а отдельный blocker search-stage / provider-availability на prod.
- Отдельный серверный шум `terminate called without an active exception` / `Segmentation fault` продолжает иногда появляться после завершённых `unittest`/off-process Python probes; на live backend runtime и health-check это не повлияло.

[2026-06-19] — Prod activity audit and generic web hardening on 178: routing fixed, search-stage stabilized, relevance still needs tightening

Context:
- Пользователь попросил одновременно добить хвосты и посмотреть, что реально происходит на prod, чтобы не плодить skills без подтверждённой пользы.
- На тот момент незакрытым оставался generic web collection без явных URL, а также не было фактической картины, какие сценарии на prod используются чаще всего и какие ошибки повторяются.

Prod activity snapshot:
- Всего пользователей: 22.
- Всего threads: 76, messages: 460, chat_tasks: 221.
- За 7 дней: active users by threads = 20, active users by messages = 17, создано 64 threads, 412 messages, 197 chat_tasks.
- Jobs: 8 всего, из них active = 4; за 14 дней job_runs = 1 success.
- Самые частые assistant message kinds за 14 дней:
  - `llm_or_unspecified` = 175;
  - `file_response` = 31;
  - `processing_status` = 28;
  - `job_created` = 4;
  - `dashboard_result` = 3;
  - `collection_execution_result` = 3.
- Самые заметные реальные error-классы за 14 дней:
  - `timed out` на file/export follow-up и длинных upstream-path;
  - `message_export_target_missing` на запросах вида `Собери файл / Отправь мне файл` без пригодного предыдущего ответа;
  - `telegram_analytics_source_missing` в старом false-trigger классе;
  - `web_collection_sources_not_found` на generic web без URL;
  - `llm_reply_blocked_by_postguard` в отдельных generic-chat кейсах.

Implemented:
- В `search_web_source_candidates(...)` добавлен fallback `DuckDuckGo HTML -> Bing HTML`, чтобы generic web search-stage не умирал от DDG bot challenge.
- Добавлено декодирование Bing redirect URLs (`u=a1...` -> real URL).
- В `execute_web_collection_contract(...)` добавлена partial-source tolerance: один `403/blocked` источник больше не валит весь сбор, если хотя бы один другой источник успешно скачался.
- В meta/reply добавлены `web_sources_skipped` и число пропущенных источников.
- Создан отдельный skill `software-development/web-source-search-stage-hardening` под класс generic-web source discovery / fallback / partial-source failures.

Verified:
- Локально: `py_compile` — OK.
- Локально: targeted `pytest` по fallback + partial-source tolerance + смежным collection regressions — `6 passed`.
- На prod 178: targeted `unittest` по двум новым web regressions — OK.
- После выкладки и рестарта backend health — OK.
- Live round-trip на prod для generic web без URL теперь завершается `message_kind=collection_execution_result` с реальным CSV attachment.

Important nuance:
- Технически generic web path теперь живой, но quality/relevance ещё не идеальна: Bing fallback может возвращать нерелевантные или сервисные страницы, и это уже не runtime outage, а качество source ranking/query formulation.
- По прод-активности не видно оснований создавать широкий новый зоопарк skills. Наиболее оправданным оказался только один новый skill: `web-source-search-stage-hardening`.
- Для остальных болевых зон уже достаточно существующих skills:
  - `artifact-delivery-contract-hardening`;
  - `scheduled-job-delivery-diagnostics`;
  - `chat-runtime-reply-routing`;
  - `monitoring-request-routing`;
  - `file-artifact-intent-routing`.

Do not revisit without new data:
- К идее, что generic web без URL можно считать полностью закрытым только по факту route-selection без live artifact.
- К созданию новых skills без подтверждённого повторяющегося failure class на prod.

[2026-06-19] — Generic web relevance hardening and explicit dashboard skill extraction

Context:
- После починки runtime-path `generic web without URL` пользователь попросил пойти дальше: улучшить качество найденных источников и отдельно оформить dashboard в явный skill, потому что технология и алгоритм уже есть, но в перечне он не читался как основной сценарий.

Implemented:
- В backend добавлены lightweight relevance heuristics для generic web search-stage:
  - low-value URL filtering до fetch (`privacy`, `terms`, `servicesagreement`, `help`, `validate`, и т.п.);
  - oversampling search results с последующей фильтрацией;
  - post-fetch relevance selection по subject/title/text/url;
  - сохранение runtime-устойчивости: partial-source tolerance не сломана.
- Создан новый основной skill `software-development/dashboard-request-routing`.
- Skill фиксирует отдельный dashboard contract:
  - explicit dashboard intent required;
  - routing split `dashboard / collection_then_dashboard / research_only / monitoring`;
  - local-first source policy;
  - stable dashboard envelope;
  - visual-first delivery contract;
  - anti-pattern guard против false dashboard trigger.

Verified:
- Локально: targeted regressions по search fallback / relevance filtering / partial-source tolerance — `5 passed` до известного teardown-noise.
- На prod 178: targeted `unittest` по новым relevance checks — OK.
- После выкладки backend health — OK.
- Live generic-web probe на prod после relevance-hardening по-прежнему создаёт реальный CSV attachment.

Important nuance:
- Runtime-only heuristics улучшили качество, но настоящий скачок качества дало не дальнейшее ужесточение HTML parser, а переключение generic web discovery на existing local-first Hermes CLI search contour с HTML fallback.
- На prod это потребовало отдельного исправления service env: `hermes` не был в PATH user-unit, поэтому backend надо было учить искать бинарь явно через `~/.local/bin/hermes` / `/home/hermes/.local/bin/hermes`.
- После этого live generic web request по `LegalAI` начал возвращать предметные URL и реальный CSV c 5 содержательными строками.

Do not revisit without new data:
- К предположению, что один только HTML SERP parser даст стабильно качественный research-grade source discovery для любых тем.
- К смешению dashboard skill с generic analytics prose или recurring monitoring logic.

[2026-06-19] — Prod user-signal audit: short complaint followups and recurring-job dedupe

Context:
- Пользователь попросил перестать ориентироваться только на формально зелёные логи и проверить именно пользовательские сигналы: `где файл`, `не работает`, `непонятно`, одинаковые сообщения в разных чатах и другие паттерны, где `chat_task` может считаться закрытым, а UX по факту сломан.
- Аудит на prod `178` снят из живой БД/рантайма через отдельный probe-скрипт, а не по ощущениям.

Observed on prod:
- За 30 дней: `236` chat-tasks, из них `205 completed` и `31 error`.
- Топ user-visible error classes:
  - `timed out` — `13`;
  - `telegram_analytics_source_missing` — `4`;
  - `message_export_target_missing` — `3`.
- Реальные пользовательские сигналы в БД подтвердили класс `file delivery mismatch`:
  - есть реальный follow-up `А где файл то?` после длинного apologetic assistant reply про повторную сборку документа;
  - есть повторы `Отправь мне файл`, `Отправь повторно файл пожалуйста`, `Так дай файл в docx`.
- В duplicate-audit найден отдельный operational failure class: один и тот же recurring monitoring request (`Поставь еженедельный сбор информации из СМИ в чате.`) повторялся в нескольких thread'ах, и prod уже содержал дубли активных monitoring jobs по сути одной и той же задачи.

Implemented:
- В backend добавлен новый runtime guard для short problem followups:
  - короткие реплики вроде `не работает`, `где файл`, `непонятно`, `повтори ещё раз` теперь распознаются как focused follow-up class;
  - для них строится суженный контекст из последнего содержательного user request + последнего содержательного assistant reply + текущей жалобы, вместо широкого повторного прогона всей истории.
- В export routing расширены implicit file-followup markers:
  - `А где файл?`, `где документ`, `не получил файл`, `повтори файл` и близкие формулировки теперь могут детерминированно переиспользовать предыдущий содержательный assistant answer и собрать export без лишнего LLM-круга.
- В recurring monitoring path добавлена duplicate protection across chats:
  - сравнение по `user_id`, normalized subject, `schedule_kind`, `days_of_week`, `time_of_day`, `timezone`;
  - при совпадении backend возвращает `job_reused` и не создаёт второй активный job-клон.
- Обновлены skills:
  - `chat-runtime-reply-routing` — зафиксирован отдельный класс short complaint followups;
  - `monitoring-request-routing` — добавлен guard против дублирования recurring jobs между чатами/threads.

Verified:
- Локально: targeted regressions по новым кейсам — `7 passed`.
- На prod `178`: targeted `unittest` по 5 кейсам — `OK`:
  - short problem followup detection;
  - focused follow-up routing for complaint reply;
  - implicit `где файл` export detection;
  - direct `where-file` export execution path without HTTP auth dependency;
  - recurring job dedupe across threads.
- Backend `8791` на `178` перезапущен после выкладки; `/api/health` снова `ok`, `mode=hermes-api`, `users_count=22`, `threads_count=101`, `jobs_count=15`.

Do not revisit without new data:
- К идее, что `completed chat_task` сам по себе означает нормальный пользовательский результат.
- К созданию нового recurring job по повторной формулировке того же monitoring request от того же пользователя без проверки существующего активного job.
- К возврату short complaint followups (`где файл`, `не работает`, `непонятно`) в generic broad-history LLM path, если backend уже знает последний содержательный контекст.
- К идее, что локальный Hermes CLI provider можно считать включённым на prod просто по факту его установки — нужно отдельно проверять PATH/runtime env user-service.

[2026-06-20] — Layered task-bundle routing for mixed user requests: classification/selection live-verified through prod-user path

Context:
- Пользователь зафиксировал архитектурную проблему: живые запросы почти всегда комбинированные (`собери + проанализируй + выдай файл`), и попытка свести их к одному intent ломает routing.
- Дополнительно пользователь попросил включить в модель отдельные смысловые компоненты `classification` и `selection / подбор`, но не как новые конкурирующие верхнеуровневые ветки, а как части analysis-stage внутри общего pipeline.
- Цель была не теоретическая: нужно было довести это до реального runtime-контура и прогнать сценарии именно в роли пользователя на prod `178.104.207.89`.

Decision:
- Для mixed user requests верхнеуровневым каркасом считать не один intent, а `task bundle` с жёсткими слоями:
  - `root_class`
  - `stages`
  - `source_kind`
  - `deliverable_kind`
  - `cadence`
  - `analysis_modes`
- `classification` и `selection` трактовать как `analysis_modes` внутри `data_pipeline`, а не как отдельные route-ветки, конкурирующие с collection/export/monitoring.
- Monitoring subject при явной формулировке в текущем сообщении (`по теме LegalAI`) брать прямо из current message, а не из fallback `отслеживай тему из текущего чата`.

Implemented:
- В `services/backend/policies/chat_routing_policy.json` расширены rules для mixed collection-analysis phrasing и subject extraction на связки вида `по теме ... , классифицируй / подбери / сравни ...`.
- В `services/backend/app.py` добавлены:
  - `infer_collection_analysis_modes(...)`
  - `build_collection_task_layers(...)`
  - передача `analysis_modes` + `task_layers` в collection contract/meta
  - расширенный `looks_like_collection_request(text, attachments)` для mixed analysis/file запросов по web и attachment path
  - использование explicit current-message subject в recurring monitoring path.
- В `services/backend/test_smoke.py` добавлены/обновлены регрессии на:
  - combined request `collect + classify + select + file`
  - attachment analysis request `проанализируй файлы + классифицируй + отдай csv`
  - recurring monitoring with explicit current-message subject.
- Skills обновлены:
  - `collection-proposal-routing` — зафиксированы `analysis_modes` и `task_layers`
  - `monitoring-request-routing` — зафиксирован приоритет explicit subject из current message.

Verified:
- Локально: `py_compile` — OK.
- Локально: targeted `unittest` по 4 новым/связанным кейсам — `OK`.
- На prod `178` backend выкачан и перезапущен в canonical runtime env; `/api/health` = `ok`.
- Live probe через временного prod-user `layer-live-20260620@demo.local` подтвердил:
  - combined web request `собери + классифицируй + подбери + csv` -> `message_kind=collection_execution_result`, `downstream=chat:web_collection_result`, real CSV attachment, HTTP 200;
  - contract/meta содержит `root_class=data_pipeline`, `stages=[acquisition, analysis, delivery]`, `analysis_modes=[classification, selection, comparison]`;
  - follow-up `А где файл?` -> `message_kind=file_response`, attachment реально возвращён;
  - first recurring request `Поставь еженедельный мониторинг ... по теме LegalAI` -> `job_created` с subject `LegalAI`;
  - повтор того же monitoring request в другом thread -> `job_reused`, дубликат не создан.

Implication:
- Для текущего живого контура устойчивее не пытаться заранее придумать все task classes, а удерживать ограниченный набор execution-каркасов и наращивать только analysis modifiers внутри них.
- `classification` и `selection` уже можно считать не «идеей на будущее», а live-проверенным analysis layer внутри `data_pipeline`.

Do not revisit without new data:
- К модели, где `classification` и `selection` оформляются как отдельные competing top-level routes рядом с collection/export/monitoring.
- К fallback subject `отслеживай тему из текущего чата`, если текущий monitoring request уже содержит явную тему.

[2026-06-20] — Explicit external dashboard requests should bypass local clarification and go straight to web dashboard path

Context:
- После cleanup осталось одно повторяемое UX-замечание: запрос вида `Собери из интернета данные по рынку LegalAI и дай дашборд` в local-first policy всё ещё уходил в `clarification_request`, хотя пользователь уже явно выбрал внешний источник.
- Это был уже не runtime-crash, а routing/UX хвост: backend сначала строил local dashboard clarification, а внешний web dashboard path не включался автоматически при явном `из интернета`.
- Отдельно учтено ограничение prod-контура: live UI login через текущие известные demo-учётки не подтвердился, поэтому финальная живая верификация делалась через server-side smoke в canonical runtime env и health-check боевого backend-процесса.

Decision:
- Для dashboard-запросов с явным external-source intent (`из интернета`, `по открытым источникам`, `внешний обзор`, URL и близкие маркеры) backend не должен сперва требовать локальное уточнение.
- Если общий dashboard route уже выбран, глобальный источник доступен, а local-first ветка вернула только `clarification_request`, при явном external intent нужно сразу переключаться в `build_global_dashboard_reply(...)`.
- `local_only` policy при этом не трогать: она должна по-прежнему честно блокировать global fallback и отдавать clarification.

Implemented:
- В `services/backend/app.py` добавлен helper `dashboard_request_prefers_global_sources(text)`.
- В `maybe_build_dashboard_reply(...)` добавлен guard: если local-first local reply = `clarification_request`, но текст явно просит внешний сбор, backend сразу идёт в global `web_research` dashboard path.
- В `services/backend/test_smoke.py` добавлена регрессия на запрос без explicit `source_mode`, но с формулировкой `Собери из интернета данные ... и дай дашборд`, который теперь обязан возвращать `dashboard_result`, а не clarification.

Verified:
- Локально: `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` — OK.
- Локально: `python3 -m pytest services/backend/test_smoke.py -q -k 'global_only_dashboard or internet_dashboard or local_only_dashboard or dashboard_result_for_dashboard_output or collection_route_preempts_dashboard_and_recurring'` — `2 passed`.
- На prod `178`: обновлённые `app.py` и `test_smoke.py` выложены в `/home/hermes/workspace/hermes-web-mvp-react-8793/services/backend/`.
- На prod `178`: targeted `unittest` в canonical env через `bash scripts/runtime_env.sh ...` по связанным кейсам (`is_dashboard_request`, `dashboard output`, `collection route priority`) — OK.
- Боевой backend `8791` после выкладки живой: `/api/health` вернул `status=ok`, `mode=hermes-api`, `users_count=24`, `threads_count=154`, `jobs_count=18`.

Open questions:
- Отдельно стоит позже добить product-level path для live UI login/smoke под технической учёткой, чтобы финальные acceptance-проходы меньше зависели от ручного поиска валидного пользователя на prod.

Do not revisit without new data:
- К поведению, где явный запрос `из интернета ... дай дашборд` сначала уходит в локальное уточнение только потому, что policy по умолчанию `local_first`.
- К попытке лечить этот кейс через ещё один phrase-level special route вне общего dashboard-flow: фикс должен жить внутри существующего policy-switch в `maybe_build_dashboard_reply(...)`.

[2026-06-20] — Live cleanup pass: market-subject routing fixed and Telegram export now returns a real file in UI

Context:
- После live user-smoke стало видно, что один и тот же запрос `Собери из интернета данные по рынку LegalAI и дай дашборд` в старых thread'ах ещё мог уходить в `clarification_request`, хотя более поздние прогоны уже проходили.
- Параллельно вскрылся отдельный продуктовый хвост по Telegram-сценарию: backend честно запускал TG API и отдавал статус, но не прикладывал реальный файл выгрузки обратно в chat/UI.
- Пользовательский приоритет был не в новых архитектурных развилках, а в добивке живых кейсов до рабочего состояния в prod-контуре `178`.

Agreed:
- Формулировки вида `по рынку X` должны считаться валидным subject extraction path для collection/dashboard запросов, а не приводить к `missing_fields`.
- Telegram collection path должен завершаться не только текстовым подтверждением, но и реальным attachment-файлом, если запрос просит `csv/xlsx/json`.
- Для TG path сохраняется backend-level singleflight: новый export не должен стартовать, пока не завершён предыдущий вызов к однопоточному TG API.

Implemented:
- В `services/backend/policies/chat_routing_policy.json` расширены `subject_patterns`:
  - добавлен path `по рынку ...`;
  - добавлены stop-markers для `дай дашборд` / `построй дашборд`, чтобы subject не захватывал хвост action-фразы.
- В `services/backend/test_smoke.py` добавлена жёсткая регрессия: запрос `Собери из интернета данные по рынку LegalAI и дай дашборд.` должен давать `subject=LegalAI`, `output_format=dashboard`, `source_kind=web`, без `missing_fields`.
- В `services/backend/app.py` добавлена нормализация Telegram rows и generation реального collection attachment из ответа TG API.
- В `services/backend/test_smoke.py` обновлён Telegram smoke: теперь проверяется не только вызов API и singleflight lock, но и наличие реального CSV attachment.
- Локальные правки выкачены на prod `178`, backend `8791` перезапущен в canonical env через `../../scripts/runtime_env.sh`.

Verified:
- Локально: `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py` — OK.
- Локально: targeted `pytest -k 'telegram_collection or dashboard_output or internet_dashboard'` — `2 passed`.
- На prod `178`: targeted `unittest` по dashboard subject extraction и Telegram collection attachment — OK.
- На prod `178`: backend `8791` после рестарта живой, `/api/health` вернул `status=ok`, `mode=hermes-api`, `threads_count=160`, `users_count=25`.
- Live user-path через UI подтверждён:
  - новый chat с запросом `Собери из интернета данные по рынку LegalAI и дай дашборд.` завершился `dashboard_result`, без clarification;
  - новый chat с запросом `Собери данные из Telegram-каналов @b1_news, @Axenix_Ru ...` вернул assistant message с реальным UI attachment `collection_ит-консалтинг_*.csv`.
- Direct prod probe подтвердил analysis-layer path:
  - combined request `собери + классифицируй + подбери + csv` завершился `collection_execution_result` с реальным CSV attachment;
  - follow-up `Проанализируй предыдущий файл...` отработал как нормальный ответ по данным собранного файла.

Open questions:
- Отдельно стоит позже ужесточить message/meta contract для обычных аналитических follow-up ответов: сейчас часть из них приходит без специального `message_kind`, хотя по content/path работают корректно.
- Полноценный live upload-case `пользователь загружает свой файл через UI -> агент анализирует файл` всё ещё лучше перепроверить отдельным прогоном, когда понадобится именно attachment-from-user contour.

Update 2026-06-20 13:53 UTC:
- Первый хвост закрыт: generic LLM follow-up ответы теперь получают `message_kind=chat_response` через `enrich_assistant_meta(...)`, а не остаются без типа.
- Проверка на prod `178` подтверждена live probe в thread `184`: follow-up `Проанализируй предыдущий файл...` завершился `chat_response`, с заполненным `token_accounting` и без зависания в `processing_status`.
- Второй хвост тоже закрыт на runtime-уровне: attachment-from-user contour проверен direct prod probe — upload запроса `Собери из этих файлов csv...` завершился `collection_execution_result` с реальным CSV attachment `collection_note-txt_20260620_135124.csv`.

Do not revisit without new data:
- К модели, где TG export считается «закрытым», если в чате есть только текст `Сообщений получено: N`, но нет реального файла.
- К subject extraction, где `по рынку X и дай дашборд` снова разваливается на `subject=X и дай дашборд`.
