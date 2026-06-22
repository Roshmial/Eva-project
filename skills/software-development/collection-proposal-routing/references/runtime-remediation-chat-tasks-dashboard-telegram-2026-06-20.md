# Runtime remediation notes — chat tasks, dashboard, Telegram export (2026-06-20)

Context: live prod verification on Hermes Web backend/runtime contour.

Key durable findings:

1. Immediate chat-task dispatch must claim the task before spawning the worker thread.
- Durable pattern: atomically update `chat_tasks.status` from `pending` to `running`, stamp `started_at`, clear `last_error`, then start the background thread.
- If the thread is spawned without a claim step, tasks can remain `pending` forever with `started_at = NULL` even though the request path looked successful.

2. For user-message POST flow, dispatch belongs immediately after enqueue.
- After creating the pending assistant placeholder and enqueuing the task, call the immediate dispatcher from the request path.
- Do not rely only on the periodic processor loop when the UX expectation is "reply starts now".

3. Dashboard execution needs a backend fallback payload.
- Durable pattern: after collection execution, if the LLM/dashboard normalizer returns weak or partial structure, build a minimal but valid dashboard payload in backend code.
- Minimum fallback shape: summary/text section, limitations section, and at least one lightweight visual section (`bar_list` / `pie_list`) so the route ends as `dashboard_result` instead of crashing or degrading into a generic reply.

4. Telegram collection for ad-hoc channel export should use task-local configs and conservative limits by default.
- The runtime task artifacts root for Telegram collection is the TG-API workspace (`/home/hermes/workspace/TG-API` in this contour), not the backend local data directory.
- For heavy date windows / new channels, a safer starting profile is lower `limit_per_channel` / `global_limit` rather than very large defaults.

5. Product decision still open for slow Telegram exports.
- If the export can exceed chat-task patience even after conservative limits, do not pretend it is a synchronous chat reply.
- Preferred fallback is an explicit async contract: accept the task, run export out-of-band, then deliver the file/status later.

Useful verification markers observed during remediation:
- Fixed immediate-dispatch behavior: new tasks gain `started_at` and leave `pending` without manual nudging.
- Fixed dashboard path: web-collection dashboard request ends with `message_kind=dashboard_result`.
- Unfixed Telegram heavy export path: assistant placeholder stays `pending`, then ends with `processing_status=error`, `last_error=timed out`.
