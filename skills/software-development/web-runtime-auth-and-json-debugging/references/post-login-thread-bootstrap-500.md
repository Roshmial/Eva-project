# Post-login thread bootstrap can masquerade as login failure

Use this note when a user shows a login-screen `internal_server_error`, but generic auth smoke passes.

## Symptom pattern
- User enters valid credentials.
- UI stays on or returns to the login surface with a generic `internal_server_error`.
- Broad smoke-user login may succeed, creating false confidence that auth is healthy.

## Durable lesson
A login-screen error is not always `/api/auth/login` failing. In chat-first apps it can be:
1. login succeeds;
2. frontend stores token;
3. frontend immediately calls bootstrap/profile/thread endpoints;
4. one of those authenticated reads crashes;
5. UI surfaces the failure as if login itself failed.

## Concrete failure class seen in Hermes Web
Historical `messages.meta_json` may be stored as a JSON string containing another JSON object, for example quoted JSON instead of a direct object.

Failure chain:
- `json_loads(meta_json, {})` returns `str`, not `dict`;
- downstream code assumes `meta.get(...)`;
- `list_thread_files(...)` or similar post-login thread hydration crashes with `AttributeError: 'str' object has no attribute 'get'`.

## Preferred verification path
- Check the exact user in the live DB first.
- Read backend logs around the login attempt timestamp.
- Identify the first authenticated route after login (`/api/bootstrap`, `/api/me`, `/api/threads/:id`, etc.).
- If password is unavailable, create a temporary server-side session for that user and load the UI with that token to reproduce the real post-login path.

## Preferred fix shape
- Make JSON parsing tolerant of nested JSON strings by unwrapping a second layer when the first parse returns a string starting with `{` or `[`. This is safer than patching only one caller because the same malformed historical payload can surface in multiple serialization paths.
- Add a regression test for nested JSON string payloads.

## Scope note
This reference is about the debugging pattern and compatibility fix, not about any one user's data.