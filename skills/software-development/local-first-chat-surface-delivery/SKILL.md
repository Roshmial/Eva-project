---
name: local-first-chat-surface-delivery
description: "Доведение chat-first local-first web-интерфейсов до рабочего состояния: scroll/sticky layout, structured message artifacts, backend/frontend wiring и обязательная live-проверка."
---

# Когда использовать

Используй этот навык, когда нужно менять или чинить chat-first web UI в local-first контуре, особенно если задача затрагивает:

- вкладку чатов, ленту сообщений, composer, sticky header/nav;
- специальные типы сообщений или artifacts в чате;
- локальные dashboard/analytics flows, встроенные в чат;
- связку backend `message.meta` -> frontend renderer;
- приёмку через реальный runtime, а не только по коду.

# Цель

Не просто внести патч, а довести экран чатов до реально рабочего состояния в активном runtime: сообщения открываются в правильной позиции, прокручивается нужный контейнер, composer не теряется, специальные сообщения читаемы и отрисовываются осознанно.

# Пошаговый подход

1. Сначала найди активный runtime.
   - Определи конкретный проект/порт/процесс, а не «похожую папку».
   - Работай только в том frontend/backend, который реально обслуживает текущий UI.

2. Локализуй acceptance contour целиком.
   - frontend component/state;
   - CSS/layout/overflow/sticky;
   - backend serialization и meta-поля сообщений;
   - тесты/smoke, если они уже есть.

3. Для chat UI проверяй четыре вещи вместе.
   - initial open position: новый/открываемый чат должен попадать в конец обсуждения, если это ожидаемый UX;
   - scroll container: прокрутка должна жить в ленте сообщений, а не случайно на внешнем shell;
   - sticky behavior: header/nav/banner/composer должны иметь осознанную стратегию закрепления;
   - low-contrast states: attachments, meta, secondary text внутри user bubble нужно проверять отдельно.

4. Для новых special-message/artifact сценариев всегда проводи двустороннюю проводку.
   - Backend должен отдавать стабильные `message.meta` поля.
   - Frontend должен явно распознавать `message_kind` и рендерить нужный artifact.
   - Не полагайся на то, что raw text сам по себе достаточно объяснит состояние.

5. Для dashboard flows сначала делай универсальный контракт, потом частные builder-ы.
   - Сначала определи общий intent на «построить дашборд».
   - Затем резолви локальный источник данных через registry/builder pattern.
   - Если источник не распознан, возвращай structured clarification message, а не молча хардкодь частный сценарий.

6. После кодовых правок обязательно заверши цикл проверки.
   - build;
   - backend smoke / API-проверка критичных путей;
   - browser/live verification на реальном runtime.
   Без этого задача по chat UI не считается закрытой.

# Практические приёмы

## Scroll и открытие чата внизу

- Держи отдельный ref на scroll container и отдельный ref на terminal/end anchor.
- При смене active thread и изменении message list синхронизируй прокрутку вниз явно.
- Проверяй welcome/empty state отдельно: он часто ломает ожидаемую прокрутку.

## Sticky layout

- Сначала реши, какой контейнер должен скроллиться: обычно это только messages panel.
- Внешний shell должен иметь `min-height: 0` и предсказуемый `overflow`.
- Sticky header/banner/composer вводи только после того, как понятен настоящий scroll container.
- Если sticky не нужен, допустима альтернатива: вся навигация и composer съезжают вместе с основным scroll-контуром. Важно, чтобы поведение было консистентным.

## Structured messages

Полезные поля в `message.meta`:

- `message_kind`
- `dashboard`
- `clarification_title`
- `clarification_prompt`
- `clarification_options`
- `approval_title`
- `approval_prompt`
- `approval_scope`

Frontend должен трактовать их как отдельные состояния интерфейса, а не как случайные украшения текста.

## Export/file-response flows inside chat

Если пользователь просит «пришли в Word/PDF/файл» прямо внутри чата, проверяй не только генерацию attachment, но и логику выбора исходного assistant message.

- Не экспортируй просто «последний assistant message».
- В source selection явно исключай service/artifact сообщения: `processing_status`, `file_response`, error/fallback replies.
- Исключай пустые и служебные тексты вроде `Готовлю ответ…` и fallback-ответы наподобие `Не удалось получить ответ...`.
- Для regression-проверки смотри не только наличие файла, но и `exported_message_id` плюс `preview_excerpt`: они должны ссылаться на последний содержательный ответ, а не на предыдущий export/error.
- Если backend добавляет quality/validation для generated/exported artifacts, не оставляй их только внутри export helper-а: доводи поля до attachment metadata, top-level `file_response` meta и `thread_files`, иначе UI не сможет показать одинаковый статус в чате, drawer и preview modal.
- Для user-facing file cards держи короткий и прикладной словарь статусов (`ok` / `degraded` / `failed`) с человеческими подписями, а не сырые backend-структуры.
- Если generated `.pptx` — это быстрый внутренний draft для дальнейшей ручной сборки, допустимо встраивать compact quality banner прямо в титульный слайд, но только для проблемных случаев `degraded/failed`; `ok`-артефакты оставляй чистыми без служебной плашки.
- Если встраиваешь такой banner в сам artifact, делай это вторым проходом после первичной validation/quality оценки и затем повторно валидируй пересобранный файл, чтобы не заявлять статус для неподтверждённого patched `.pptx`.
- Для таких flows минимальный regression-набор должен проверять два слоя сразу: backend contract propagation (`attachments` / `thread_files` / `file_response.meta`) и frontend production build; для artifact-embedded warning отдельно проверяй, что проблемный `.pptx` получает титульную пометку, а `ok`-файл — нет.

## Timeout triage for background chat tasks

Если баг выглядит как «чат внезапно timed out», сначала проверь, нет ли скрытого более короткого retry-timeout в backend/runtime.

- Сверяй основной request timeout и retry timeout отдельно.
- Ищи значения по env + runtime wrapper/service unit, а не только в коде по месту вызова.
- Если симптом стабильно выглядит как «ровно 60 секунд», проверь default для retry/fallback attempts: часто именно он режет запрос раньше основного timeout.
- После фикса подтверждай результат не только тестом, но и живым probe: сам timeout, `model_attempts[*].timeout_seconds`, и статус backend после рестарта.

# Питfalls

- Не считай задачу завершённой после CSS/JS патча без живой проверки в runtime.
- Не оставляй Telegram- или другой доменный flow зашитым в CTA/label/intent detection, если пользователь просил универсальный инструмент.
- Не меняй большие файлы повторно после partial read-warning, не перечитав их целиком: targeted patch допустим, но для следующего слоя правок нужен full read.
- Не ограничивайся только frontend, если речь о новых message artifacts: без backend meta-полей UI останется декоративным.

# Критерии готовности

Считать задачу закрытой можно только если подтверждено следующее:

- чат открывается в ожидаемой позиции;
- скролл идёт по правильному контейнеру;
- header/nav/composer не теряются при длинной ленте;
- attachments и secondary text читаемы на пользовательских bubbles;
- clarification/approval/dashboard artifacts реально приходят и рендерятся;
- build и runtime smoke пройдены.

# Дополнительные материалы

- `references/chat-surface-acceptance-checklist.md` — короткий live-checklist для приёмки chat UI после правок.
- `references/export-flow-and-timeout-regression.md` — памятка по регрессиям export/file-response и скрытым 60-second timeout в background chat tasks.
- `references/pptx-quality-artifact-ui.md` — памятка по доведению backend quality/validation до chat file cards, `thread_files` и preview modal.

# Что приложить при повторяемых кейсах

Если во время задачи нашлась устойчивая схема meta-полей, карта файлов runtime или приёмка по конкретному экрану — добавь это в `references/` как короткую прикладную памятку, а не размазывай по SKILL.md.
