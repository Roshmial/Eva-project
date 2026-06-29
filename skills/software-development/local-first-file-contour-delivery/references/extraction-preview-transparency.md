# Extraction / Preview Transparency Notes

Когда file contour уже переведён на единый `file_surface`, следующий полезный шаг для document-heavy сценариев — не заставлять frontend восстанавливать смысл из сырых полей `text_extracted`, `extraction_note`, `preview_text`.

## Рекомендуемые дополнительные поля payload

- `extraction_summary` — человекочитаемое объяснение, что удалось извлечь.
- `preview_summary` — короткий summary того, что система увидела внутри файла.
- `preview_lines` — небольшой массив строк для встроенного preview modal.

## Практичная логика статусов

### `extraction_status`
- `recognized` — текст извлечён нормально.
- `partial` — текст извлечён, но есть ограничение/warning; хороший эвристический сигнал — `text_extracted=true` и при этом есть `extraction_note`.
- `not_recognized` — текст не извлечён.

### `preview_status`
- `available` — есть `preview_text`, `preview_excerpt` или `extracted_text`.
- `unavailable` — показать честное сообщение, а не пустую заглушку.

## Что показывать в preview modal

Минимальный полезный состав:
- file semantics (`file_kind`, `file_origin`);
- extraction status;
- preview status;
- extraction summary / note;
- встроенный текстовый preview для `txt`, `csv`, `docx`, `xlsx`, `pdf-text`;
- fallback-ссылка `Открыть отдельно`.

## Для каких форматов это особенно полезно

- `txt`
- `csv`
- `docx`
- `xlsx`
- `pdf-text`

## Regression-идея

Держать targeted backend test, который проверяет, что `normalize_attachment_payload(...)` реально отдаёт:
- `file_surface.extraction_status`
- `extraction_summary`
- `preview_summary`
- `preview_lines`

## Test pitfall рядом с file flows

Если HTTP-тест создаёт message через `POST /api/threads/<id>/messages`, а потом вручную вызывает `process_chat_task(task_id)`, надо на HTTP-шаге патчить `dispatch_chat_task_now`, иначе появляется гонка между auto-dispatch и ручным вызовом processor.
