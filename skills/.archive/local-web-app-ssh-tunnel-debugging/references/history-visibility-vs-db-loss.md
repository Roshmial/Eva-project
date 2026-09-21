# History visibility vs real DB loss

Use this note when a user says the web chat history "reset" or "disappeared" in a local/self-hosted multi-user MVP.

## Core distinction

Do not equate an empty or shortened thread list in the UI with actual data loss.

In app-layer chat products there are at least three different states:
1. data is missing from the DB;
2. data exists in the DB but is hidden by filters or user scope;
3. data exists, but the current session is authenticated as a different user.

## Fast verification path

1. Check the app DB directly.
- Inspect counts for `threads` and `messages`.
- Read the latest few rows with `id`, `user_id`, `archived`, `updated_at`, short message content.
- This tells you whether the storage actually lost records.

2. Check the user-facing API under the real account.
- Login as the affected user.
- Compare `GET /api/threads?include_archived=0` vs `include_archived=1`.
- Load a specific thread with `GET /api/threads/<id>`.

3. If available, compare with admin endpoints.
- `GET /api/admin/threads`
- `GET /api/admin/events`
- If admin sees more threads than the user, investigate ownership and visibility before concluding the DB was wiped.

## Common causes of fake "reset"

- archived threads are hidden by default;
- the user is logged in under another account;
- the thread belongs to another `user_id` in the app DB;
- UI scope/filter changed after restart or relogin;
- demo/admin seed data exists, but the current user sees only their own threads.

## Good explanation pattern for the user

Say explicitly which layer changed:
- "История в базе есть";
- "во вьюхе сейчас показывается только активное";
- "архив скрыт";
- "часть чатов принадлежит другому пользователю".

This keeps the diagnostic honest and avoids panic edits to storage when the problem is really view filtering or auth context.
