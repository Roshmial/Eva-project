# Hermes Web MVP: tail-fixes and runtime patterns

Use this reference when finishing local-first Hermes Web MVP tasks that touch live UI/runtime.

## 1. Assistant-generated files in chat

When the agent needs to send a file into a chat from the assistant side, prefer the existing local `MEDIA:/absolute/path` pattern instead of inventing a new upload/storage pipeline.

Recommended implementation shape:
- Parse `MEDIA:/...` lines from assistant text on the backend.
- Remove `MEDIA:` lines from visible chat text before rendering to the user.
- Convert valid paths into `message.meta.attachments` entries.
- Add authenticated download URLs per attachment, for example `/api/messages/<message_id>/attachments/<attachment_index>`.
- Reuse the same enrichment path both for normal thread replies and job-delivery messages so behavior stays consistent across chat and job threads.
- If assistant metadata is enriched twice (for example once before insert and once after message_id is known), preserve existing attachments and only append `download_url`; otherwise the second pass can silently drop the already parsed file metadata.

Safety/validation:
- Only allow absolute local paths from explicitly allowed roots, such as `/home/hermes` and `/tmp`.
- Reject missing files and non-files.
- Keep attachment metadata minimal: name, mime type, size, local path, assistant_generated flag, user-facing note.

Frontend expectations:
- Assistant messages must not show raw `MEDIA:/...` lines.
- Assistant-generated attachments should render with a distinct friendly status like `Подготовлен ответом`.
- Provide an explicit download link in the attachment card, not only the file badge/status.
- Existing user-file attachment behavior must remain unchanged.

Verification note:
- Smoke tests should cover both metadata creation and real download by URL.
- In live browser checks, do not rely only on an optimistic typing placeholder; reload the thread or inspect persisted message state after the response lands.
- If backend code changed, restart the actual process bound to the service port before concluding that a new route or attachment behavior is missing.

## 2. Professional Russian UI copy pass

For Hermes Web UI cleanup, do not stop at functionality. Run a phrase audit over visible labels, statuses, placeholders, banners, and helper text.

Look for:
- colloquial or clumsy wording (`галочками`, overly casual phrasing)
- technical leaks visible to end users
- vague empty states (`пока не задан`) that can be made more professional
- inconsistent object naming across screens

Preferred tone:
- деловой русский
- спокойно и нейтрально
- without slang or playful wording
- short but specific enough to explain the action/state

## 3. Finish means runtime, not only code

For MVP tail-fixing tasks, do not treat code edits as done. Minimum acceptance should include:
- syntax/compile check
- live runtime check in browser or API
- verification that restart/redeploy did not accidentally target a stale process
- cleanup of test artifacts if they were created during verification

## 4. Data cleanup expectation

When the user asks to clean the working DB, interpret it as operational cleanup, not only UI cleanup.
- Remove test users and transient records after verification.
- Preserve the admin account if the user explicitly says `кроме админа`.
- Prefer controlled cleanup after runtime verification so evidence is still available during debugging.
