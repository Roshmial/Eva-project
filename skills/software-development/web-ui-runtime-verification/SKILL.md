---
name: web-ui-runtime-verification
description: Проверка и доведение local-first web UI по живому runtime, а не только по коду — для задач, где важно подтвердить реальные пользовательские потоки, читаемость и поведение интерфейса.
---

# Когда использовать

См. также:
- `references/hermes-web-acceptance-pitfalls.md` — pitfalls для случаев, когда runtime уже зелёный, а acceptance остаётся хрупким из-за onboarding modal, устаревших smoke-ожиданий, неверных demo-учёток или слишком жёстких мгновенных assertions.
- `references/live-user-smoke-auth-and-runtime-notes.md` — практические заметки для случаев, когда server-side smoke зелёный, а повторная проверка именно через пользователя расходится из-за live DSN/runtime/auth path.
- `references/file-delivery-and-runtime-acceptance.md` — как доводить UI/file-delivery сценарии до реально подтверждённого результата: не останавливаться на `task completed`, проверять attachment в message meta и в самом UI, и отличать старые thread'ы до фикса от новых post-fix прогонов.
- `references/chat-task-tail-closure.md` — как добивать последние acceptance-хвосты: выставлять terminal `message_kind` для generic follow-up ответов, проверять upload-driven artifact flow до реального файла и правильно патчить LLM-вызов в backend smoke-тестах до `POST /messages`.
- Live contour with frontend proxy to remote backend: before declaring a UI fix done, verify where `/api` really goes (`VITE_API_BASE_URL`, reverse-proxy config, `HERMES_WEB_FRONTEND_BACKEND_BASE`, process env). Patch and restart that real backend contour, not only the local code copy.
- For admin/settings screens that "save" but visually revert, run a full round-trip on the real backend target: GET current state -> PATCH intended change -> inspect PATCH response -> verify follow-up GET/hydration payload.
- Session/auth acceptance is a separate check from JS-console cleanliness: a live UI can show `Сессия истекла. Войдите снова.` even when browser console is clean. Verify `/api/auth/login`, `/api/me`, stored token/cookie, and whether the frontend points at the runtime you actually patched.
- If UI auth smoke still fails after user creation, verify the live backend storage target before changing passwords again: inspect DSN/driver/env of the running process and make sure you are editing the same database that live `/api/auth/login` uses.
- Do not assume `runtime_env.sh <command>` actually executes the command in the intended runtime. For this contour, prefer `source .../runtime_env.sh && <command>` (or `source ... && exec <command>`) so restart/verification commands really inherit the live env.

- If a user reports a mobile "blank white screen" after a click, treat it first as a likely full React render crash, not as an empty dataset or a normal loading state. A screenshot with no header, no loader, no banner, and no partial content is evidence that the whole tree failed to render.
- For modal-trigger regressions on live UI, verify both data readiness and mount-time handler wiring. A common failure mode is fixing the async preload race but leaving the modal mounted with an undefined callback/prop reference; the click then flips `open=true` and the entire screen whites out on render.
- After rebuilding a live frontend contour, verify the actually served asset hash from the live `index.html` and confirm the new JS file is reachable over HTTP. Do not assume a successful `vite build` means the contour is already serving the new bundle.

- For suspected false postguard failures, replay the exact failing thread/message in the live service environment, not in a clean shell import. Load env from the actual backend process (`/proc/<pid>/environ`) or run inside the same service contour; otherwise ad-hoc imports may fall back to mock mode and give a false diagnosis.
- A durable false-positive pattern: repeated structural section lines in a valid answer (for example repeated `Что делаем:` blocks in a service catalog) can trip naive duplicate-line guards. When fixing this class of bug, narrow the heuristic to ignore benign repeated headings and markdown separators, then re-run the real thread to verify the guard no longer blocks the answer.


## Быстрый check-list для policy / settings регрессий

Если policy- или settings-экран выглядит так, будто «всё включено», toggle не держится, или выбор по умолчанию не переживает reload, сначала проверь не backend persistence вообще, а следующие frontend-классы ошибок:

1. Нормализация bootstrap/GET payload:
   - не подставляй оптимистические UI-defaults вроде `enabled=true`, если backend поле не прислал явно;
   - для allow-list semantics enabled-state должен выводиться из authoritative membership, а не из удобного frontend fallback.

2. Draft clone / hydration drift:
   - draft clone обязан переносить все поля round-trip редактирования: nested maps, default selections, notes, connector assignments;
   - если поле потерялось именно в clone-слое, экран будет выглядеть рабочим, но редактировать синтетический default, а не реальное runtime state.

3. Mixed value spaces inside one control group:
   - checkbox, select, label и save payload должны жить в одном canonical contract;
   - нельзя в одной части UI использовать group keys, а в другой `source_key` или display key как fallback — это даёт ложное ощущение сохранения.

4. Save payload completeness:
   - если backend опирается и на aggregate structure, и на override map, при сохранении отправляй обе формы, а не только одну «удобную» frontend-структуру;
   - сверяй PATCH payload с live backend contract, а не только с тем, что лежит в draft state.

Этот паттерн особенно важен для admin/policy экранов Hermes Web и похожих local-first UI, где один и тот же state проходит через bootstrap → normalize → draft clone → PATCH payload → reload.

- `references/duckdb-user-row-corruption-after-login.md` — как отличать auth/boot defect от точечной порчи user-row в DuckDB, когда login проходит, а почти все protected reads отвечают `503 auth_backend_temporarily_unavailable`.
- `references/duckdb-concurrency-and-flaky-react-smoke.md` — как разделять реальный backend concurrency defect на DuckDB и отдельную хрупкость длинного React smoke, если live targeted probes уже подтверждают рабочий contour.
- `references/react-acceptance-stabilization-and-doc-closeout.md` — как стабилизировать длинный React smoke через реальные tab-click paths, а после зелёного прогона сразу перевести backlog/docs из режима defect в режим hardening.
- `references/runtime-error-fallback-and-remote-user-systemd.md` — как принимать backend/runtime-правки, где одновременно важны узкий fallback по LLM-модели, безопасный public error path без HTML-полотен и корректное управление удалёнными `systemd --user` unit'ами.
- `references/frontend-proxy-admin-doc-upload-guard.md` — split-contour приёмка для случаев, где фронтовый `/api` proxy должен ходить в отдельный backend, admin-вкладка падает на runtime wiring, document extraction теряет таблицы/headers, а LLM-ответы нужно фильтровать post-guard'ом.

Используй навык, когда нужно:
- проверить, что UI-правки реально видны в браузере, а не только присутствуют в файлах;
- разбирать жалобы вида «в коде исправлено, а на экране нет»;
- доводить local-first web MVP без новой инфраструктуры;
- принимать admin/policy-экраны, где важно отдельно доказать backend-контракт и живой UI round-trip.

См. также `references/admin-policy-hydration-acceptance.md` — паттерн приёмки экранов, где форма появляется раньше, чем гидратируются данные.
См. также `references/mixed-contour-and-zero-server-handoff.md` — как не принять смешанный frontend/backend contour за готовый runtime и что обязательно передавать в deploy-пакете для нового пустого Hermes-сервера.
- отделять продуктовый UX-дефект от дефекта startup/runtime/auth boot;
- проверять чаты, списки, unread, jobs, админку и другие stateful экраны.

# Основной принцип

Нельзя считать UI-задачу закрытой только потому, что патч записан в файл. Для этого класса задач критерием завершения является живой runtime: страница открывается, логин проходит, экран рендерится, пользовательский поток воспроизводится, визуально спорные элементы читаемы и ведут себя как ожидалось.

# Базовый порядок работы

1. Сначала зафиксируй конкретные пользовательские симптомы.
- Что именно пользователь видит не так.
- Это про внешний вид, состояние, прокрутку, данные, навигацию или права.
- Какие элементы особенно важны для приёмки.

2. Проверь код, но не делай из этого вывод о завершении.
- Найди точки в frontend и backend.
- Отдельно выпиши: что уже изменено, что ещё нет, что только гипотеза.

3. Подними живой runtime и проверь правильную поверхность.
- Убедись, что открыт именно frontend, а не backend JSON endpoint.
- Для local-first контуров отдельно проверь, какой URL реально обслуживает UI.
- Если нужен временный static serve frontend для диагностики, это допустимо как QA-путь, но не как финальное доказательство продуктовой готовности.
- До разбора симптомов сделай короткий sanity-pass на «косяки контура», а не только на сам баг. Минимальный набор для split/prod-сценария:
  - какой код реально запущен на целевом порту;
  - совпадает ли deploy-файл с рабочим деревом по `sha256`/размеру/хотя бы line count;
  - какой storage/backend-driver реально используется в runtime;
  - нет ли признаков legacy-контура в логах (`duckdb`, старый DB path, старый `service mode`, неожиданный cwd).
- Если это не проверить сразу, легко потратить лишний круг на симптомы вроде CORS, login или layout, хотя первопричина — старый backend/frontend с тем же именем сервиса.

4. Проверь auth/startup отдельно от бизнес-экранов.
- Если логин не переводит на app shell, сначала локализуй auth boot.
- Проверяй по отдельности: session, profile, bootstrap, threads, files, jobs meta.
- Если поштучные запросы работают, а общий boot падает, ищи проблему в пакетной инициализации, Promise.all, парсинге ответов или гонке состояния.
- Отдельно проверяй класс симптома `login = 200`, но почти все auth-protected read-endpoint'ы (`/me`, `/bootstrap`, `/files`, `/threads`, `/jobs/meta`) сразу дают одинаковый `503 auth_backend_temporarily_unavailable`. Для local-first DuckDB это не только auth/boot-path баг: сначала сделай прямые SQL-probes по `users` и `sessions join users` именно для текущего user_id. Если чтение конкретной строки пользователя или join падает на `Corrupt database file: computed checksum ...`, root cause в data corruption, а не во frontend. В таком случае не лечи boot-path вслепую: сначала сделай backup `.duckdb`, затем собирай repaired DB и точечно пересобирай повреждённую строку/блок, после чего заново прогоняй live login acceptance.

- Для chat UX обязательно проверяй реальные инварианты.
- Откуда открывается чат: сверху или снизу.
- Прокручивается ли лента после отправки.
- Не залипают ли информационные плашки при прокрутке.
- Читаемы ли служебные статусы файлов и OCR/извлечения текста.
- Не меняются ли названия чатов динамически, если пользователь просил стабильность.
- Если жалоба про composer звучит как `поле ввода не растёт` или `между последним сообщением и вводом пустота`, не ограничивайся CSS-правкой `textarea`. Для messenger-like composer сначала разделяй два слоя:
  - autosize-mechanics: CSS-only `height:auto`/`max-height` может выглядеть правильно в коде, но не давать фактического роста. Надёжный repair-path — `ref` на textarea + effect/handler, который на каждом изменении делает `style.height='auto'`, затем ставит высоту по `scrollHeight` с верхним лимитом;
  - bottom-spacing-mechanics: пустоту под сообщениями часто создаёт не один элемент, а комбинация `messages-panel padding-bottom`, `workspace gap` и `margin-top:auto` у нижних hint/placeholder-блоков.
- Для такого класса дефекта приёмка должна подтвердить обе вещи отдельно: (1) textarea реально увеличивается по мере ввода нескольких строк; (2) последний message/hint визуально подходит к composer без искусственного нижнего провала.

- Для jobs проверяй не только список, но и весь вертикальный срез.
- list;
- detail;
- run;
- Для multi-recipient/collaborative jobs отдельно проверяй delivery semantics: у владельца и у добавленного `fixed_user` должны материализоваться разные `thread.id` для одного `job_id`, если продуктовый контракт обещает отдельный чат на получателя.
- Для cron/job acceptance проверяй не только `job_runs`, но и фактический delivered message в recipient thread: технический хвост (`llm_route`, `downstream`, `request_policy`, `personalization_preview`, `route` / `Маршрут` и похожие служебные поля) может быть вычищен из summary, но всё ещё просочиться в доставленное сообщение.
- Если acceptance-логика для live backend становится длинной (временный admin, временный recipient, временный job, manual run, проверка `/threads`, cleanup), не пытайся держать её в тяжёлом nested SSH heredoc. Надёжнее записать локальный verification script, скопировать его на remote host и выполнить там через runtime venv, затем удалить тестовые сущности.
- pause/resume;
- read-only/editable состояние;
- честное отображение источника данных.
- если пользователь просит упростить точечные действия вроде `Добавить получателей` или `Добавить доступ`, не прячь их за полное `Открыть настройки` / edit modal. Для jobs это отдельный UX-инвариант: быстрые вторичные действия должны открывать узкий picker только для своей сущности, а полная форма задачи — оставаться отдельным сценарием.
- если спор про визуальный размер кнопок или карточек пользователей, не ограничивайся формулировкой `стало компактнее`. Снимай DOM-метрики через `getBoundingClientRect()` хотя бы для кнопок detail-экрана и первых карточек picker-а. Это защищает от ложного вывода, когда CSS-класс уже поменялся, но live кнопка всё ещё имеет высоту порядка 80+ px и пользовательская жалоба остаётся справедливой.
- если проверяешь self-subscribe или другой дополнительный путь доставки, разделяй два инварианта:

  - delivery/thread semantics: появляется ли нужный `job`-thread, входит ли пользователь в фактических recipients и что именно запускает lifecycle thread-а.
- Не считай успешный `subscribe` доказательством полной готовности. У jobs может отдельно жить логика прав и отдельно — логика materialization получателей/чатов.
- Для спорных случаев проверь, является ли нужный `recipient_type` частью продуктовой модели. Типичный скрытый разрыв: пользователь формально подписался, запись в subscriptions появилась, но job-thread не создаётся, потому что задача не включает канал `subscribers` в `job_recipients`.
- Если self-subscribe задуман как самостоятельный пользовательский контур, отдельно проверь, участвуют ли `job_subscriptions` в расчёте фактических recipient user ids и lifecycle `job`-thread'ов даже без явного `recipient_type = subscribers`. Иначе можно ложно принять feature по `200 subscribed`, хотя отдельный job-чат так и не материализуется.

- Для tabbed admin UI проверяй вкладки по одной, а не пачкой.
- Кликни конкретную вкладку.
- Сними новый snapshot или проверь DOM/console именно после этого клика.
- Только потом переходи к следующей вкладке.
- Если быстро переключить несколько вкладок подряд, легко получить ложное ощущение, что «всё проверено», хотя финальный snapshot отражает только последнюю активную панель.
- Не угадывай признаки активной вкладки: сначала прочитай реальные классы и селекторы в frontend-коде. В этом классе UI активная admin-вкладка отмечалась не `active`, а парой `primary/ghost`, а панель скрывалась не через общий `hidden`, а через кастомный `admin-panel-hidden`.
- Если snapshot визуально «не меняется», не делай вывод о поломке сразу. Проверь состояние через DOM: какая кнопка получила активный класс, какие панели имеют `display:none` / скрывающий класс, и что лежит в `state.adminSection`.
- Для admin overview с selector-based фильтрами/агрегациями проверяй три уровня отдельно: значение control, обновление `state`, и фактический DOM-текст/график после перерендера. Возможен промежуточный ложный сигнал, когда `select.value` и `state.admin.overviewTimeseries.granularity` уже переключились, а видимый chart-text ещё старый. В таком случае не объявляй feature сломанной или починенной по одному признаку: принудительно вызови тот же refresh-путь, который использует экран (`refreshAdmin()` или эквивалент), и только потом снимай финальный snapshot приёмки.
- Если пользовательский симптом звучит как «подписи не обновляются сразу, пока не дёрнешь общий refresh», считай это отдельным UI-state дефектом, а не просто задержкой данных. Практический паттерн ремонта: вынеси загрузку selector-зависимых данных в отдельный helper, при `change` сначала сразу обнови `state` выбранным значением, очисти старые buckets/labels и сделай немедленный `render...()` для честного DOM, а уже затем подставь результат fetch. Проверяй live runtime в два шага: (1) immediate DOM после события `change` — правильная подпись режима без устаревших labels; (2) settled DOM после завершения fetch — уже с реальными labels/точками графика.
- Если пользователь просит сделать админку «аналитикой, а не складом счётчиков», не начинай с косметики карточек. Сначала выпиши, какие показатели реально являются продуктовой или operational-аналитикой, а какие — внутренний шум. Для этого класса задач отдельный анти-паттерн — держать в overview KPI вроде количества сессий только потому, что это легко посчитать. Перед фронтовой полировкой зафиксируй whitelist полезных сигналов и blacklist метрик, которые пользователь уже отверг.
- Для security/admin доработок иди backend-first. Если UI обещает TTL сессий, смену пароля, отзыв старых сессий, фильтр логов или экспорт, сначала усили backend-инварианты и существующие endpoints, а уже потом добавляй формы и кнопки. Иначе легко сделать декоративный frontend, который выглядит готовым, но не подкреплён реальным lifecycle и правами.
- Для admin logs/operations сначала расширяй существующий endpoint, а не строй новый параллельный контур. Практический паттерн: добавить фильтры `date_from/date_to/limit` и `export=csv|json` в уже существующий `/admin/events`-подобный route, а затем подвязать UI. Это уменьшает дублирование и ускоряет live-проверку.
- Если успела изменить backend и HTML-каркас, но не довела JS wiring или live smoke, не маркируй задачу как почти завершённую одним числом. В промежуточном отчёте разделяй минимум три уровня: (1) backend-инварианты уже реально изменены; (2) markup/DOM hooks уже добавлены; (3) frontend handlers и runtime-верификация ещё не подтверждены. Для длинных local-first UI задач это защищает от ложного «осталось чуть-чуть», когда на самом деле ещё не доказан ни один пользовательский поток.
- Для экранов с контекстной topbar-плашкой не проверяй её на любой вкладке по инерции. Сначала вернись именно на тот экран, где она должна существовать по продуктовой логике. В этом контуре `#topbarChatGuide` корректно виден на `Чаты` и закономерно скрыт на `Управление`; проверка «плашка пропала» вне вкладки `Чаты` даёт ложный дефект.
- Если нужно проверить UI-состояние из `browser_console`, не предполагай, что глобальный state лежит на `window.state`. В этом контуре рабочая переменная была доступна как `state`, а `window.state` мог быть `undefined`, что давало ложные ошибки в диагностике.
- Если browser-click выглядит успешным, но detail-панель не открылась, не повторяй слепо тот же клик. Проверь через DOM, привязаны ли `data-*`-кнопки, и при необходимости воспроизведи клик через `browser_console`/DOM evaluation для конкретного элемента. Для плотных tabular admin UI это надёжнее, чем гадать по accessibility snapshot.
- Тот же fallback применяй и к React navigation/modal-кнопкам (`Профиль`, `Все чаты`, tab-like controls), если accessibility click формально успешен, но экран не меняется и в консоли нет JS errors. В таком случае сначала раздели два вопроса: (1) UI реально сломан; (2) именно browser-click слой не донёс событие. Надёжная последовательность приёмки: `browser_click` -> snapshot без изменений -> `browser_console` с адресным `element.click()` -> повторный snapshot/DOM-state. Если после DOM-click экран или модалка переключились, фиксируй это как limitation verification path, а не как доказанный продуктовый дефект.
- Для chat/profile contour с файлами не считай сценарий `Открыть` подтверждённым только по наличию кнопки в DOM. Нужна отдельная проверка download path: (1) получить живой файл из `/api/files`; (2) взять его фактический `id`/`download_url`; (3) подтвердить, что route отвечает корректным статусом и содержимым именно для этого файла. Не подменяй это проверкой на жёстко взятом `id=1` или абстрактным ожиданием, что раз список файлов есть, значит и open/download уже работает.
- Для профильных экранов сначала отделяй профильные сигналы от chat-context шума. Если пользователь просит `product-level` профиль, не тащи в summary метрики вроде `Файлов в чате`, `текущий чат` или другие показатели, завязанные на временный экранный контекст. Оставляй только данные, которые описывают сам профиль: заполненность, статус первичной настройки, количество профильных файлов, наличие распознанного текста, ключевой следующий шаг.
- Для профильных file-list экранов проверяй два режима отдельно: empty-state и non-empty list-state. Empty-state должен честно объяснять, что файлов нет по текущему фильтру. Для non-empty state нужна отдельная живая проверка строки списка: контент слева (имя, размер, тип, дата, summary), действие справа (`Открыть` или эквивалент), без плавающей кнопки посреди текстового блока.
- Если в profile/settings экране рядом с рабочей формой есть декоративный preview-блок, сначала спроси себя, добавляет ли он новую информацию. Если блок просто дублирует уже выбранные значения (`тон`, `глубина`, `манера`) и раздувает экран, это кандидат на удаление или сокращение до короткого поясняющего summary. Для задач класса `довести до 8.5/10` user-facing правило простое: меньше декоративного дубля, больше деловой плотности.
- Избегай расплывчатых подписей вроде `С текстом`, если по смыслу речь идёт об обработке файла, а не о типе файла. Для profile/files UX предпочитай предметные формулировки: `Распознано`, `С распознанным текстом`, `Без распознанного текста`. Сначала проверь, что backend-флаг действительно означает успешное извлечение/распознавание (`text_extracted` или эквивалент), и только затем переименовывай UI.
- Если download/open route выглядит частично рабочим в браузере, но даёт странный `content-type` или расходится с прямым backend-call, не закрывай UX-поток преждевременно. Для local-first React/Vite контуров это отдельная проверка цепочки: frontend `API_BASE`/proxy -> live backend port -> auth token key в `localStorage` -> физическое наличие файла на диске -> ответ именно backend route, а не HTML fallback другой поверхности.
- Для file-open flow в React/Vite отдельно проверяй нормализацию `download_url`/path во frontend helper-е. Если backend уже возвращает путь с API-префиксом вроде `/api/files/59/download`, helper не должен слепо делать `fetch(`${API_BASE}${path}`)`, иначе получится ложный `404` на `/api/api/...`.

- Для chat onboarding / welcome-state после UI-полировки проверяй не только внешний snapshot, но и реальную state-машину dismiss-path. Отдельный приёмочный паттерн: (1) подтвердить, что `browser_click` или DOM-click действительно запускает handler; (2) сразу проверить в `browser_console`, изменились ли управляющие флаги вроде `state.chatWelcomeDismissed` / `user.onboarding_completed`; (3) затем отдельно проверить, что `render...()` реально убрал блок из DOM (`hidden`/`display:none`) и не оставил второй пустой placeholder-конкурент в message-area; (4) после dismiss ввести реальный текст в composer и подтвердить, что поле действительно в фокусе, текст принимается, а основное действие (`Отправить`/send button) выходит из disabled-состояния. Иначе легко получить ложное ощущение, что UX уже доведён, хотя welcome-блок всё ещё доминирует над chat-first экраном или composer остался визуально красивым, но неготовым к первому действию.
- Если задача звучит как «дотянуть первый экран чата до 9/10», считай zero-state отдельным продуктовым режимом, а не просто пустой версией обычного экрана. Самый частый потолок soft-polish — около `8.5/10`, когда интерфейс уже аккуратный, но above-the-fold внимание всё ещё распадается между hero, guide/banner, thread header, sidebar empty-state и composer. Практический паттерн high-ROI: (1) определить единственный primary entrypoint — обычно composer; (2) убрать дублирующий CTA из hero/welcome; (3) в zero-state скрыть вторичные блоки вроде `chat-thread-header` и topbar guide/policy cards, если они не критичны для первого шага; (4) оставить верхний welcome как короткий onboarding-text, а не как вторую самостоятельную карточку-сценарий; (5) после каждой такой правки проверять live DOM-инварианты (`headerVisible`, `guideVisible`, `welcomeVisible`, `jsErrors`) и заново снимать внешнюю оценку. Если после этого внешний вердикт всё ещё ниже 9 и причина формулируется как «всё ещё два центра внимания» или «слишком много воздуха/служебного текста», не притворяйся, что достаточно ещё одного CSS-tweak: честно фиксируй, что предел soft-polish достигнут и дальше нужен controlled zero-state redesign без смены архитектуры.
- После `location.reload()` или другого жёсткого refresh во время live UI-приёмки не считай возврат на login screen автоматически регрессом свежих правок. Сначала проверь, не потеряна ли просто текущая сессия браузера, и при необходимости быстро переавторизуйся тем тестовым пользователем, которым уже шла приёмка. Только после повторного входа делай выводы о фактическом состоянии zero-state / screen layout. Иначе легко перепутать auth/session-effect с визуальным дефектом экрана.

- Если browser-click по заголовку плотной таблицы формально успешен, но сортировка не переключилась, не повторяй тот же click вслепую. Для sortable `thead` в admin UI надёжный fallback — адресный `browser_console`/DOM-click по `[data-*]` кнопке заголовка, а затем немедленная проверка двух сигналов: изменился ли `state.admin.*Sort` и сменилась ли первая строка таблицы.
- Для таблиц с несколькими агрегатами не ограничивай приёмку снимком заголовков. Если пользователь просит разнести один summary-столбец на несколько числовых колонок (`Чаты`, `Задачи`, `Сессии` и т.п.), финальная проверка должна подтверждать три вещи: (1) отдельные заголовки реально видны в DOM; (2) каждое значение рендерится в своей ячейке, а не как старый объединённый chip-row; (3) сортировка по каждому числовому столбцу реально меняет порядок строк.

- Для soft-status справочников и похожих catalog/reference UI проверяй не только список, но и lifecycle статуса.
- Подтверди три состояния: `active`, `inactive`, `deleted`.
- Проверь отдельно list summary, detail table, create/edit modal и backend write-path.
- Если правило звучит как «неактивное/удалённое нельзя выбрать заново, но старое значение должно остаться видимым», разбей проверку на две части:
  - fresh choice: выключенный элемент не появляется в новом выборе;
  - preserved choice: уже сохранённое значение остаётся в select с явной пометкой статуса.
- Не считай preserved-flow подтверждённым только потому, что фильтрация работает в runtime-наборах. Нужен отдельный сценарий: сохранить значение, затем перевести его в `inactive/deleted`, затем переоткрыть форму и проверить, что оно осталось видимым как историческое.
- Для admin-блоков, где policy опирается на reference dataset (например, `dashboard policy` ↔ `data_sources`), принимай экран только после двух независимых проверок: (1) сам policy read/write path реально работает; (2) список selectable items реально согласован с live reference dataset. Если `GET/PATCH` по policy успешны, но UI показывает пустое состояние вроде `активные источники пока не настроены`, не называй блок принятым по одному save-path. Это отдельный продуктовый дефект согласованности данных.
- Отдельно различай два класса пустого policy-screen: acceptance drift и живой hydration bug. Если DOM действительно содержит только empty-state (`Источники пока не настроены`, `0` внутренних/внешних коннекторов), а прямой live `GET /admin/dashboard-policy` в тот же момент возвращает непустой `data_sources`, фиксируй это как frontend/runtime defect гидратации overview, а не как проблему backend policy route и не как дефект одного Playwright locator-а.
- В таком классе экранов отдельно проверяй preserved-choice fallback: если policy уже содержит `allowed_sources`/сохранённые ключи, а runtime dataset временно пустой или неполный, UI должен либо показать эти значения как исторически сохранённые, либо явно подсветить рассинхрон. Иначе пользователь видит полурабочую карточку: режим сохраняется, но фактический состав источников проверить и изменить нельзя.
- Для jobs detail после write-actions (`pause`, `resume`, rename/display_name`) проверяй не только backend status, но и перерисовку detail-панели. Если list уже показывает новое состояние (`на паузе`), а detail всё ещё держит старую кнопку (`Приостановить задачу` вместо `Возобновить задачу`), это не просто flaky smoke. Это отдельный UI-state/stale-detail defect. В таком случае не лечи это бесконечными `waitForTimeout(...)`: сначала зафиксируй расхождение `list vs detail`, затем чини refresh path выбранной сущности.
- Для monolithic jobs/admin smoke не смешивай в один хрупкий проход несколько version-sensitive действий вроде `rename -> reload -> reopen detail -> pause/resume`. Если backend уже доказан targeted probe-ом, а длинный smoke падает на stale-state после одного из write-actions, режь сценарий на независимые acceptance-слои: `create/open detail`, `pause/resume`, `rename/display_name`, `admin tabs`. Иначе smoke начинает скрывать реальный продуктовый баг за вторичными concurrency- и navigation-эффектами.
- После добавления новых статусных полей в backend (`is_active`, `deleted_at`, `status`) обязательно прогоняй и агрегирующие admin queries/smoke. На DuckDB/SQL-совместимых контурах типичный регресс — забытый `GROUP BY` для новых колонок, хотя CRUD уже выглядит рабочим. В этом классе задач отдельный симптом — smoke падает не на create/update, а на admin user stats query.
- Если runtime-проверка требует тестовых create/update/delete действий в живой local-first БД, заранее планируй cleanup как часть приёмки, а не как факультативный хвост. Для справочников и пользователей это значит: либо откатывать тестовые записи через штатные API, либо, если пришлось временно остановить backend и чистить DuckDB напрямую из-за file lock, после cleanup обязательно снова поднять backend и повторно прогнать smoke/health-check, чтобы приёмка заканчивалась на чистом состоянии.
- Когда вручную проверяешь admin/API сценарии из браузерного `fetch`, не считай HTML `404` автоматически дефектом backend. Сначала сверяйся с frontend-обёрткой `api(...)` и её `API_BASE`: часть ложных 404 возникает из-за запроса в неправильный путь/origin в обход продуктового маршрута.
- после этого обязательно сделай ещё один короткий browser-pass именно по тем экранам, где тестовые данные были видны пользователю, и зафиксируй, что summary/detail уже показывают очищенное состояние. Иначе технически backend чистый, а продуктовая приёмка остаётся недоказанной.
- После cleanup mixed-source экранов не делай вывод по одному числу в `state`. В этом контуре `jobs` мог снова показывать внешние Hermes cron-задачи, хотя локальные Web MVP jobs уже были удалены из DuckDB. Для приёмки разделяй два вопроса: (1) локальная БД действительно очищена; (2) экран честно показывает смешанный источник данных и не вводит в заблуждение. Иначе легко ложно объявить cleanup «неполным».
- Если `browser_click` по табличной кнопке формально успешен, но detail-панель не обновляется, попробуй адресный DOM-click через `browser_console` по `data-*`-атрибуту нужной строки, а не повторяй тот же click вслепую. Для плотных admin tables это надёжный fallback.
- Контекстные topbar-блоки проверяй только на тех экранах, где они должны жить по продуктовой логике. Если после перехода на другую вкладку блок скрыт, сначала исключи ожидаемое поведение экрана, а уже потом считай это регрессом.
- Если Hermes browser wrapper/CDP недоступен, а пользователь просит просто подтвердить открытие конкретного экрана, не останавливайся на сообщении про сбой браузерного инструмента. Для local-first web UI валиден fallback через уже подключённый в проекте Playwright runtime: подними targeted `node`-probe из repo с импортом `playwright`, открой живой frontend, и подтверди экран по DOM.

- Если token injection в `localStorage` не выводит приложение из login screen, не объявляй screen-flow сломанным сразу. Отдели `session restore` от обычного login flow: сначала попробй штатный UI login теми же тестовыми данными, и только потом делай вывод о поломке экрана.
- Если даже login/session restore в headless runtime нестабилен, а пользователь просит только коротко подтвердить, что конкретное доступное действие открывает экран, отделяй `navigation wiring` от полной auth/runtime-приёмки. Практический fallback: убедиться, что frontend загрузил app JS и нужный handler доступен, временно раскрыть app shell через DOM только для проверки маршрутизации, затем вызвать тот же UI-control (`button.click()` по реальному id/selector вроде `#topbarProfileBtn`) и снять три сигнала: активный `screen`, заголовок экрана и видимость target-container. Такой проход подтверждает, что действие действительно переключает экран, но не должен подаваться как доказательство полного authenticated flow.
- Для React/Vite экранов не полагайся только на `innerText`, если визуально страница выглядит пустой. У части экранов полезный сигнал живёт в `#root.innerHTML`, классах активной навигации и заголовках секции, тогда как `innerText` может вернуть пустую строку или неполный текст.
- Для короткой приёмки конкретного экрана достаточно трёх live-сигналов: (1) активная кнопка навигации переключилась на нужную; (2) в `main` появился ожидаемый заголовок экрана; (3) HTML соответствующего контейнера содержит профильный контент. Для profile-screen хороший минимальный набор — активная вкладка `Профиль`, заголовок `Профиль пользователя`, и summary/profile-блоки в `main`.
- Если пользователь просит не полный smoke, а только `открыть экран X и кратко подтвердить`, не разворачивай лишний отчёт. После live-проверки верни короткое подтверждение в 1 фразе: что именно открыто и какие 1–2 DOM/runtime-сигнала это подтвердили. Для profile-screen достаточно формата вроде: `Экран открыт: активна вкладка Профиль, виден заголовок Профиль пользователя.`

- для monolithic React acceptance не используй `localStorage + reload` как основной navigation path, если экран уже имеет реальные tab/button controls. Такой restore-path быстро превращается в источник flaky smoke и даёт ложные падения не по продуктовой причине. Сначала адаптируй script к текущему UI-контракту: клик по tab-кнопке, ожидание активного класса/структурного DOM-инварианта, затем проверка содержимого.
- если длинный smoke уже снова зелёный, не оставляй backlog и runbook в состоянии "ещё не доведено". Для local-first web задач закрытие темы включает не только код и прогон, но и перевод проектной документации из defect-mode в hardening-mode: обновить backlog, runbook/deploy guide и decision log под фактический рабочий baseline.

9. Если UI и backend расходятся по степени готовности, фиксируй это как разные уровни приёмки.
- Возможна ситуация, где chat UX и jobs list/detail уже подтверждены в живом UI,
- но automated smoke всё ещё падает на backend run-path.
- В таком случае не смешивай вывод в фразу «ничего не готово».
- Отдельно помечай: что уже принято по UI/runtime, что осталось починить в backend.
- Отдельная практическая ловушка: после чистого логина может всплыть transient banner вроде `Сервис вернул не JSON (500)` на части startup-запросов, а затем целевой экран всё равно успешно загрузится и подтвердить UI-pass будет можно. Не смешивай такие эпизоды с визуальной приёмкой. Разделяй два вывода: (1) сам экран и его UX-поток реально приняты; (2) в startup/backend остаётся отдельный нестабильный хвост, который надо чинить уже как отдельную задачу.
- Для таких случаев полезно делать двойную проверку: сначала подтвердить пользовательский экран через snapshot/vision/DOM, затем отдельно проверить console/network-сигналы и записать runtime-хвост как independent follow-up, а не как повод откатывать весь UI verdict.

# Практические приёмы

## 1. Если пользователь говорит «в интерфейсе ничего не изменилось»

Действуй так:
- не спорь с пользователем;
- перепроверь реальный экран;
- отдельно отметь, что уже есть в коде и что не подтверждено в runtime;
- после правки снова проверь браузером, а не только diff/patch.

## 2. Если один из startup-запросов иногда отдаёт HTML вместо JSON

Считай это дефектом пути boot/runtime, пока не доказано обратное.

Полезная последовательность:
- проверить отдельные API-запросы по одному;
- затем вызвать те же refresh-функции по одной;
- только потом проверять агрегированный boot;
- если поштучные запросы работают, а общий boot падает, ищи проблему в пакетной инициализации, Promise.all, парсинге ответов или гонке состояния.
- если backend сидит на DuckDB или другом single-writer контуре, проверь, нет ли скрытой записи в supposedly-read path. Отдельная ловушка: `require_auth()`/session middleware, которое на каждый GET обновляет `last_seen_at` или другой heartbeat. При параллельном boot это может давать плавающие `500` на `/me`, `/bootstrap`, `/jobs/meta`, `/files` и выглядеть во frontend как «Сервис вернул не JSON (500)», хотя endpoint логически read-only. Для диагностики прогоняй несколько раундов параллельных запросов к boot-endpoint'ам с одним и тем же токеном; если падают разные read-endpoint'ы, сначала убери лишнюю запись из auth-path или вынеси heartbeat в отдельный редкий update, а не лечи это как frontend parse bug.
- если после восстановления с токеном app shell не показывается, хотя `session/bootstrap/me/threads` уже отвечают, не держи показ оболочки за второстепенными загрузками. Для local-first UI это отдельный паттерн приёмки и ремонта: сначала shell-first boot (скрыть `loginScreen`, показать `appShell`, выставить базовый screen), а уже потом догружать `jobs meta`, `user files`, admin overview и другие тяжёлые панели через deferred `Promise.allSettled(...)`. Ошибка в открытии последнего чата или во вторичном admin fetch не должна возвращать пользователя на экран логина.
- отдельно проверь, не открыта ли UI-страница с неправильного origin: local-first frontend может выглядеть «живым», но фактически ходить в backend по CORS-несовместимому адресу.
- если live endpoint даёт `500`, а причина не видна по HTTP-ответу, воспроизведи тот же вызов через локальный Flask/Werkzeug `test_client()` на том же коде и с той же БД. Это быстрый способ получить настоящий traceback handler-а и отделить permission/data проблему от банального `NameError`/ошибки функции внутри route.
- если для live UI acceptance нужен Playwright, а прямой `node script.mjs` падает на missing `.so`, сначала попробуй штатный repo-wrapper вроде `scripts/browser_runtime_env.sh`, а не городи новый одноразовый overlay прямо в команде. Для local-first проектов это более устойчивый путь: сначала короткий sanity-probe (`browser launch -> goto frontend -> title`), и только потом full acceptance script.
- для acceptance сценариев с новыми chat-first функциями сначала отдельно докажи backend-контракт прямым API-вызовом, а уже потом проверяй UI-отрисовку. Практический пример класса задач: если проверяешь request-level dashboard policy, сначала подтверди, что `/messages` реально возвращает `meta.request_execution_policy` и `meta.dashboard_artifact`, и только затем требуй от Playwright наличия policy-strip, artifact-card и `Сохранить как задачу`.
- если один monolithic acceptance уже дошёл до живого UI, но упал на неоднозначном локаторе или хрупком поиске сущности, не retry тем же способом. Сразу переводи проверку на unique marker + targeted selector: `exact: true`, timestamp в тексте/имени job, поиск нужного thread/job по backend round-trip, а не по неустойчивому `preview` или общему `getByText(...)`.
- если frontend показывает transient banner вида `Сервис вернул не JSON (500)`, сначала раздели два слоя: (1) UX-экран мог уже успешно загрузиться; (2) backend мог отдать не-JSON на одном из startup/chat route. Для такого случая acceptance должен отдельно подтвердить backend error-contract: живые `404/405` и другие error-path должны возвращать JSON, а не HTML/plain text.
- если задача одновременно затрагивает model routing и chat queue, не ограничивайся тем, что selector появился во frontend. Отдельно проверь live round-trip: `/api/bootstrap` реально отдаёт `llm_routing`, отправка сообщения реально прокидывает `model_preference`, а в `chat_tasks.request_policy_json` сохраняется ожидаемое значение. Иначе можно принять UI-контрол, который визуально существует, но теряется между payload и очередью.
- если переносишь кусок routing/queue-логики в более старый backend-срез, не предполагай, что там уже существуют те же helper-функции и константы, что в локальной ветке. Перед restart обязательно проверь весь dependency-chain патча: normalizer/helper, модельные константы/alias map и точки вызова внутри route. Для mixed-slice правок безопаснее использовать совместимый минимальный helper (например, возвращать строковые значения `auto` / `owl_alpha` / `deepseek_r1`, если в целевом срезе ещё нет общих констант), чем слепо переносить более новый код и ловить live `NameError` на `POST /messages`.
- если acceptance нашёл реальную backend-ошибку на admin-route, не ограничивайся browser verdict. Сними traceback из лога живого backend-процесса, исправь handler, сделай чистый restart именно этого runtime и затем повтори тот же acceptance script. Для local-first web задач это надёжнее, чем разбрасываться новыми ad-hoc smoke-командами.
- если supposedly read-only admin-route падает только под параллельной нагрузкой, не списывай это на UI smoke или случайный runtime jitter. Для local-first DuckDB это отдельный durable-паттерн: воспроизведи route прямыми concurrent GET, проверь transient file-handle/catalog conflicts, затем лечи `duckdb.connect(...)`/DB connection path лёгким retry и добавляй regression именно на параллельный endpoint. После этого отдельно перепроверь live HTTP concurrency и только потом возвращайся к browser/UI automation.
- если после повторного acceptance все write/read path'ы и backend round-trip проходят, а падает только один визуальный assert вроде `policy_strip_visible`, не смешивай это с общей неготовностью feature. Зафиксируй отдельным уровнем: функциональный контур принят, оставшийся хвост — точечный React/UI rendering nuance.
- Для split-contour React/Vite поверхностей отдельно подтверждай, в какой backend реально ходит live runtime. Недостаточно проверить frontend-репозиторий на диске: сначала прочитай `vite.config.*`/proxy и сверь фактический target (`/api` proxy, `HERMES_WEB_FRONTEND_BACKEND_BASE` или эквивалент) с живым PID/port backend-процесса. Иначе легко править backend в «новом» репозитории, пока браузер продолжает питаться от другого проекта/процесса.
- Если симптом формулируется именно как `frontend_proxy_upstream_unavailable`, первым продуктовым smoke не делай прямой вызов backend. Сначала проверь `frontend-origin/api/service-info` или эквивалентный лёгкий `/api/*` route именно через пользовательский frontend-origin. Только после этого лезь в unit/env upstream. Это быстрее отделяет runtime proxy defect от живого backend.
- если после правки frontend и backend поведение расходится, не спорь с экраном. Считай это сигналом проверить цепочку целиком: `browser -> frontend origin -> proxy/dev server -> live backend cwd/pid -> DB/env`. Для local-first MVP это часто дешевле и точнее, чем ещё один раунд CSS/JS правок в неверном дереве.

- если порты держатся через `systemd --user`, не останавливайся на проверке одного PID. Для канонического contour обязательно сверь сами user units: `WorkingDirectory`, `ExecStart`, env-файл и restart-статус frontend/backend/runtime-сервисов. Иначе можно убить вручную старый процесс, а через секунду получить тот же legacy backend обратно из unit-файла или restart-policy.
- если frontend-service ушёл в restart-loop, сначала исключи банальный конфликт за порт с вручную поднятым `vite`/dev-server. Не называй это дефектом React-кода, пока не проверишь, что порт не занят параллельным ручным runtime. Для приёмки отдельно различай `systemd unit healthy` и `manual dev runtime works` — оба сигнала полезны, но это не одно и то же.
- перед live-приёмкой явно зафиксируй канонический contour этой задачи: какое дерево репозитория считается целевым, какие frontend/backend порты считаются боевыми для текущего прохода, и какие legacy/dev-поверхности не должны использоваться для verdict. Не полагайся на `по умолчанию` или на вчерашние порты.
- если задача включает последующую передачу на новый сервер, не ограничивайся кодом и runtime-pass. Для этого класса задач отдельный слой готовности — deployment handoff: dependency inventory, zero-server bootstrap для Hermes, env-example, systemd user units, verify-script и явная пометка first-run режима (`demo-seed` vs production-like). Без этого local acceptance ещё не означает переносимую систему.
- если в машине одновременно открыты несколько живых контуров, финальный вывод обязан различать три вещи: (1) какой contour был целевым; (2) какой contour реально был проверен; (3) был ли это свежезапущенный runtime или уже существующий процесс. Формулировка вида `проверила UI` без этих трёх привязок для local-first задач недостаточно надёжна.
- если пользователь отдельно указал каноническое дерево, серверные роли или порты, считай это приёмочным инвариантом, а не справочной деталью. Перед любым browser-pass сначала сверь именно эти значения, и только потом делай выводы по экрану или backend-route.
- если пользователь прямо сказал `правь только новый сервер` или эквивалентно ограничил целевой contour, не делай даже "временных" продуктовых правок на текущем/локальном контуре ради удобства диагностики. Сначала сверь, где реально идёт live traffic, и вноси persona/UI/backend-изменения только туда. Если уже успел изменить не тот contour, откати это до продолжения работ.
- если по задаче есть разделение ролей между серверами, не смешивай `временный runtime для доводки` и `целевой production contour` даже в формулировках. Отдельно фиксируй: (1) где реально гонялись frontend/backend проверки; (2) что из этого является только техническим стендом; (3) на каком сервере ещё нужно выполнить финальное развёртывание и связку. Иначе легко выдать корректную техническую проверку за доказательство готовности неверного целевого контура.
- если фронт временно поднят на backend-сервере только для сборки, smoke или ручной доводки, не помечай `frontend готов` без оговорки. Корректный статус в таком случае: `код и временный runtime проверены, но целевая связка old-frontend -> new-backend ещё не принята`.
- если acceptance нашёл реальную ошибку на live admin/backend route, не ограничивайся browser verdict и не переключайся сразу на абстрактный код-review. Сними traceback живого процесса, затем найди, не является ли причина data-shape drift между текущей БД и кодом. Типичный durable-кейс для local-first DuckDB: handler считает, что поле лежит прямо в `messages.user_id`, тогда как в реальной схеме доступны только `thread_id` и `meta_json`.
- если live auth/данные текущей БД ненадёжны для продуктовой верификации, не строй ad-hoc проверки на случайном runtime. Для backend acceptance предпочитай штатный smoke-style harness проекта: временная DuckDB + те же helper-инициализации/фикстуры, что используются в `test_smoke` или эквиваленте. Это надёжнее, чем делать выводы по живому login `401` или по голому `python app.py` import-path.
- для live browser acceptance не полагайся на `admin@demo.local` и другие исторические demo-логины как на вечный инвариант. Если текущая БД уже живая и не в demo-mode, сначала найди или подготовь отдельный acceptance-аккаунт с известным паролем, не трогая основной admin. Иначе легко принять `401 invalid_credentials` за проблему frontend/backend связности.
- если после логина экран формально загрузился, но любые nav-клики перехватывает `.modal-backdrop-react`, сначала сними живой DOM и проверь, не поднялся ли onboarding-modal. Для этого контура устойчивый путь — явное закрытие через кнопку `Позже`, а не слепой `Escape` или повторение того же click. После закрытия отдельно проверь, что nav-кнопки (`Задачи`, `Управление`, `Профиль`) снова реально кликабельны.
- если acceptance-script падает на фразах вроде `в UI нет кнопки сохранения policy` или `не отрисовались источники`, не объявляй feature сломанной до живой DOM-проверки. Сначала сними фактические `id`, `data-*`, тексты кнопок и заголовки секции; затем адаптируй automation к текущему UI-контракту. Для admin/policy экранов дрейф текстов вроде `Сохранить policy` -> `Сохранить и включить` / `Сохранить и выключить` — это типичный acceptance drift, а не обязательно продуктовый дефект.
- для dashboard/source-policy сценариев принимай feature в два слоя: (1) isolated backend proof на временной БД — что `local_first`, `local_only`, `clarification_request`, `policy_blocked_global` и artifact/meta реально работают по контракту; (2) отдельно live UI/admin-pass на каноническом contour. Не подменяй один слой другим.
- см. также `references/runtime-env-and-acceptance-account.md` — как выровнять canonical contour через общие env-переменные, не размазывать порты по коду и не завалить live acceptance из-за onboarding modal или устаревших demo-логинов.

Практический паттерн для local-first web MVP:
- сначала подтвердить канонический frontend origin, который реально разрешён backend'ом;
- не считать временный static server финальным доказательством готовности, если продуктовый backend ждёт другой origin;
- если видишь `Unexpected token '<'`, проверь не только JSON parsing, но и то, не прилетел ли HTML fallback из другого маршрута или другого runtime-контура.

- Если UI восстанавливается в уже существующей авторизованной сессии, не подменяй session-restore первичным setup-flow. Сначала найди реальный runtime entrypoint для существующей сессии (`restoreSession()` или эквивалент) и используй его. В этом классе задач вызов bootstrap/setup-функции поверх готовой сессии дал ложную диагностическую ошибку уровня `valid_email_required`, хотя проблема была не в данных пользователя, а в неверном recovery-path.

## 3. Если UI ведёт себя «как будто код не обновился»

Сначала исключи runtime-рассинхрон, а уже потом правь логику.

Обязательная проверка:
- какой процесс реально слушает нужный порт;
- не остался ли старый backend-процесс после неудачного рестарта;
- поднялся ли новый код на том же порту или упёрся в `Address already in use`;
- какой `service-info`/mode реально отдаёт текущий backend.
- после подтверждения stale-процесса не ограничивайся `kill` + ручным `python app.py`, если у проекта есть канонический скрипт запуска. Для local-first MVP это отдельный приёмочный шаг: подними backend тем же entrypoint, который ожидает проект (`run_backend_service.sh` или эквивалент), и только потом перепроверяй live route/404/500. Иначе легко принять за кодовый дефект то, что на порту снова поднялся не тот runtime.
- если пользователь перечисляет конкретные пропавшие UI-элементы (`подписи`, `селектор модели`, `zoom файлов`, старые кнопки/лейблы), не ограничивайся поиском по source-файлам. Отдельно проверь два слоя артефакта: (1) есть ли эти строки/маркеры в текущем `src`; (2) попали ли они в реально собранный `dist`/bundle. Практический смысл такой проверки:
  - строки есть и в `src`, и в `dist` -> это не «случайная старая сборка», а текущий UI-контракт действительно уже другой;
  - строки есть в `src`, но нет в `dist` -> подозревай несвежую сборку или выкладку не того bundle;
  - строк нет уже в `src` -> нужный UX, вероятно, был вытеснен более поздним рефакторингом.
- для chat-first React-контуров это особенно полезно, когда пользователь говорит не просто `ничего не поменялось`, а `раньше были конкретные подписи и контролы, куда они делись`. Сначала зафиксируй факт дрейфа UI-контракта по `src + dist`, и только потом переходи к проверке live PID/cwd/served bundle на целевом порту.
- если после `session restore` или reload пользователь внезапно попадает на login screen, не считай это доказательством истёкшей сессии, пока не проверишь frontend catch-path. Отдельный живучий анти-паттерн: boot-код чистит token на любой ошибке `loadCoreState()`/bootstrap, и тогда побочный `404/500` на вторичном endpoint-е выглядит как "таймер авторизации сам сбросился". Практический repair-path: очищать token только на явных auth-ошибках (`invalid_token`, `auth_required`), а вторичные данные (`files`, `jobs meta`, прочие не-критичные bootstrap-ресурсы) переводить на `Promise.allSettled(...)` или deferred load, чтобы app shell не разрушался из-за неключевого route.
- если пользователь жалуется на HTML/`не JSON` в UI, разделяй два слоя: backend error-contract и user-facing текст фронта. Даже когда backend уже в основном отдаёт JSON, фронту всё равно нужен безопасный parse-path для public/startup запросов (`service-info`, `setup/status` и т.п.) и нормализованное сообщение без сырого HTML snippet. Для этого класса задач good-enough инвариант такой: живые `404/500` на API возвращают JSON, а frontend при non-JSON ответе показывает нейтральную продуктовую ошибку, а не `<html>...` пользователю.
- если в chat-first web UI backend/агент уже активно использует markdown, не лечи проблему отключением markdown на стороне Hermes только ради одного клиента. Для local-first контуров предпочтительный repair-path — добавить во frontend минимальный безопасный markdown renderer и сохранить единый контракт ответа между Telegram, Hermes и Web.
- Если продуктовая жалоба про markdown звучит как `символы/стрелки отображаются плохо`, сначала проверь frontend-нормализацию реальных пользовательских последовательностей (`$\\rightarrow$`, `$\\times 2$`, `$\\uparrow$`, `$\\downarrow$` и их escaped-варианты), а не только базовый `\\to`. Для acceptance такого класса правок нужен хотя бы один live render/DOM pass именно на пользовательских последовательностях, иначе можно ложно закрыть дефект по слишком узкому regex.
- good-enough минимум для такого renderer: заголовки `#`–`###`, маркированные/нумерованные списки, blockquote, fenced code blocks, inline code, `**bold**`, `*italic*`, ссылки `[label](https://...)` и `mailto:`. Raw HTML не интерпретировать; избегать `dangerouslySetInnerHTML`, если задача решается React nodes/text-рендером.
- live-приёмку markdown не своди к `build green`. Подтверди хотя бы один реальный message render на isolated runtime: наличие heading, list items, strong, link href, inline code, code block и quote в DOM. Для production surface отдельно проверь, что после рестарта фронт уже отдаёт свежий bundle с markdown-стилями.
- если одновременно существует несколько похожих Hermes Web контуров, не начинай с патча первого попавшегося repo. Для verdict по runtime сначала найди живой PID на целевом порту, затем проверь его `cwd`, `cmdline` и `HERMES_WEB_*` env через `/proc/<pid>/...`, и только после этого правь и перезапускай именно то дерево, из которого реально питается текущий frontend/backend. Это особенно важно, когда Vite frontend и waitress/backend визуально "похожи", но один из них уже идёт из другого checkout.
- если web-backend ходит в отдельный downstream Hermes/gateway, не ограничивайся проверкой самого web-backend. Для user-facing переключателей вроде `approvals.mode`, `--yolo`-подобного поведения или доступности command execution сначала докажи, какой именно Hermes-процесс обслуживает downstream-порт (типичный случай — listener на `8642`), затем проверяй его `cwd`, `cmdline`, `HERMES_HOME`, `PATH`, `VIRTUAL_ENV` и только после этого меняй конфиг. Практический паттерн: (1) найти PID, который слушает downstream-порт; (2) сверить, что это именно `gateway run`/нужный Hermes runtime; (3) менять `~/.hermes/config.yaml` именно этого контура; (4) делать restart соответствующего `systemd --user` unit, иначе новый `approvals.mode` может остаться только на диске.
- если пользователь просит `execute command = on`, не придумывай отдельный флаг, пока не проверишь реальную модель tool-доступа в этом Hermes-контуре. Для gateway/downstream обычно важен не один magical toggle, а факт, что включены нужные toolsets (`terminal`, при необходимости `code_execution`). Проверяй это отдельно от `approvals.mode`: первое отвечает за наличие исполняющего инструмента, второе — за политику подтверждения.
- если после reboot/restart пользователь говорит, что chat-задача `пропала`, а в UI остался текст `Не удалось получить ответ...`, не делай вывод по одной фразе assistant-message. Для этого класса задач сначала разделяй два сценария: (1) downstream timeout — в `chat_tasks` задача дошла до `error` с `last_error` вроде `timed out`; (2) broken queue recovery — задача была в `running` в момент рестарта и после запуска не вернулась в обработку. Проверяй live БД/таблицу `chat_tasks`, а не только UI.
- если пользователь говорит, что ответ модели уже фактически пришёл, а чат всё ещё висит в `Готовлю ответ…` / `ожидаю ответа`, сначала сравни два таймлайна: сколько живёт frontend polling после submit и сколько реально длится `chat_tasks` до `finished_at` в прод-данных. Если backend завершает задачи позже жёсткого окна фронта, это не downstream timeout, а frontend state-refresh defect: UI перестал опрашивать active thread слишком рано. Устойчивый repair-path — не ограничиваться bounded polling после submit, а добавить background polling активного thread, пока в `messages` есть assistant message с `meta.pending=true`, с `inFlight` guard, автоостановкой после исчезновения pending и cleanup timer при смене thread/unmount. Подробности и пример симптома см. в `references/chat-pending-refresh-vs-backend-completion.md`.
- если пользователь жалуется, что при прокрутке к старым сообщениям чат сам сбрасывает его вниз, не списывай это на browser glitch или sticky-layout, пока не проверишь связку `polling refresh -> messages state replacement -> auto-scroll effect`. Для React chat-first экранов типичный скрытый дефект такой: polling каждые N секунд приносит тот же набор сообщений новым массивом, а `useEffect([messages])` безусловно делает `scrollTop = scrollHeight`. Правильный repair-path: отделить `thread changed` от `messages really changed`, хранить флаг `shouldStickToBottom` по фактической позиции скролла и выполнять автопрокрутку только в двух случаях — (1) пользователь открыл другой thread; (2) реально изменился хвост сообщений и пользователь уже был у нижней границы. Приёмка для такого класса бага должна проверять idle-сценарий явно: вручную увести messages-panel вверх, подождать дольше polling-интервала и подтвердить, что `scrollTop` и `distanceFromBottom` не изменились без новых сообщений.
- Если пользователь говорит, что время assistant-сообщения равно времени исходного user-запроса или "прыгает", не списывай это на форматирование даты во frontend, пока не проверишь backend lifecycle placeholder-сообщения. Для chat-task контура частая причина в том, что placeholder assistant message создаётся сразу с `created_at=request_ts`, а при success/error финализации backend меняет только `content` и `meta_json`. В таком случае правильный repair-path — обновлять assistant `created_at` до общего `finished_at` задачи и использовать тот же timestamp для `chat_tasks.finished_at` и, по возможности, `threads.updated_at`. Проверять нужно живым round-trip: `assistant_message.created_at == chat_tasks.finished_at`. Подробности см. в `references/chat-message-timestamp-semantics.md`.
- Для session timeout отдельно разделяй две гипотезы: (1) expiry логически считается не от `last_seen_at`; (2) формула уже правильная, но runtime/default TTL не соответствует продуктовой политике. Не лечи это сразу переписыванием lifecycle-функций: сначала проверь `session_expires_at(last_seen_at)` и дефолт/живой `HERMES_WEB_SESSION_TTL_HOURS`.
- для reboot-safe chat queue не ограничивайся worker'ом, который умеет подбирать только `pending`. На старте backend нужен recovery-step: все `chat_tasks` со статусом `running` и пустым `finished_at` должны переводиться обратно в `pending`, `started_at` очищаться, а assistant placeholder возвращаться в состояние ожидания. Иначе пользователь видит ложную `потерю` задачи после рестарта, хотя проблема в неполном lifecycle recovery.

- при диагностике автопрыжков между вкладками проверяй не только `localStorage`, но и timing его перезаписи во время boot. Отдельная ловушка: effect, который пишет `ui_state`, может преждевременно сохранить `screen: 'chat'` до завершения session restore и тем самым сам затереть корректно сохранённый `admin/jobs/profile` экран. Практический фикс: пока `booting=true` и auth ещё не восстановлен, не перезаписывай сохранённый экран дефолтом; сбрасывай в `chat` только после завершённого boot и подтверждённого неавторизованного состояния.
- для reload-приёмки screen persistence снимай двойной сигнал: (1) значение token-key и `ui_state` в `localStorage` до/после reload; (2) фактический экран после восстановления (`login` / `chat` / `admin`). Если `ui_state.screen='admin'`, а после reload приложение открылось в `chat` или на `login`, это уже не косметика навигации, а отдельный boot/session-state дефект.

Но не переоценивай `service-info`: он может подтвердить только базовый режим сервиса и не доказать, что живой процесс действительно работает с ожидаемой БД, env и новой логикой маршрута.

Поэтому для local-first backend после `service-info` делай ещё один слой проверки:
- посмотри, какой PID слушает порт;
- проверь `ps`/`/proc/<pid>/environ`, чтобы понять, с какими `HERMES_WEB_*` переменными живёт именно этот процесс;
- отдельно сверь фактический `DB_PATH`/data-dir с тем, что ожидает код;
- если нужно, открой живую DuckDB/SQLite и проверь наличие новых колонок/строк, а не только HTTP-ответы.

Для local-first контуров это критично: пустой `/jobs`, старая админка или «неработающие» новые endpoints могут быть следствием того, что браузер и тесты всё ещё ходят в старый процесс, а не в свежий код.

Отдельная ловушка: можно ошибочно объявить проблему «не тем runtime», хотя процесс и БД уже правильные. Если колонки/данные на месте, а endpoint всё равно даёт `500`, переключайся с проверки окружения на точечную отладку самого handler-а.

## 4. Для спорных визуальных жалоб сначала проверь самые дешёвые вещи

Например:
- цвет/контраст служебной метки;
- sticky/static поведение плашек;
- направление прокрутки;
- видимость и смысл кнопки;
- честность подписи источника данных.

Это часто даёт быстрый пользовательский эффект без архитектурной перестройки.

### Когда browser snapshot/vision врёт про layout

Для responsive/sticky экранов не полагайся только на snapshot или визуальное описание скриншота.

Обязательная проверка через DOM:
- `getComputedStyle(...)` для `display`, `gridTemplateColumns`, `flexDirection`, `position`, `bottom`, `overflow`;
- `getBoundingClientRect()` для соседних блоков, чтобы понять, стоят ли они реально рядом или уже ушли друг под друга;
- отдельная проверка scroll-host: где именно живёт прокрутка — у всей страницы, у `.content` или у внутреннего контейнера переписки.

Практический паттерн:
- если snapshot показывает только линейный порядок элементов, а пользовательская претензия про «рядом / не рядом», подтверждай вердикт координатами DOM, а не текстовым деревом accessibility;
- если vision говорит, что sticky composer «не виден», проверь его `position: sticky`, `bottom: 0` и реальные `top/bottom` координаты относительно viewport, потому что screenshot легко обрезает нижнюю область или показывает уже прокрученный кадр.

### Если после CSS/HTML-правки браузер живёт старым runtime

Не считай первый `F5` достаточным доказательством. Для local-first UI после правок возможен ложный дефект из-за кэша или старого runtime-состояния вкладки.

Надёжный порядок:
- открыть страницу заново, а не только жать `F5`;
- при необходимости использовать cache-busting URL вроде `/?v=...`;
- сравнить, что видит DOM после обычного reload и после fresh navigation;
- только после этого делать вывод, что layout-правка не сработала.

## 5. Для soft-status/select логики проверяй два разных инварианта

Если задача про `active / inactive / deleted`, не ограничивайся одним API-ответом или одной таблицей. Нужно отдельно подтвердить два сценария:
- **fresh choice** — новое поле выбора не должно предлагать inactive/deleted значения;
- **preserved choice** — уже сохранённое значение должно оставаться видимым в форме, даже если оно стало inactive/deleted.

Практический паттерн для проверки:
- сначала проверь список/summary, что inactive/deleted реально считаются и рендерятся;
- затем открой форму, где значение уже сохранено;
- если нужен быстрый runtime-probe без отдельной миграции тестовых данных, допустимо временно подменить `state.bootstrap.references[dataset].items` в `browser_console`, открыть нужную форму и посмотреть, как `referenceOptions(...)` и реальный `<select>` ведут себя для fresh/preserved сценариев;
- проверяй не только наличие значения, но и статусный suffix (`не активно` / `удалено`), если UX обещает такую пометку.

- Если спорный вопрос про "локально в UI или сохранено в backend"

Не делай вывод по одному только render-helper во frontend.

Надёжная последовательность:
- проверь, какой field реально используется для показа в UI: `display_name`, `alias`, `name` и в каком порядке приоритета;
- найди backend serializer и write-path: PATCH/POST endpoint, где это поле принимается и возвращается;
- по возможности подтверди round-trip через smoke/integration test или живой UI-сценарий;
- только после этого отвечай, что значение является общим backend-backed полем, а не local-only состоянием браузера.

Практическая причина: в local-first admin UI легко перепутать `display_name`, который хранится в БД и виден другим пользователям, с чисто визуальным alias или временным клиентским state.

- Если спорный вопрос звучит как `сохраняется ли название в backend или это local-only alias`, не отвечай по render-коду или по одному `localStorage`-ключу. Обязательная проверка для такого класса вопросов: (1) найти frontend priority order (`display_name` / `alias` / `name`); (2) найти backend serializer и write-path, где поле принимается и возвращается; (3) подтвердить round-trip, что после reload/другого клиента значение приходит обратно из API. Только после этого можно утверждать, что поле общее backend-backed, а не локальное UI-состояние.
- Для chat/file acceptance не ограничивайся route `200 OK` в вакууме. Проверь полный путь на реальном payload: список файлов или thread detail -> конкретный `id`/`attachment index` -> download route -> `Content-Disposition`/контент. Это защищает от ложной приёмки, когда route формально существует, но serializer не поднимает `attachments` наружу или download handler смотрит не в тот path-field (`local_path` vs `relative_path`).
- Если пользователь жалуется не на отсутствие download route, а на то, что `в файл попало не то содержимое`, проверяй target-selection backend-first на целевом сервере: `messages.meta.exported_message_id`, `attachments[].preview_excerpt`, фактический `message_kind=file_response` и соседние assistant messages в том же thread. Для export-path это отдельный класс дефекта: route и файл могут быть живы, но backend выбирает не тот source message.
- Если пользователь просил проанализировать вложение, а вместо ответа в чат получил сгенерированный файл, сначала проверяй не OCR, а intent-routing на export. Упоминание формата или имени файла вроде `ТЗ2.docx` не должно само по себе запускать `file_response`; нужен явный export-intent (`отправь файл`, `в docx`, `выгрузи`, `пришли документ`).
- Если жалоба звучит как `распозналось не всё` для DOCX/ТЗ, не считай `document.paragraphs` достаточным извлечением. Для acceptance такого класса файлов обязательно проверяй таблицы, header/footer и, если формат табличный, отдельный путь для `XLSX` по листам/строкам. Иначе backend может честно помечать `text_extracted=true`, но терять ключевую структуру документа.
- Отдельно разделяй `полноту извлечения` и `полноту контекста, реально переданного в LLM`. Даже при успешном extraction продукт может вести себя так, будто файл `не прочитался`, если в message context попал только укороченный `preview_text`, а полный `extracted_text` был потерян. Для UI превью допустимо оставлять короткий текст, но для model-path должен использоваться полный extracted payload в пределах backend-лимита, включая reuse уже загруженных файлов.
- Для export/download assistant-ответов отдельно различай `content answer` и `non-content assistant message`. Если последний assistant-turn — apology/limitation-реплика про собственные ограничения (`не могу создать .docx`, `пытался создать текстовый файл`, `прикрепить файл не могу` и т.п.), не считай её валидным export target. Надёжный repair-path — исключать такие сообщения из export-target selection и откатываться к последнему содержательному assistant-ответу.
- Когда пользователь явно говорит `подключись к серверу X и проверь backend`, не спорь с симптомом по косвенным UI/API признакам. Для этого класса file/export дефектов сначала иди прямо в целевой contour: SSH -> live DB/messages meta -> backend code path -> service restart -> повторная live-проверка на том же сервере.
- Для dashboard/export UI отдельно различай `настоящий file-download` и `print-to-PDF flow`. Если кнопка `PDF` реализована через `window.open(...)+print()`, сначала подозревай popup-блокировку, а не сам dashboard payload. Для local-first React UI более устойчивый repair-path — генерировать export HTML и печатать его через скрытый same-page `iframe`, а не через новое окно. В отчёте пользователю формулируй это честно: это `Печать / PDF` через системный print dialog браузера, а не обязательно прямой binary `.pdf` download.

- см. также `references/files-admin-api-fallback-acceptance.md` — backend-first приёмка для `files/chat attachments/admin charts/backend-vs-local-only`, когда визуальный browser-pass блокируется средой, но нужно честно подтвердить функциональность по live API и render contract.
- Для isolated CopilotKit / chat-runtime проверяй runtime не только через браузерный popup, но и прямым HTTP/SSE-путём.

Практический порядок:
- сначала подтвердить discovery-path: `GET /copilotkit/info` или single-route `POST /copilotkit { method: 'info' }`;
- затем подтвердить, что live single-route реально принимает `agent/run`, а не только выглядит поднятым;
- для `@copilotkit/runtime` v2 single-route не угадывай payload: `body` должен соответствовать `RunAgentInputSchema`, то есть минимально содержать `threadId`, `runId`, `messages`, `tools: []`, `context: []`;
- если `POST /copilotkit` возвращает `500` или странную ошибку валидации, сначала прогоняй тот же payload локально через `RunAgentInputSchema.parse(...)`, а уже потом спорь с моделью или SSE;
- для express-mount не режь base path дважды: если `copilotRuntimeNodeExpressEndpoint({ endpoint: '/copilotkit', ... })` уже знает свой route, `app.use(handler)` надёжнее, чем `app.use('/copilotkit', handler)`, иначе single-route может видеть неверный `req.url` и давать ложные `404` на `agent/run`;
- если browser/CDP слой недоступен, альтернативная приёмка считается валидной только после реального `POST /copilotkit` с `Accept: text/event-stream` и чтения первых событий вроде `RUN_STARTED`, `TEXT_MESSAGE_START`, `TEXT_MESSAGE_CONTENT`, `RUN_FINISHED`.
- если runtime падает не на chat-логике, а на telemetry-path вроде `_copilotkit_shared.lambdaClient.send is not a function`, не объявляй чат сломанным целиком. Сначала отключи telemetry через env (`COPILOTKIT_TELEMETRY_DISABLED=true`, при необходимости `DO_NOT_TRACK=1`) и повтори `agent/run`. Это относится к классу runtime-обходов, а не к продуктовой логике чата.
- если пользователь просит chat-first UX, не тащи в интерфейс визуальные артефакты CopilotKit (`Popup`, dev console, чужой vocabulary). Оставляй CopilotKit как внутренний runtime/provider слой, а вход делай через обычный Hermes-чат.
- для такого перехода сначала убери видимые CopilotKit-компоненты из `main.jsx`/root render, но сохрани provider/runtime wiring; затем переводи стартовые действия в backend-driven chat operations, а не в локальные frontend-only кнопки.
- backend-driven стартовые операции проверяй в два слоя: (1) seed/source-of-truth в коде; (2) текущая рабочая local DB. Для local-first MVP недостаточно обновить только `DEFAULT_REFERENCE_DATA`: existing DuckDB/SQLite может продолжать отдавать старые `starter_prompts`, пока не обновишь живую таблицу `reference_items`.
- для CopilotKit/dashboard acceptance не предполагай, что продуктовый вход всё ещё живёт в legacy popup/sidebar. Сначала сними живой DOM и найди фактический пользовательский вход. Если страница уже работает как chat-first shell, канонический сценарий приёмки должен идти через основной composer: отправить dashboard-запрос, дождаться `clarification_request`, затем `dashboard_result`/`dashboard-artifact`. Старые sidebar-селекторы в таком случае считай drift automation, а не доказанным продуктовым дефектом.
- если long browser-pass падает до UI-артефакта, сначала докажи backend-контракт прямым live API-вызовом на том же каноническом contour. Для dashboard flow минимальный порядок такой: (1) создать новый thread; (2) отправить первичный запрос на дашборд; (3) проверить `assistant_message.meta.message_kind`; (4) если это `clarification_request`, отправить `clarification_actions[0].prompt`; (5) подтвердить, что второй ответ вернул `dashboard_result` с непустым `dashboard`. Только после этого чини browser-smoke или frontend rendering.
- если `http://127.0.0.1:PORT/` отдаёт Vite HTML shell, но login form/app shell не появляется, не retry старый smoke вслепую. Считай это отдельным runtime-mount вопросом: HTML-сервер жив, но React UI может не смонтироваться или может рендериться не тот entry flow. Сначала проверь `#root`/`innerHTML`, фактический frontend PID/cwd и какой именно runtime уже держит порт; только потом делай вывод, что сломан сам feature-flow.
- после добавления нового runtime helper-поля в backend (`starter_prompt_cards` и т.п.) не считай helper достаточным доказательством. Проверь, что конкретный endpoint вроде `/api/bootstrap` реально прокидывает это поле в JSON-ответ. Частый скрытый разрыв: helper уже считает новый payload, а route по-прежнему вручную возвращает только старые ключи.
- если backend после патча будто бы `не меняется`, сначала проверь PID на порту и только потом код. Для local-first UI типичный ложный хвост — старый `python app.py` всё ещё держит порт, новый запуск падает на `Address already in use`, а ты продолжаешь тестировать старый payload.
- см. также `references/copilotkit-runtime-sidecar-notes.md` — минимальный рабочий payload, route-map, telemetry-обход и chat-first интеграционные заметки для local-first sidecar-проверки.
- см. также `references/copilotkit-chat-first-operations.md` — как перевести working CopilotKit runtime в backend-driven стартовые chat operations без popup/UI-артефактов.

- Если после крупного React/admin-рефакторинга кнопка или modal формально присутствуют в DOM, но пользовательский клик ничего не делает и `js_errors: []`, не считай это мелким browser glitch. Это отдельный класс дефекта: stale prop-path / broken wiring между root render, screen component и handler-ом.

Надёжная последовательность:
- проверь, существует ли сам modal/state/handler в коде;
- отдельно проверь, прокинут ли нужные props именно в текущем root render или screen wrapper;
- если accessibility click формально успешен, а экран не меняется, сними через DOM/console список кнопок и адресно проверь `hasHandler`-контур, а затем перечитай точный render-фрагмент компонента, который рендерится на живой странице;
- только после этого делай патч по wiring. Наличие `useState(...)`, `handleOpen...` и JSX modal-компонента по отдельности ещё не доказывает, что пользовательский путь реально подключён.
- Для jobs/admin экранов отдельно проверяй final root render на drift имён обработчиков. Практический анти-паттерн: screen получает пропсы вроде `handleOpenCreateJob` / `handleOpenEditJob` / `handleOpenRecipientsModal`, а в `App.jsx` реально существуют только `openCreateJob` / `openEditJob` / `openRecipientsPicker`. В таком случае `vite build` остаётся зелёным, но live runtime падает уже при открытии экрана. Для приёмки такого класса задач недостаточно grep по handler-ам: нужно проверить точный JSX вызов screen-компонента и потом открыть экран живьём.
- Отдельный runtime smell для admin-вкладок: кнопка или tab есть в navbar, но при открытии конкретного экрана прилетает `ReferenceError` на пропе/handler-е (`onSaveNotice={handleSaveChatNotice}` при существующем `handleSaveNotice` и т.п.). В таком случае не закапывайся сразу в роли/viewport — сначала сверяй точный root render и console после открытия вкладки.

- Для split-contour выкладки не считай `systemctl restart` достаточным доказательством. После перезапуска frontend surface обязательно проверь три сигнала именно на целевом origin: (1) `systemd --user` unit активен и получил новый `MainPID`; (2) live `index.html` на пользовательском порту ссылается на ожидаемый свежий bundle (`/assets/index-*.js` / `.css`); (3) хотя бы один критичный пользовательский flow подтверждён Playwright/DOM-проходом уже на этом боевом surface, а не только на локальном dev-порту.

- Для create/edit modal в admin UI проверяй live не только факт открытия, но и обязательные поля. Недостаточно текста-подсказки вида `Email, пароль и имя обязательны`.

Минимальная приёмка:
- открыть modal в runtime;
- сделать пустой submit или адресный submit без одного обязательного поля;
- подтвердить, что UI показывает человекочитаемую ошибку;
- если обязательных полей несколько, не подменяй это выводом `валидация есть вообще`. Зафиксируй, покрыта ли каждая обязательность (`email`, `password`, `name`) и как именно это видно пользователю.

Дополнительный приём для parity-сравнения:
- если стандартный smoke использует старые legacy selectors, не заставляй новый React/UI-контур искусственно под них подстраиваться;
- лучше сделай отдельный React-specific acceptance script или targeted probe под фактические роли/лейблы/DOM-инварианты нового интерфейса;
- иначе можно получить ложный вывод "React flow сломан", хотя сломан только старый тестовый контракт.

## 7. Для isolated React/Vite веток сначала подтверждай реальный build/run entrypoint

В React-миграциях не предполагай, что `package.json` лежит рядом с `src/`.

Надёжная последовательность:
- сначала найди `vite.config.*` и проверь `root`;
- отдельно найди, где реально лежит `package.json` и какие npm scripts определены;
- не предполагая наличие стандартного `build`, сначала прочитай фактические scripts (`react:build`, `ui:smoke`, `react:dev` и т.п.), и только потом запускай нужную команду;
- если sources лежат, например, в `services/frontend-react/`, а `package.json` и `vite.config.js` — в корне копии проекта, то build нужно запускать из корня (`npm run react:build` или эквивалент), а не из source-подкаталога.

Это защищает от ложного вывода, что React-контур «не собирается», когда на самом деле ошибка была не в коде, а в неверно угаданном script name или поверхности запуска.

### Если dev-server не поднялся, потому что порт уже занят

Не смешивай два разных утверждения:
- `я успешно подняла свежий dev-runtime`;
- `на этом порту уже есть живой runtime, и я проверяю именно его`.

Практический порядок:
- если `npm run dev`/`vite` отвечает `Port ... is already in use`, сначала проверь, отвечает ли этот порт вообще;
- если страница на порту уже открывается, считай это существующим runtime и отдельно зафиксируй, что новый процесс не стартовал;
- parity-проверку можно продолжать против существующего runtime, но финальный вывод должен явно различать `existing live runtime verified` и `fresh dev instance started by me`;
- если нужна именно чистая верификация свежего кода, либо освободи порт, либо подними инстанс на другом порту.

Это снижает риск ложной приёмки, когда агент думает, что тестирует свежий dev-server, а на деле смотрит на давно живущий процесс.

### Для быстрого parity-pass перед следующей задачей режь объём до high-ROI зон

Если пользователь просит «доделать быстро, чтобы не блокировать следующий эксперимент», не пытайся одинаково глубоко полировать весь UI.

Практический паттерн:
- сначала зафиксируй 2–4 самые дорогие зоны parity-разрыва;
- для React admin/jobs обычно максимальный ROI дают `admin users contour` и `jobs detail contour`, а не общий redesign;
- после адресных правок обязательно раздели три уровня проверки: `build green`, `live runtime visible`, `critical screens accepted`;
- если эти зоны уже живы и без JS errors, можно честно считать runtime достаточно рабочим для перехода к следующему эксперименту, даже если отдельный visual polish `8.5+` ещё остаётся отдельной темой.

## 8. Если browser-smoke упёрся в Playwright/system runtime, переключайся на live DOM verification

См. также `references/react-parity-runtime-checklist.md` — короткий checklist для случаев, когда legacy UI сверяется с параллельной React/Vite поверхностью и нужно честно разделить `build green`, `runtime visible` и `deep flows verified`.
- `references/chat-runtime-debugging-patterns.md` — приоритетный acceptance-order для chat-регрессий, hidden auth-write conflicts на boot и практические проверки file-send/file-receive.
- `references/chat-queue-restart-recovery.md` — как отличать потерю chat-задачи после reboot от downstream timeout и как чинить recovery для задач, застрявших в `running`.
- `references/chat-pending-refresh-vs-backend-completion.md` — как отделять backend-completed chat task от зависшего frontend pending-state, если UI перестал опрашивать thread раньше фактического завершения модели.
- `references/chat-message-timestamp-semantics.md` — как диагностировать и чинить случай, когда assistant bubble показывает время placeholder/request, а не реальное время завершения ответа.
- `references/chat-export-request-timeout-diagnosis.md` — как разбирать случаи, когда chat bubble показывает `Не удалось получить ответ`, а реальная первопричина сидит в `chat_tasks.last_error`, gateway tool-flow и отсутствии штатного export-path для Word/docx-подобного запроса.
- `references/export-runtime-acceptance-and-bundle-verification.md` — layered acceptance для export/download-фич: live backend round-trip по форматам, bundle-proof на production frontend и cleanup временного acceptance-аккаунта, если headless UI частично блокируется средой.
- `references/react-admin-roundtrip-stale-detail-and-policy-hydration.md` — как отличать backend-green path от двух живых UI-дефектов: пустой policy overview при непустом `data_sources` и stale jobs detail после `pause`.
- `references/backend-json-and-model-routing-roundtrip.md` — что проверять, когда frontend жалуется на `Сервис вернул не JSON (500)`, а задача затрагивает backend error-contract, `llm_routing`, chat model selector и сохранение `request_policy` в очереди.
- `references/duckdb-auth-hot-path-and-systemd-port-conflicts.md` — как не спутать фронтовую нестабильность с DuckDB auth hot-path writes и конфликтом manual runtime vs `systemd --user` owner на тех же портах.
- `references/react-session-restore-and-json-contract.md` — как отличать реальное истечение сессии от ложного logout из-за boot-catch path, как проверять PID/cwd/env живого backend на порту и как нормализовать user-facing реакцию на HTML вместо JSON.


Если smoke-script падает из-за missing shared library, headless browser startup или другой setup-state проблемы среды, не объявляй приложение сломанным автоматически.

Рабочий fallback:

## 8.1 Разделяй native browser/runtime failure и app-runtime failure

Когда Playwright smoke ломается рано, явно отделяй три слоя, а не лечи всё как одну браузерную проблему.

- Если финальный визуальный pass блокируется именно средой browser runtime, не подменяй честную приёмку ложным screenshot-вердиктом. Для local-first UI допустимо закрыть функциональный контур по более надёжной связке: живой backend payload -> serializer/write-path -> frontend render/open wiring -> прямой API smoke по тем же сущностям. Это особенно важно для экранов `files`, chat attachments и admin mini-charts, где пользователь спрашивает не про красоту, а про факт: `данные есть?`, `открывается?`, `это backend-backed или local-only?`.
- В таком fallback-режиме разделяй два вывода:
  - functional acceptance: подтверждено ли, что поток реально работает по API и UI-контракту;
  - visual acceptance: подтверждён ли именно внешний вид экрана браузером/скриншотом.
- Если первое подтверждено, а второе заблокировано нативным browser crash, так и пиши пользователю: функционально принято, визуальная headless-приёмка ограничена средой.

1. Native browser/runtime dependencies.
- Сначала подтверди, что сам browser binary стартует.
- Если Chromium/Playwright падает на missing shared libraries, это системный runtime-слой, а не дефект приложения.
- После фикса библиотек обязательно перепроверь `ldd` и минимальный browser launch до правок в app code.

2. App transport/runtime wiring.
- Во время local-first runtime-проверки убирай лишний cross-origin там, где стек уже позволяет same-origin путь.
- Для embedded runtime вроде CopilotKit предпочитай локальный путь вида `/api/copilotkit`, если фронт и backend уже живут в одном контуре.
- Если browser уже стартует, а `copilotkit/info` даёт 4xx/5xx, это уже не native dependency issue; переходи к backend/runtime debugging.

3. Auth/app-shell crash after login.
- Если анонимная загрузка страницы работает, а browser закрывается после логина, воспроизведи это минимальным Playwright-probe: открыть страницу -> заполнить login form -> submit -> wait.
- Если такой минимальный probe стабильно даёт `page closed` или `browser disconnected`, не продолжай бесконечно переустанавливать browser deps. Это уже application boot/runtime defect.
- Дальше коррелируй момент закрытия страницы с backend request log и endpoint-ами, которые дёргаются сразу после auth/session restore.

## 8.2 Используй изолированную local-first пару frontend/backend для runtime-приёмки

Если основной dev-контур шумный, общий или уже загрязнён старыми процессами, не дебажь всё только на исходных портах.

Рабочая схема:
- поднять fresh backend на новом порту;
- поднять fresh frontend на соседнем порту, смотрящий только в этот backend;
- прогнать тот же минимальный Playwright/auth probe и тот же smoke уже по изолированной паре.

Это даёт важный диагностический разворот:
- если изолированная пара работает, проблема вероятнее в исходном процессе/env state;
- если изолированная пара ломается так же, проблема уже в code path или app boot logic.

## 8.2.1 Если post-login crash локализовался до chat/composer, проверь layout-механику shell, а не только React-логику

Если binary search уже сузил проблему до authenticated chat/composer screen, не останавливайся на выводе `падает textarea` или `ломает Sidebar`.

Отдельный durable-паттерн проверки:
- сравни один и тот же editable control в трёх контейнерах: без sidebar, со stacked-layout и в настоящем двухколоночном shell;
- если `textarea` живёт без sidebar и в stacked-layout, но падает рядом с боковой колонкой, подозревай не input-логику, а layout;
- для desktop auth-shell отдельно проверь, что именно используется: `display: grid` или `display: flex`;
- если двухколоночный `grid` стабильно роняет headless Chromium после логина, а эквивалентный `flex`-shell живёт, не продолжай лечить composer как компонентный баг. Это structural layout issue, и правильный следующий шаг — перевод shell на безопасный `flex`-контур с сохранением product-level UI.

Что важно не перепутать:
- `Sidebar` сам по себе может быть невиновен;
- `textarea` сама по себе может быть невиновна;
- виноватым может быть именно их соседство внутри authenticated two-column grid shell.

Практический вывод для local-first React UI:
- сначала докажи, что виноват layout-класс (`app-layout`/эквивалент), а уже потом переписывай composer;
- если `grid -> flex` снимает headless crash, предпочитай этот fix урезанию UI вроде замены `textarea` на `input`, скрытия sidebar или перехода на stacked desktop-layout.

## 8.3 Учитывай DuckDB lock conflicts при многопроцессной local verification

Для local-first backend на DuckDB параллельные backend-процессы могут давать нестабильные `500` на setup/auth-adjacent endpoints просто из-за shared DB lock, а не из-за frontend-логики.

Проверочное правило:
- если health в целом жив, но `setup/status` или соседние boot-endpoint-ы иногда дают `500`, сначала проверь backend logs на DuckDB lock conflict.

Практический verification workaround:
- для изолированной runtime-проверки подними свежий backend на копии DuckDB через env var пути к БД, чтобы acceptance run не конкурировал с основным процессом.
- Это именно tactic для verification/isolation, а не продуктовый permanent fix.

## 8.4 Что сохранять из такого инцидента

Сохраняй не машинно-специфичный список недостающих пакетов, а устойчивую последовательность диагностики:
- native libs -> same-origin runtime wiring -> minimal auth probe -> backend logs -> isolated frontend/backend pair -> isolated DB copy при DuckDB lock.

Рабочий fallback:
- отдельно подтвердить build (`vite build` / production bundle);
- отдельно подтвердить, что live runtime открывается и показывает реальные backend-данные;
- для регрессий в prod сначала сверить не симптомы, а сам live artifact: service `MainPID`, фактически запущенный файл/путь, hash или другой сильный version-signal (line count, build asset names), и runtime driver/storage mode в env/logs процесса;
- если контур split, не считать одинаковые `unit name` или `file path` доказательством корректной выкладки: сначала сравнить локальный и remote artifact identity, особенно после рестартов, ручных `scp` и частичных deploy;
- продолжить parity-проверку через Hermes browser tools: пройти экраны `chat/profile/jobs/admin`, снять snapshot и отделить "экран рендерится" от "flow end-to-end подтверждён";
- в промежуточном выводе честно разделить три уровня уверенности: `build green`, `runtime visible`, `deep flows verified`.

Дополнительный durable-паттерн для local-first Playwright/Chromium:
- если browser binary не стартует, сначала проверь `ldd` и `--version`, затем попробуй уже существующий user-space overlay из `~/.hermes/browser-libs/root` через `LD_LIBRARY_PATH="$LIBROOT/usr/lib/x86_64-linux-gnu:$LIBROOT/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"`;
- это setup-state fix, а не доказательство поломки приложения; после успешного старта браузера возвращайся к live UI acceptance, а не останавливайся на системной диагностике.
- если headless runtime `document.body.innerText` пустой или неполный, но DOM и `textContent` нормальные, для smoke/assertions переходи на `textContent` или на targeted selectors вместо `innerText`;
- если задача про export/download assistant- или dashboard-артефактов, а headless browser частично блокируется, не ставь verdict только по browser-pass. Для этого класса задач acceptance надо разделять на три слоя: (1) live backend round-trip по каждому формату и unsupported-format path; (2) proof, что production frontend уже обслуживает свежий bundle с export-wiring; (3) отдельно — получилось ли подтвердить сам UI click-flow. Если слой (1) и (2) зелёные, а (3) упёрся в browser runtime, фиксируй это как ограничение visual acceptance, а не как неподтверждённость всей feature.
- если проверка зависит от последнего assistant-turn в chat-first UI, используй свежий новый чат: длинный исторический thread даёт ложные совпадения и ложные падения из-за старых dashboard artifacts, clarification-блоков и предыдущих ответов;

- сначала отделяй системный browser-runtime блокер от прикладного runtime/UI дефекта;
- если `chrome-headless-shell` или Playwright падает на missing `.so`, сначала закрой именно нативные зависимости и перепроверь бинарь отдельно через `--version`/`ldd`, а уже потом делай выводы про само приложение;
- если root/`sudo apt install` недоступен, допустим user-space overlay: скачать нужные `.deb`, распаковать их в локальный каталог и запустить smoke с временным `LD_LIBRARY_PATH` только для тестового процесса;
- после этого обязательно сделай вторую развилку диагностики: если браузер уже стартует, но smoke всё ещё падает, перестань лечить ОС-зависимости и переключись на console/network/runtime path.
- если первый probe падает не на запуске браузера, а на selector mismatch (`locator.fill timeout`, пустой CopilotKit popup, не найден старый placeholder), сначала сними реальную DOM-карту страницы: какие `textarea`, `button`, `input`, `main`/`#root` реально существуют, какой у них placeholder/text/class, и только потом перенастраивай probe. Для chat-first контуров это особенно важно: не предполагай наличие CopilotKit popup-селекторов, если продукт уже работает через обычный composer.
- если страница уже рендерится и пользовательский поток подтверждается через DOM и network events, а screenshot/Fontconfig падает позже отдельным headless-crash, не откатывай verdict до `не проверено`. В таком случае честно фиксируй: browser runtime жив, flow подтверждён DOM/HTTP-сигналами, screenshot-path остаётся нестабильным как отдельный технический хвост.

Для React/Vite + встроенного runtime отдельно проверяй same-origin wiring:
- если frontend формально открывается, а в консоли идут ошибки на `copilotkit/info` или похожий runtime discovery path, сначала проверь не только код `main.jsx`, но и реальные env/run-script defaults (`VITE_*`, shell-entrypoint, proxy target в `vite.config.*`);
- не считай относительный runtime path доказанным, пока не сверишь, что живой dev-server не переопределяет его жёстким `http://127.0.0.1:PORT/...` из entrypoint-скрипта;
- для local-first preview предпочитай same-origin путь вроде `/api/copilotkit` через существующий Vite proxy, а не отдельный cross-origin sidecar, если задача — product-like приёмка UI, а не изоляционное тестирование runtime;
- если после перевода на same-origin CORS исчез, но `GET /api/copilotkit/info` даёт `501`, это уже не browser/runtime проблема. Фиксируй её как backend preview/runtime gap и чини route/metadata-endpoint отдельно от Playwright.

Это особенно важно для формулировок вроде «React-версия не деградирует»: такое утверждение допустимо только после третьего уровня, а не после одного лишь зелёного build или открывающихся экранов.

- см. также `references/playwright-local-runtime-overlay.md` — двухступенчатая схема: user-space overlay для missing libs, затем same-origin/runtime-path диагностика для React/Vite preview.
- см. также `references/playwright-user-space-overlay-and-dom-acceptance.md` — как дотянуть Playwright до живого запуска без root-доступа, а затем принять сценарий по DOM и network signals, даже если screenshot-path остаётся нестабильным.
- см. также `references/headless-auth-shell-binary-search.md` — как локализовать post-login headless crash через binary search по authenticated shell: `auth ok` -> sidebar -> screen -> messages/composer -> минимальный `textarea`.
- см. также `references/headless-grid-vs-flex-auth-shell.md` — как отделить ложный «падает textarea/чат» от реального layout-конфликта authenticated shell, когда headless Chromium ломается именно на двухколоночном CSS grid, а эквивалентный flex-shell живёт.

### Когда monolithic smoke уже мешает больше, чем помогает

Если один длинный smoke-script проходит через chat, profile, jobs и admin подряд, не держись за него любой ценой.

Типичный класс ложных падений:
- strict-mode ambiguous locators в Playwright;
- одинаковые тексты в истории чата или в list/detail одновременно;
- повторно накопленные smoke-данные, из-за которых `getByText(...)` и похожие ожидания становятся двусмысленными;
- таймеры `waitForTimeout(...)`, которые ломаются от естественного runtime jitter.

Практический паттерн:
- после 1–2 таких сбоев не retry тем же способом;
- переходи на targeted acceptance-pass с уникальными маркерами (`timestamp`/unique email/job/message);
- жди не абстрактный timeout, а конкретный инвариант экрана;
- проверяй важные write-path'ы двойным критерием: UI visibility + backend round-trip (`GET /resource/<id>` или список).
- для React jobs/admin не завязывайся только на старый detail-text assert, если живой экран уже эволюционировал. Надёжный fallback: выбрать `.job-card` по уникальному `hasText`, кликнуть по самой карточке и подтвердить structural signal (`job-card active`) даже если текст detail-panel меняется или рендерится асинхронно. Если такой targeted probe проходит, а длинный monolithic smoke всё ещё падает на role/text selectors, фиксируй это как smoke-maintenance хвост, а не как автоматическое доказательство product defect.

### Если live UI один раз увидел `500`, а test_client на том же коде даёт `200`

Не объявляй путь автоматически исправным и не объявляй его автоматически сломанным.

Это отдельный класс mixed-runtime сигналов:
- возможно data-dependent состояние;
- возможно race/ordering только в живом web-runtime;
- возможно UI сделал дополнительный follow-up request, которого не было в упрощённой server-side репродукции.

Правильная реакция:
- зафиксировать route(ы), которые дали `500` в live runtime;
- отдельно воспроизвести их через `test_client()` или прямой API call;
- разделить вывод на два уровня: `backend handler reproduces cleanly` vs `live runtime still sees intermittent/bounded failure`;
- не закрывать parity только на основании одного из этих двух сигналов.

## 9. Для admin logs/operations принимай рабочий путь даже на пустых данных

Пустая лента событий не делает runtime-проверку бессмысленной.

Подтверди отдельно:
- что фильтр даты-времени реально меняет `state` и query params;
- что экран честно показывает применённый период;
- что `export=csv/json` проходит по тому же backend-path и даёт пользователю success-сигнал;
- что UI не падает и не производит JS errors, даже если список пуст.

Это позволяет честно принять сам admin workflow, не дожидаясь специально подготовленных данных.

# Критерии приёмки

Не считай задачу закрытой, пока не подтверждено:
- страница действительно рендерит app shell после логина;
- спорный экран виден в браузере;
- ключевой пользовательский сценарий проходит руками или smoke;
- визуальные жалобы проверены по месту, а не логически «должны быть исправлены»;
- если есть mixed-source данные, UI честно показывает источник и ограничения.

# Что писать пользователю

Разделяй ответ на 4 части:
1. Что исправлено в коде.
2. Что проверено в живом runtime.
3. Что пока блокируется и чем именно.
4. Какой следующий шаг логичнее: UI/runtime, backend, smoke или журнал решений.

# Паттерны, которые стоит запомнить

- Для этого класса задач «код изменён» не равно «UX исправлен».
- Если пользователь жалуется на читаемость, это не косметика: это приёмочный критерий.
- Если startup неустойчив, сначала стабилизируй вход в интерфейс, потом проверяй остальной UI.
- Для local-first MVP переиспользуй текущий backend/frontend контур и имеющийся bridge/adapter, а не строй новый слой только ради проверки.

# Пересечения

Навык частично пересекается с существующими umbrella-навыками про local-first web UI cleanup и turnkey local-first MVP delivery. Если в библиотеке уже есть редактируемый umbrella для этих тем, этот навык можно позже слить в него как раздел про runtime-first UI verification и приёмку по живому интерфейсу.
