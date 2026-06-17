# Runtime contour and session hygiene reference

## What this reference captures

A concrete local-first cleanup pass where backend, frontend, CopilotKit runtime, admin metrics, file links, and session hygiene all interacted.

## Canonical contour pattern

Use one explicit contour of truth:
- frontend on one port
- backend on one port
- runtime/proxy sidecar on one port
- all three tied to one repo copy

Operational lesson:
If an older repo copy is still listening, acceptance and debugging become misleading even when code patches are correct.

## Specific failure patterns worth remembering

### 1. Frontend proxy silently pointing to a retired backend

Symptom:
- frontend is healthy
- `/api/*` intermittently fails or returns stale behavior
- Vite proxy still targets an old backend port

Fix pattern:
- inspect dev-proxy default target
- update it to the canonical backend port
- stop the legacy backend contour so the mistake cannot hide

### 2. Admin activity query derived from the wrong table shape

Symptom:
- admin health endpoint returns `500`
- SQL assumes `messages.user_id`

Root cause:
- `messages` contains `thread_id`, not `user_id`

Correct pattern:
- derive user activity via `messages m JOIN threads t ON t.id = m.thread_id`
- then aggregate on `t.user_id`

### 3. Message attachment open-link route missing a storage fallback

Symptom:
- user file downloads work
- message attachment open-link returns `404`

Root cause:
- route only resolves `local_path`
- stored attachment payload uses `relative_path`

Correct pattern:
- support `local_path`
- if absent, reconstruct allowed path from `relative_path` under the data root
- keep path normalization/ownership checks

### 4. Session explosion from repeated test logins

Observed shape:
- session TTL exists
- expired active sessions count is zero
- active sessions still explode because every login issues a new token and leaves prior ones active

Correct pattern:
- on successful login, revoke prior active sessions for that user before issuing a new token
- keep maintenance cleanup for expired and old revoked tokens
- verify by logging in multiple times and checking active sessions stay at 1 for that user

## Recommended live checks

1. Listener check
- confirm which ports are listening
- confirm PID/command/cwd match the intended repo

2. Backend checks
- health
- service-info
- CopilotKit info
- admin health
- admin users

3. Contract checks
- file list contains `download_url`
- authenticated file download works
- authenticated message attachment open-link works

4. Session checks
- total sessions
- active sessions
- active sessions by user
- old active sessions beyond TTL
- effect of repeated login on active session count

## Architectural rule reinforced by the session

For this class of app, admin and summary views should be centered on:
- `user_id`
- `threads`
- `messages`
- ownership and runtime truth

They should not drift into session-count-centric summaries unless the endpoint is explicitly about auth maintenance.
