# Hermes Web collection -> artifact delivery pattern

## When this reference matters
Use this when a Hermes Web chat request is not just "export the last answer", but a live collection task like:
- "собери данные с URL и дай в csv"
- "собери из интернет-источников и отдай в json/xlsx"
- similar source-driven requests where the system must execute collection first, then deliver an artifact.

## Durable pattern
Do not stop at `collection_contract` when the request is already fully specified and the source type is executable in the current stack.

Preferred flow:
1. detect collection request,
2. build contract,
3. if contract incomplete -> `clarification_request`,
4. if contract complete and source type supported -> execute,
5. build real artifact under the backend data directory,
6. attach artifact to the assistant message via standard `attachments` metadata,
7. expose download through the normal message attachment route.

## Concrete backend choices that worked
- Reused the existing message attachment flow instead of inventing a separate artifact API.
- Ensured message serialization injects `download_url` for attachments if the backend only stored `local_path` / `relative_path`.
- For explicit URL sources, treated `subject`, `output_format`, and `fields` as contract requirements; missing `subject` correctly triggers clarification.
- For complete explicit URL prompts, execution produced `collection_execution_result` plus a real attachment.

## Runtime verification pattern
Minimum live acceptance on prod:
1. Send an incomplete web-collection prompt with explicit URLs.
   - Expected: honest `clarification_request`.
2. Send a complete web-collection prompt with explicit URLs, subject, output format, and fields.
   - Expected: `collection_execution_result`.
3. Inspect assistant message metadata.
   - Must contain non-empty `attachments`.
4. Download the attachment via `/api/messages/<id>/attachments/<index>`.
   - Must return the actual file bytes.
5. Inspect file content.
   - Must be a real structured artifact, not a transcript or placeholder text.

## Example proven on prod
Prompt class:
- "Собери данные с https://example.com и https://example.org в csv по теме example domains. Нужны поля title, summary"

Expected result shape:
- assistant text says the file is prepared,
- `message_kind=collection_execution_result`,
- attachment exists,
- attachment download returns CSV,
- CSV contains rows for both URLs.

## Key pitfalls
- File exists on disk but is not surfaced in message `attachments`.
- Attachment metadata exists but has no usable `download_url`.
- Complete request still returns `collection_contract` instead of execution result.
- Verification checks only UI text and not the actual attachment GET.
