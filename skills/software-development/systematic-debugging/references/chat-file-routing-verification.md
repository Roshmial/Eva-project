# Chat file-routing live verification

Use when a chat/backend claims to "send a file" but the failure mode may actually be wrong routing or wrong export source.

## What to verify

1. Distinguish two modes explicitly:
   - export existing answer -> backend should package a prior assistant message
   - generate new content + attach -> backend should first generate a fresh answer, then package that new answer

2. For export-existing mode, inspect backend metadata:
   - `message_kind=file_response`
   - `source=message_export`
   - `exported_message_id=<prior assistant message id>`

3. For generate-and-attach mode, inspect backend metadata:
   - `message_kind=file_response`
   - `source=generated_file_response`
   - `generated_from_request=true`
   - no `exported_message_id`

4. Compare `preview_excerpt` or equivalent preview field to the expected content source.
   - If it repeats an older assistant answer, the backend is probably exporting stale content.
   - If it begins with the newly requested content, routing is likely correct.

5. Fetch the attachment over HTTP and verify:
   - `Content-Type`
   - download headers
   - magic bytes / file signature when relevant (`PK\x03\x04` for `.docx`)

## Common pitfall

A backend may stop producing apology text and still be wrong: it can reliably return a real file while exporting the wrong previous message. This is not a file-generation bug; it is a request-mode classification bug.

## Good acceptance probe

Run both cases:
- short generic request like "Отправь мне файл" after a known prior assistant answer -> should export previous answer
- substantive request like "Пришли полноценный концепт ... в виде файла" with a stale older answer already present -> should generate a new answer and attach that, not export the stale one
