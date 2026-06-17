# Backend live verification: endpoints green, chat path red

Use this when a web/backend service appears healthy (`/health`, `/bootstrap`, `/jobs`, admin routes all return 200) but user-facing chat or task execution still fails.

## Why this matters

A backend can be structurally healthy while its downstream inference/runtime path is broken. Simple route checks are not enough for chat-first products.

## Verification pattern

1. Verify service process health.
   - systemd/service status
   - recent journal with fresh timestamps

2. Verify structural API health.
   - public health/info/setup endpoints
   - authenticated bootstrap and list endpoints
   - jobs/admin endpoints if the product exposes them

3. Verify the real user action, not only list/read endpoints.
   - create/login a real session
   - create a thread/conversation
   - post a message/task
   - poll thread/task state until completion or error

4. Inspect queue/task state separately from model execution.
   - confirm task is enqueued
   - confirm background processor picks it up
   - inspect task status distribution in DB if needed
   - distinguish `pending/running/completed/error`

5. If the task reaches `error`, inspect downstream runtime/provider logs.
   - Hermes API server / gateway log
   - provider/auth/model configuration
   - API server auth and base URL

## Key diagnostic lesson

If message POST succeeds and queue recovery works, but the assistant message flips from pending to error with a runtime/provider exception, the bug is not in the queue itself. Report it as a downstream inference configuration problem, not as a backend route failure.

## Good final framing

Split conclusions into:
- backend/web API health
- queue/worker health
- downstream inference/runtime health

This avoids saying "the whole backend is broken" when only the model execution layer is misconfigured.
