# File-analysis regressions: export misfire vs incomplete LLM context

Use this note when a user reports one or both symptoms:
- "I asked to analyze a file, but the system returned a file instead of an answer in chat"
- "The document was uploaded, but it looks like not everything was read"

## 1. Separate two different failure classes

Do not collapse these into a generic "OCR/doc parsing is broken" claim.

Check separately:
1. request routing / intent classification
2. document extraction completeness
3. what portion of extracted text actually reaches the LLM context

A document may be extracted successfully while the user still gets a bad answer because only a truncated preview reached the model.

## 2. Export misfire pattern

A durable failure mode in chat-first file workflows:
- backend treats simple mentions of `.docx` / `docx` / `document` as an export request
- the user asked for analysis of an uploaded file
- the system responds with `file_response` / generated attachment instead of a normal chat answer

Durable repair pattern:
- split `format mention` from `export intent`
- allow explicit format selection (`docx`, `pdf`, `md`, etc.) to resolve only when a real export-intent phrase is present
- keep filename mentions like `ТЗ2.docx` and analysis phrases like `разбери документ и дай выводы в чат` inside the normal chat-analysis path
- a good implementation shape is a dedicated helper like `is_message_export_request(...)`, then `detect_message_export_format(...)` calls it instead of treating format keywords as sufficient on their own

### What to verify
- inspect export-intent detection logic
- check whether explicit format detection (`docx`, `pdf`, etc.) is allowed to fire without explicit export intent (`send`, `export`, `generate file`, `in docx`)
- add a regression for phrases like:
  - `Проанализируй файл ТЗ2.docx`
  - `Разбери приложенный документ docx и дай выводы в чат`
- these must stay in normal analysis flow
- keep positive tests for real export requests:
  - `Отправь мне файл в docx`
  - `Выгрузи ответ в pdf`

## 3. Extraction completeness vs model context completeness

For long DOCX/PDF-like inputs, verify two lengths separately:
- full extracted text length
- preview text length sent to UI

If `text_extracted=true` but only `preview_text` reaches the message context, the user-visible symptom will be "file was not fully read" even though parser extraction succeeded.

### Acceptance rule
- `preview_text` may stay short for UI convenience
- LLM context must receive full `extracted_text` up to the backend attachment limit, not only preview
- persist `extracted_text` in the stored file record (`user_files`-like table), not only in the transient upload object
- repeated / reused file flows must preserve the same full extracted payload; otherwise first-use analysis may work better than later reuse of the same uploaded file

## 4. DOCX-specific acceptance

For complaints like `не всё распозналось`, do not accept `document.paragraphs` as sufficient proof.

Check at least:
- body paragraphs
- tables
- headers
- footers
- for long files: tail sections that would be lost if only the first preview chunk were used

## 5. Minimal regression pack

Add or keep tests for:
- `detect_message_export_format(...)` does not trigger on filename-only `.docx` mentions
- explicit export requests still resolve to export format
- `build_attachment_context(...)` prefers full `extracted_text` over short preview
- stored/reused file rows preserve `extracted_text`

## 6. Reporting discipline

When closing the incident, state clearly which layer was broken:
- wrong export routing
- parser/extraction incompleteness
- context truncation after successful extraction

Do not report all three as the same defect unless they are all proven.
