# Victoria live case: DOCX ingestion and wrong-message export pattern

Use this reference when a Hermes Web user reports some combination of:
- uploaded `.docx` is "not visible" to the agent;
- assistant insists the file never arrived even though the UI shows it attached;
- generated `.docx` contains technical chatter, timestamps, or earlier export notices instead of the requested content.

## Confirmed live pattern

In the validated production case, two failure classes coexisted:

1. upload/ingestion inconsistency for `.docx`
2. export loop where `message_export` selected the wrong assistant message

## Ingestion pattern

Observed on `app.user_files`:
- some `.docx` rows had `text_extracted=0` and `extraction_note='Для этого формата пока сохраняю файл без извлечения текста.'`
- other `.docx` rows for the same user later had `text_extracted=1` and non-empty preview/extracted text

Strong signal from the live data:
- failed rows often had `stored_name` without a `.docx` suffix
- successful rows had `stored_name` preserving `.docx`

This does not prove the root cause by itself, but it is a strong diagnostic clue that extension-sensitive extraction or path handling may be involved.

## Wrong-message export pattern

In the validated case, repeated `file_response` deliveries exported earlier assistant messages that were themselves about export failures or prior generated files.

Symptoms:
- user asks for a Word file with the substantive content
- backend emits `source=message_export`
- `exported_message_id` points to an apology / prior export notice / technical explanation instead of the last substantive answer
- the next `.docx` therefore contains chat metadata, timestamps, or service chatter
- repeated retries can create a loop where each new export packages the previous export notice

## Practical checks

1. Inspect `app.messages` around the relevant thread.
2. For every suspicious `file_response`, record:
   - `message id`
   - `source`
   - `exported_message_id`
   - attachment path/name
3. Read the target exported file and compare it to the intended source assistant message.
4. Inspect `app.user_files` for the uploaded source documents, especially:
   - `stored_name`
   - `text_extracted`
   - `extraction_note`
   - `preview_text`
5. Do not accept assistant claims like "file not transferred" if a `user_files` row already exists.

## Interpretation rule

If the upload exists in `app.user_files` but the assistant says it cannot see the file, classify the issue as runtime/ingestion mismatch, not user error.

If the exported `.docx` is structurally valid but contains the wrong message, classify it as source-selection / export-contract bug, not binary file corruption.
