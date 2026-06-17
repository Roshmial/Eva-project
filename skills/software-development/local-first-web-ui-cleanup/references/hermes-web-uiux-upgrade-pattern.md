# Hermes Web MVP: UI/UX upgrade pattern for local-first admin/chat apps

Use this pattern when the app is already technically working and the next pass is about reducing friction without adding infrastructure.

## High-value upgrade batch

1. File workflow
- Add reuse from `Мои файлы` without re-upload.
- Distinguish `pending new files` vs `existing profile files selected for reuse` in client state.
- Show explicit composer status: idle, prepared-to-send, sending.
- Add profile-level filters: search, scope (`all` / `current_thread`), type/status (`all` / `text_ready` / `stored_only`).
- In message cards show extraction status (`Текст извлечён`, note/warning, or `Сохранён`).

2. Message rendering
- Keep `user_text` separate from the attachment context assembled for the backend.
- When rendering a user message with attachments, display the original user text if available and avoid duplicating the generated attachment preamble in the visible chat bubble.
- For reused files, mark them explicitly in the attachment card (`Файл использован повторно из личного списка`).

3. Profile screen
- Add a short profile summary card instead of only a long form.
- Treat `Мои файлы` as a working area, not a passive archive: preview, filter, reuse.

4. Admin screen
- Split heavy admin pages into explicit sections/tabs instead of one long vertical sheet.
- Collapse history/details behind `details` or equivalent progressive disclosure.
- Prefer `overview / users / operations / references` style grouping for local-first admin surfaces.

## Backend contract pattern

When adding file reuse, extend the existing message endpoint instead of creating a parallel pipeline:
- keep upload via `multipart/form-data`;
- accept `existing_file_ids` in the same send-message flow;
- enforce the same total attachment limit across new and reused files;
- include attachment metadata plus `reused: true` for reused items;
- store `user_text` separately in message meta so the frontend can render the original text cleanly.

## Verification ladder

If a full browser visual pass is blocked or flaky, do not stop at that point. Finish a technical acceptance ladder:
- `node --check` for frontend JS;
- `py_compile` (or project-equivalent syntax check) for Python entrypoints;
- backend smoke test covering upload flow;
- extend smoke tests when the backend contract changes (for example, add a reused-file assertion after implementing `existing_file_ids`);
- verify HTTP readiness of backend and frontend entrypoints.

Visual browser acceptance is still desirable, but its absence should be reported honestly as an unconfirmed layer, not as a blocker to all technical verification.

## Pitfalls

- Do not treat files only as one-message attachments if the product already needs a persistent `Мои файлы` area.
- Do not create a second upload pipeline for reused files; extend the existing send-message contract.
- Do not leave attachment statuses implicit; users need to see whether text was extracted or the file was only stored.
- Do not claim full UI acceptance if only technical/runtime verification was completed.
