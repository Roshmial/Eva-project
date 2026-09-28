---
name: hermes-web-user-facing-ui-hardening
description: "Доводит user-facing Hermes Web UI до продуктового состояния: убирает contract/debug шум, правильно раскладывает files surfaces и проверяет live bundle/runtime без подмены визуальной приёмки абстрактными build-ами."
---

# Когда применять

Используй этот skill, когда нужно:
- исправить Hermes Web chat UI, recurring/file result cards, profile/files surfaces;
- сравнить текущий user-facing UX с эталонным скрином или жалобой пользователя;
- убрать из интерфейса служебные поля контракта (`result kind`, `output mode`, debug/status chips);
- переделать размещение файлов, preview и повторного использования;
- честно проверить, доехал ли новый frontend bundle и живой runtime path.

# Главные продуктовые правила

1. Default UI должен показывать пользователю результат, а не внутренний контракт.
   - Не выводи в обычном режиме поля вроде `Тип результата`, `Режим вывода`, `Причина`, `Получатели`, `Доставка`, если они не нужны для действия пользователя.
   - Не дублируй статус несколькими слоями одновременно.
   - Не оставляй пустые bubble-placeholder'ы вроде `…`, если реальный контент вынесен в card.

2. Для text-only и status paths приоритет — читаемость.
   - Один понятный статус лучше, чем несколько похожих блоков.
   - Running/pending сообщения не должны выглядеть как debug dashboard.

3. Files UX раскладывай по поверхности, а не по удобству реализации.
   - Файлы конкретного диалога должны открываться как отдельная вкладка/панель внутри чата по кнопке.
   - Не прячь thread files в composer file picker как основное место доступа.
   - Не делай постоянный side panel, если пользователь ждёт chat-internal surface.
   - В profile/files показывай единый user-level список файлов по всем диалогам, а не только активный чат.

4. Preview и tags — это вторичный, но реальный user-facing слой.
   - Если backend уже отдаёт `preview_summary`, `preview_lines`, `file_surface`, `thread_file_role`, их нужно рендерить, а не терять.
   - Preview должен помогать понять содержимое файла, а не раздувать карточку.

5. Будь устойчив к drift'у backend payload, особенно в thread/files и recurring delivery.
   - Если `GET /api/threads/<id>` не отдал top-level `thread_files`, не считай это автоматически «нулём по файлам».
   - Сначала проверь `messages[].meta.attachments` и собери thread-level files оттуда как fallback, сохранив `assistant_generated`, `preview_*`, происхождение и роль файла.
   - Для recurring/file-result сообщений не запихивай весь digest/summary в короткий headline card'а.
   - Если summary содержит служебный reasoning-пролог или плоский semicolon-список (`- title; channel; date; link; summary; links`), вынеси короткий заголовок отдельно, а тело переформатируй в читаемый markdown-блок.
   - Хвосты вроде `Файл приложен к сообщению.` убирай из основного digest body и оставляй файл отдельной карточкой/действием.

# Рабочая схема

1. Сначала зафиксируй жалобу пользователя как продуктовые требования.
   - Что именно выглядит «не так».
   - Что является целевым UX.
   - Что считается служебным шумом.

2. Потом разложи проблему на 4 слоя:
   - frontend renderer logic;
   - CSS/layout;
   - backend payload semantics (`thread_files`, `attachments`, `preview_*`);
   - live runtime / bundle delivery.

3. Проверяй renderer path адресно.
   - Ищи в `App.jsx` функции вроде `renderRecurringSummary`, `messageDisplayText`, `renderAssistantContractStrip`, `MessageBubble`, `ThreadFilesPanel`, `ProfileScreen`.
   - Для files surfaces отдельно проверь, как грузятся `userFiles`, `threadFiles`, `activeThreadId`, `profileSection`.

4. После правок обязательно проверь:
   - `npm run react:build`
   - целевой backend regression test на affected contract
   - что live URL реально отдаёт новый asset bundle
   - что в bundle есть новые маркеры текста/компонентов
   - что feature действительно доведена end-to-end, а не существует только как half-wired backend/frontend fragment

5. Для markdown regressions проверяй не только renderer, но и классификацию rich-text path.
   - Если UI «уронил md», проблема может быть не в самом markdown renderer, а в том, что сообщение перестало распознаваться как markdown и ушло в plain-text path.
   - Для Hermes Web отдельно проверяй детекторы вроде `looksLikeRichRecurringBody(...)`: они должны ловить не только bold/list/headings, но и markdown-таблицы, fenced code blocks и blockquote.
   - Если уже чинили `<br>`/table rendering, не считай это достаточным: отдельно проверь, что таблица вообще попадает в markdown path.
   - Отдельно проверяй переход `вводный абзац → markdown-таблица`. Типовой баг: parser жадно продолжает собирать paragraph block и не останавливается перед строкой, которая является заголовком таблицы (`| ... |` + separator line ниже). В таком случае проблема не в отсутствии markdown-path и не в table CSS, а в block segmentation внутри `renderMarkdownContent(...)`.
   - Не делай широкую правку уровня «отключить markdown для обычных сообщений», пока не проверил, что баг не локализуется в переходе между блоками. Если у пользователя есть разметка и жалоба звучит как «таблица начинается не там / пихается сразу», сначала проверяй paragraph termination rules.
   - Если пользователь сообщает, что live UI всё ещё сломан после локального regex/эвристического фикса, не продолжай бесконечно латать самописный markdown parser точечными условиями. Для mixed-content ответов вида `paragraph + hr + heading + table + list` быстро переходи на token-based markdown parsing (например, `marked`/lexer в текущем локальном фронтенде) и валидируй структуру именно на реальных проблемных сообщениях.
  - Отдельно проверь pre-parse normalization helpers вроде `stripCitationArtifacts(...)` или других text-cleanup функций. Если там используется что-то уровня `replace(/\\s{2,}/g, ' ')`, фронт может уничтожить `\n\n` и block boundaries ещё до `marked.lexer(...)`. В таком случае пользователь увидит один giant paragraph, а `---`, `###` и markdown-таблицы останутся сырым текстом внутри него. Для этого класса дефекта безопаснее схлопывать только горизонтальные whitespace-символы и отдельно ограничивать серии пустых строк. См. `references/frontend-whitespace-markdown-collapse-2026-06-25.md`.
  - После такого фикса не закрывай задачу по одному только `npm run react:build`. Обязательно сделай live DOM-проверку на реальном user-facing сообщении: сравни, что раньше всё сидело в одном `message-md-paragraph`, а после правки появились отдельные `hr`, `message-md-heading-*`, `message-md-table`, `message-md-list`. Это особенно важно, когда пользователь уже потерял доверие из-за прежних заявлений "всё сделано и проверено".
  - После такого фикса не закрывай задачу по одному только `npm run react:build`. Обязательно сделай live DOM-проверку на реальном user-facing сообщении: сравни, что раньше всё сидело в одном `message-md-paragraph`, а после правки появились отдельные `hr`, `message-md-heading-*`, `message-md-table`, `message-md-list`. Это особенно важно, когда пользователь уже потерял доверие из-за прежних заявлений "всё сделано и проверено".
   - После перехода на token-based parser отдельно проверь сохранение переносов строк в paragraph/list блоках. Типовой регресс: рендер брать из `token.text`, а не из более близкого к исходнику `token.raw`, из-за чего digest/summary схлопывается в один массив текста и теряет визуальные абзацы.
   - Не сужай markdown-path для assistant replies слишком агрессивно. Если user-facing ответы содержат таблицы, переносы, списки и rich recurring text, правка уровня «assistant message goes plain unless detector sees obvious markdown» легко ломает KPI/digest-чаты. Для Hermes Web безопаснее считать assistant text markdown-capable по умолчанию и отдельно чистить только шум/служебные прологи.
   - Для проверки именно «всё сообщение ушло в таблицу» снимай не только текст жалобы, но и block structure проблемного live message: какие токены/блоки parser видит (`paragraph`, `heading`, `table`, `list`, `hr`). Если parser даёт правильную последовательность, а пользователь всё ещё видит старое поведение, следующая гипотеза — stale live bundle/runtime, а не очередной parser tweak.

6. Для file/export UX проверяй всю цепочку формата, а не одну функцию-builder.
   - Недостаточно иметь `build_message_export_<format>(...)` в backend: формат должен быть включён в allowed formats, alias normalization, MIME map, request-format detection, stream builder и regression tests.
   - Если пользователь просит legacy/человеческое имя формата (`doc`, `xls`, `jpg`), для user-facing UX допустим alias на реальный поддержанный контейнер (`docx`, `xlsx`, `jpeg`), но это должно быть оформлено честно и стабильно в server-side normalization.
   - Для image/text-like exports (`png`, `jpeg`, `py`) проверяй не только `/export`, но и generated-file request path, если продукт поддерживает сценарий «сформируй новый ответ и сразу дай файлом».

7. Если backend уже отдаёт user-facing поле, сначала отрендерь его, а не придумывай новую семантику.
   - Для `Jobs`/`Детали задачи` сначала проверь, не приходит ли уже `owner` в list/detail payload.
   - Если поле уже есть, добавляй его в UI напрямую; не плодите отдельные вычисления или дублирующий API only because it was overlooked in frontend.

5. Не подменяй live acceptance ложным `exit 0`.
   - Если browser automation попал не в тот экран, это не визуальная приёмка.
   - Если login/reload path развалился, так и зафиксируй: bundle доехал, runtime API жив, но final screen acceptance блокируется auth/bootstrap choreography.

# Проверки, которые почти всегда нужны

- Сборка frontend:
  - `npm run react:build`

- Подтверждение нужных маркеров в live asset:
  - скачать `index-*.js` с живого frontend URL
  - проверить наличие строк-маркеров через простой script/curl/python

- Backend contract на thread files:
  - сначала проверить, отдаёт ли `GET /api/threads/<id>` top-level `thread_files`
  - если нет, отдельно проверить `messages[].meta.attachments` и решить, нужен ли frontend fallback-aggregator
  - проверить, что не теряются и user files, и assistant result files / message attachments

- Backend contract на recurring/file delivery:
  - проверить, не приходит ли в `recurring_summary.summary` / `status_detail` reasoning-пролог вместо чистого user-facing текста
  - reasoning-note нужно чистить в двух местах: в backend `display_text`/summary sanitation и во frontend recurring fallback path; иначе он может исчезнуть в одном сценарии и снова пролезть в digest в другом
  - если приходит semicolon-список, нормализовать его во frontend в читабельный блок, а не показывать сырьём одной строкой

- Если UI кажется пустым:
  - отделить «новый bundle не доехал» от «bundle доехал, но runtime/bootstrap/auth path не поднял экран»

# Чего не делать

- Не объявляй задачу закрытой только потому, что build зелёный.
- Не тащи в default UX backend contract semantics «для прозрачности».
- Не смешивай profile files и thread files в одну поверхность, если у них разные задачи.
- Не считай browser pass валидным, если automation пришёл в blank/login/skeleton state.

# Что сохранять после таких задач

- В decision-log фиксируй:
  - какой user-facing UX признан целевым;
  - какие surfaces должны существовать отдельно;
  - что именно считается contract/debug noise.

- Если родился конкретный session-specific набор симптомов и проверок, положи его в `references/` этого skill.

# References

- См. `references/sprint-1-3-ui-hardening-2026-06-24.md` — конкретные уроки по Hermes Web Sprint 1–3: files tab inside chat, all-files profile surface, compact recurring/text-only rendering, runtime verification pattern.
- См. `references/thread-files-and-digest-hardening-2026-06-24.md` — fallback aggregation of thread files from message attachments, recurring digest cleanup/reformatting, and asset/API proof when browser-based visual acceptance is blocked.
- См. `references/sprint3-export-markdown-lifecycle-2026-06-24.md` — Sprint 3 lessons: markdown rich-path detection, end-to-end export-chain verification, alias normalization for formats, and surfacing already-available backend fields like job owner.
- См. `references/markdown-table-transition-regression-2026-06-24.md` — узкий regression class: markdown есть, но parser склеивает вводный paragraph с последующей таблицей вместо отдельного `paragraph -> table` перехода.
- См. `references/live-markdown-kpi-regression-2026-06-25.md` — live-case с mixed markdown (`paragraph + hr + heading + table + list`), где правильный следующий шаг — проверить block sequence на реальном сообщении и при необходимости перейти с regex parser на token-based markdown parsing, а затем подтвердить live bundle delivery.
- См. `references/assistant-markdown-and-reasoning-digest-regression-2026-06-25.md` — регрессия, где слишком узкий assistant markdown-path ломает таблицы/переносы, а reasoning-note нужно чистить одновременно в backend display_text и frontend recurring fallback.
