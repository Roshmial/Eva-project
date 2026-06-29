---
name: local-first-file-contour-delivery
description: Доведение local-first file contour в chat-first продукте через единый file semantics/provenance contract, backend/frontend round-trip и acceptance без расползания в разрозненные file-флаги.
---

# Когда использовать

Используй этот skill, когда в local-first chat/product UI нужно довести файловый контур до понятного продуктового слоя, а не просто «прикрутить upload/download».

Типовые триггеры:
- пользователь говорит, что Sprint / этап про `files`, `attachments`, `preview`, `reuse`, `export`, `generated result`;
- в backend уже есть частичные file-поля, но они разъехались по разным special-case веткам;
- во frontend файл можно открыть, но непонятно, что это: входной файл, повторное использование, экспорт старого ответа или новый deliverable;
- в message meta уже есть `attachments`, но нет явного provenance и непонятно, какие файлы реально использовались в конкретном ответе.

# Цель

Собрать file contour в один first-class слой:
1. единый contract для file semantics;
2. явное различение file roles;
3. provenance использованных файлов;
4. сквозной backend/frontend round-trip;
5. acceptance не только по коду, но и по targeted tests + production build.

# Основной принцип

Не добавляй ещё один набор разрозненных флагов под каждый сценарий. Сначала вводи единый семантический слой файла, а уже потом навешивай UI и маршруты.

Хороший путь:
- единый `file_surface` / аналогичный envelope;
- одинаковая нормализация для message attachments, profile files, generated results, exports;
- provenance `used_files` / `used_file_ids` на assistant message;
- frontend читает один contract и не угадывает тип файла по косвенным признакам.

Плохой путь:
- отдельные ветки `if generated`, `if export`, `if reused`, `if artifact` без общего контракта;
- UI определяет смысл файла только по `message_kind`;
- semantics живёт только в display-тексте, а не в machine-readable meta.

# Рекомендуемый контракт

Минимальный полезный `file_surface`:
- `file_kind` — роль файла в сценарии;
- `file_origin` — происхождение;
- `extraction_status` — распознан ли текст;
- `preview_status` — доступен ли preview/excerpt;
- `used_in_response` — использовался ли файл в данном ответе;
- `next_actions` — какие пользовательские действия допустимы.

Практичный набор `file_kind`:
- `input_file`
- `reused_file`
- `generated_result`
- `exported_answer`

Практичный набор `file_origin`:
- `user_upload`
- `profile_reuse`
- `generated_file_response` / `generated_result`
- `message_export` / `exported_answer`
- при необходимости `assistant_generated`

Для document-heavy сценариев не заставляй frontend заново выводить смысл из `text_extracted` и `extraction_note`. Сразу нормализуй в payload ещё три поля:
- `extraction_summary` — человекочитаемое объяснение, что удалось извлечь;
- `preview_summary` — короткий summary того, что система увидела внутри файла;
- `preview_lines` — компактный набор строк для встроенного preview modal.

Практичный смысл `extraction_status`:
- `recognized` — текст извлечён нормально;
- `partial` — текст извлечён частично, есть ограничения или warning;
- `not_recognized` — текст не извлечён.

# Порядок работы

## 1. Сначала собери факты о текущем контуре

Проверь три слоя:
- backend serialization message/meta;
- file storage / user_files / attachments;
- frontend rendering file cards / preview / profile files.

Нужно ответить на вопросы:
- где уже есть truth-source по файлам;
- какие поля уже существуют;
- где semantics дублируется или расходится;
- какие сценарии реально есть в продукте: upload, reuse, export previous answer, generate-and-attach, artifact delivery.

## 2. Введи единый normalizer

Сделай helper-слой, который:
- принимает сырой file payload;
- достраивает `file_surface`;
- выставляет `file_kind` и `file_origin` даже для старых payload-ов;
- работает одинаково для attachments и `user_files`.

Это должен быть один путь нормализации, а не разная логика в трёх местах.

## 3. Разведи generated vs export явно

Не оставляй оба сценария под одним только `message_kind=file_response`.

Обязательно различай:
- экспорт предыдущего ответа (`exported_answer` / `message_export`);
- новый файл, созданный по текущему запросу (`generated_result` / `generated_file_response`).

Иначе во frontend и в acceptance потом всё смешается в один «просто файл».

## 4. Добавь provenance использованных файлов

Если ответ опирается на файлы пользователя или profile reuse, сохраняй это на assistant message meta:
- `used_files`
- `used_file_ids`

Это важнее, чем просто список входных attachments пользователя, потому что показывает, чем ответ реально пользовался.

Если технически точный file-level provenance пока дорог, стартовый допустимый вариант:
- использовать attachments текущего user message как conservative provenance;
- но сохранить это именно как `used_files`, чтобы потом улучшить точность, не ломая contract.

## 5. Переведи frontend на contract-driven rendering

UI должен показывать не только имя и размер файла, но и:
- тип файла по продуктовой роли;
- происхождение;
- использовался ли он в ответе;
- распознан ли текст.

Минимальные точки:
- file result card в чате;
- профиль / список пользовательских файлов;
- отдельный блок уровня `Использовано в ответе`, если у assistant message есть `used_files`.
- preview modal, который не ограничивается кнопкой `Открыть отдельно`, а показывает extraction status, preview status и встроенный текстовый preview для `txt/csv/docx/xlsx/pdf-text`, если backend уже отдал `preview_summary`/`preview_lines`.

Для user-facing file results не делай длинный preview default-visible внутри chat bubble или recurring summary card. По умолчанию пользователь должен видеть компактный результат:
- короткий статус (`Файл готов`, `Документ собран` и т.п.);
- имя файла;
- базовые действия (`Открыть`, `Скачать`, при необходимости `Preview`).

Длинный текстовый хвост, содержимое документа, delivery/debug-метаданные и прочие вторичные детали показывай только по отдельному действию: `Preview`, `Показать текстовый preview`, `Детали`.

## 6. Закрой acceptance

Минимальный обязательный набор:
- targeted backend tests на serialization contract;
- targeted backend tests на `used_files` provenance;
- targeted regression tests на соседние export/generated scenarios;
- syntax/compile check backend;
- production build frontend.

Не закрывай работу только на локальном ручном просмотре JSON.

# Частые pitfalls

## Pitfall: чинить UI без общего контракта

Симптом:
- во frontend появляются специальные подписи под каждый file case;
- backend продолжает отдавать разнородные payload-ы.

Правильнее:
- сначала стабилизировать contract в backend;
- потом переводить frontend на чтение этого contract.

## Pitfall: не различать export и generated

Симптом:
- оба сценария визуально и семантически сливаются в один file response;
- пользователь не понимает, это новый deliverable или упаковка предыдущего ответа.

Правильнее:
- разные `file_kind` / `file_origin` при одном message family.

## Pitfall: хранить только входные attachments, но не provenance ответа

Симптом:
- видно, что пользователь приложил файлы, но не видно, использовались ли они в конкретном ответе.

Правильнее:
- отдельные `used_files` / `used_file_ids` на assistant message.

## Pitfall: делать preview default-visible в user-facing file result

Симптом:
- assistant bubble и recurring summary card сразу показывают длинный текст документа или preview содержимого;
- пользователь видит одновременно статус, файл, delivery-метаданные и большой текстовый хвост;
- результат выглядит тревожно и перегруженно даже когда файл собран корректно.

Правильнее:
- по умолчанию показывать только компактную file card;
- сырой preview, текст документа, delivery/debug details и прочие вторичные блоки открывать только отдельным действием;
- если backend уже умеет отдавать короткий status/summary, не дублировать длинное содержимое в bubble только потому, что оно есть в payload.

## Pitfall: recurring/job delivery с файлом рендерится как несколько несвязанных блоков

Симптом:
- TG daily digest или другой recurring/job delivery приходит как `summary + attachment`;
- UI показывает сразу несколько слоёв: служебную summary-grid, потом отдельный plain attachment list, иногда ещё и пустую заглушку `…` вместо текста;
- пользователь видит backend contract, а не единый результат.

Правильнее:
- для recurring/job delivery с attachment делать один компактный result card;
- внутри держать только короткий итог, status, при необходимости delivery note и один file list с primary action;
- не дублировать тот же файл вторым `attachment-list` ниже;
- если для такого path `messageDisplayText()` сознательно возвращает пустую строку, bubble не должен рендерить placeholder.

Но различай два продуктовых режима:
- `file-first delivery` — основной результат это сам файл; тогда compact card действительно должна быть главным visible блоком;
- `text-first digest/report delivery` — основной результат это читаемый текст сообщения, а файл лишь вторичный экспорт/служебное приложение.

Для TG digest, client digest, summary brief и похожих сценариев не прячь полезный readable текст внутрь file-only карточки. Правильный user-facing слой здесь:
- сначала сам digest/summary как основной контент сообщения;
- затем короткая пометка про файл, если он приложен;
- затем компактная file card как secondary artifact.

Если readable текст уже самодостаточен для потребления, файл не должен перетягивать на себя главный визуальный фокус и не должен превращать экран в `Файл -> Открыть`, оставляя сам digest вторичным хвостом.

## Pitfall: гонка в HTTP-smoke тестах из-за auto-dispatch

Симптом:
- тест создаёт message через `POST /api/threads/<id>/messages`;
- endpoint сразу запускает `dispatch_chat_task_now(task_id)`;
- тест потом вручную вызывает `process_chat_task(task_id)` и получает недетерминированное падение.

Правильнее:
- если тесту нужен ручной вызов `process_chat_task(...)`, патчь `dispatch_chat_task_now` на HTTP-шаге (`patch.object(..., 'dispatch_chat_task_now', return_value=True)`), чтобы убрать гонку;
- direct-path тесты, которые создают `chat_tasks` через SQL без HTTP endpoint, этой гонки не имеют.

## Pitfall: улучшать PPTX export как простой line-chunking из chat-outline

Симптом:
- `.pptx` формально открывается, но внутри остаются заголовки вида `Слайд N – ...`, сервисная прелюдия про невозможность создать бинарный файл, CTA-хвосты вроде `Вы можете создать новую презентацию...`, а сами слайды выглядят как нарезка чатового ответа по 4 пункта.
- пользователь видит не презентацию, а аккуратно упакованный transcript.

Правильнее:
- для generated `pptx` вводить отдельный presentation-planning слой, а не пытаться лечить только layout;
- сначала нормализовать body: отрезать limitation/apology-прелюдию и сервисные хвосты `При необходимости я могу помочь...`, `Дайте знать...`;
- затем нормализовать slide headings: убирать `Слайд N –` / `Slide N -`, оставляя предметный заголовок;
- title slide собирать из label-ов вроде `Заголовок` / `Подзаголовок`, если они есть, а не из буквального первого heading-а;
- для длинных deck-ов добавлять хотя бы один overview slide со структурой разделов;
- label-only sections рендерить как cards/grid, а narrative sections упаковывать более крупными смысловыми чанками, а не микрослайдами по 3–4 строки.

Практический критерий качества:
- generated deck должен быть "presentation artifact", а не "chat-outline в формате `.pptx`".

## Pitfall: валидировать новый PPTX builder через roundtrip из старого сломанного `.pptx`

Симптом:
- в качестве acceptance берут уже экспортированный старый `.pptx`, вытаскивают из него text runs и прогоняют их обратно через новый builder;
- затем по результату делают вывод о качестве нового export-контура.

Почему это ловушка:
- старый `.pptx` уже потерял исходную markdown/section-структуру;
- внутри него могут остаться legacy-артефакты (`slide` badges, служебная прелюдия, layout-specific повторы), которые новый builder честно воспринимает как входные данные;
- такой roundtrip полезен как negative example и smoke-проверка читаемости, но не как источник истины о качестве нового planning-а.

Правильнее:
- новым источником истины считать исходный generated text / fixtures / regression tests для export-builder-а;
- старый пользовательский `.pptx` использовать как ориентир симптомов, которые нужно перестать воспроизводить;
- если нужен reference, фиксировать это в `references/`, а не подменять roundtrip-артефактом настоящую acceptance-проверку.

## Pitfall: `thread_files` пусты, хотя файл реально сохранился в `user_files`

Симптом:
- `GET /api/threads/<id>` возвращает `thread_files: []`;
- при этом `/api/files` и сама БД уже показывают корректный `user_file` с тем же `thread_id` и `message_id`;
- возникает ложное ощущение, что файл потерялся на upload/storage слое.

Правильнее:
- сначала сравнить три источника отдельно: `app.user_files`, `/api/files`, `/api/threads/<id>`;
- если файл есть в БД и в `/api/files`, но нет в `thread_files`, искать баг именно в thread-level serialization path (`list_thread_files`, `serialize_user_file`, message attachment normalization), а не во frontend;
- отдельно проверять, не зависит ли serialization от request-context (`request.headers`, cookie/query token injection) без guard через `has_request_context()`.

Практический урок:
- если `serialize_user_file(...)` или соседний normalizer тянет auth token из `request`, это нужно делать безопасно: `try_get_auth_token() if has_request_context() else None`.
- Иначе один и тот же файл может быть корректно сохранён и виден в profile/files, но silently выпадать из thread-level surface.

## Pitfall: acceptance смешивает разные auth/runtime contours

Симптом:
- один frontend URL успешно открывается, но demo-login там не проходит;
- другой URL принимает тот же token и работает с локальным API;
- в результате UI-регрессию путают с тем, что acceptance запущен против другого auth-store или другого backend contour.

Правильнее:
- до UI acceptance явно установить связку `frontend URL -> API base -> auth store`;
- проверять `service-info`, `auth/session` и token-based запросы на каждом candidate contour отдельно;
- не делать вывод `UI сломан`, пока не подтверждено, что именно этот frontend смотрит в тот backend и тот auth-store, который ты сейчас чинишь.

Для local split-runtime это особенно важно:
- один contour может быть `frontend 8793 -> local API 8791`;
- другой визуально похожий contour может жить на отдельном auth/runtime state и отвергать ту же demo-учётку.

## Pitfall: закончить на backend tests и забыть production build

Даже при зелёных unittest можно легко сломать JSX/CSS слой. Для такого класса задач production build обязателен.

# Минимальный definition of done

Считать slice завершённым, когда выполнено всё ниже:
- один унифицированный file contract реально используется в backend serialization;
- `input / reuse / generated / export` различаются machine-readable способом;
- assistant message хранит `used_files` provenance;
- frontend это показывает в chat и profile surfaces;
- targeted backend tests зелёные;
- frontend production build зелёный.

# Что приложить в references

Для конкретного проекта полезно держать в `references/`:
- пример полей `file_surface`;
- accepted naming conventions для `file_kind`/`file_origin`;
- краткий список regression tests;
- session-specific примечания по UI/contract mapping;
- заметки по extraction transparency и preview modal для document-heavy форматов.

См. `references/file-surface-contract-and-provenance.md`, `references/extraction-preview-transparency.md`, `references/thread-files-runtime-and-auth-contours.md` и `references/pptx-export-planning-vs-chat-outline.md`.
