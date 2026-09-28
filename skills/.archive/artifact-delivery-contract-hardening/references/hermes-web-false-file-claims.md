# Hermes Web false file claims — live case notes

## Why this reference matters
This is a concrete example of a class-level failure: the assistant claimed that a file/document was ready, but the runtime produced no attachment. The lesson is not the specific chat topic; the lesson is how to detect and harden artifact-delivery contracts.

## Live evidence pattern
User/thread:
- user: Виктория
- thread title: `Flatpak`
- thread id: `21`

Broken messages observed in storage:
- assistant message `115`: text like "Я приступаю к финальной сборке..."
- assistant message `117`: text like "Я подготовила финальный документ..."

But metadata showed:
- `attachment_count = 0`
- `message_kind` absent/empty

Conclusion:
- these were false artifact claims,
- not real file responses.

## Important diagnostic clue
The same thread already contained earlier successful export messages:
- message ids `90`, `93`, `95`, `97`
- `message_kind = file_response`
- `attachment_count = 1`

This proved:
- the export mechanism itself was not fundamentally broken,
- the main defect was that generic file intent sometimes bypassed deterministic export routing and fell back to unconstrained model text.

## Durable fix pattern
1. Tighten system/backend instructions:
   - forbid claims that a file/link/document is ready unless the same response contains a real attachment, file path, or download URL.
2. Expand generic file-intent routing:
   - phrases like `давай файл`, `пришли документ`, `отправь файл`, `направь файл` should map to deterministic `docx` export of the latest eligible assistant answer.
3. Add regression tests:
   - explicit export request,
   - generic file request.
4. Run live acceptance:
   - create temp user/thread,
   - produce normal assistant answer,
   - send `Давай файл`,
   - verify `message_kind=file_response`, `export_format=docx`, non-empty attachment list, real `download_url`.

## Verified acceptance shape from this case
After hardening, live acceptance on the real runtime produced:
- `message_kind = file_response`
- `export_format = docx`
- `attachment_count = 1`
- real `download_url`
- real `original_name = ...docx`

## Optional next hardening step
If the surface is high-stakes, add a backend guard that scans assistant output for claims like:
- "файл готов"
- "документ подготовлен"
- "ссылка приложена"

and blocks or rewrites the response when attachment metadata is empty.
