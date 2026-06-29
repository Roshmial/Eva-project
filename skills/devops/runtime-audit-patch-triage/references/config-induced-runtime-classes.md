# Configuration-induced runtime classes

Use this note when daily runtime audit shows repeated classes that come from missing preconditions or backend configuration, not from route-specific business logic.

## Recognition pattern

Typical signs:
- same low-severity `chat_task_error` repeats across 24h/72h;
- user intents vary, but the class is identical;
- the exception is raised before route-specific logic can materially diverge;
- examples may mention export/dashboard/collection, but the failure happens on the first generic downstream call.

## Example: `hermes_api_key_missing`

Observed pattern worth remembering:
- `call_hermes_messages(...)` raises `ApiError("hermes_api_key_missing", 500)` when `APP_MODE == "hermes-api"` and `HERMES_API_KEY` is empty.
- The proved code path is:
  - `post_message(...)`
  - `enqueue_chat_task(...)`
  - `process_chat_task(...)`
  - `call_hermes_api(...)`
  - `call_hermes_messages(...)`
  - `finalize_chat_task_error(...)`
- This proves the local raise site, but not yet the exact operational cause in live env (systemd unit, env file, deploy contour, manual shell launch, etc.). Treat the environment-level cause as a hypothesis until inspected directly.

## Preferred patch order

1. Improve user-facing error surface.
   - Add explicit normalization in `normalize_public_error_text(...)`.
   - Avoid forcing the user to infer that a generic failure was actually backend misconfiguration.

2. Reduce avoidable task churn.
   - Consider request-time preflight before enqueuing a chat task when the backend is known to be unable to call Hermes at all.
   - Useful when the frontend/API contract can absorb a synchronous failure cleanly.

3. Improve audit interpretation.
   - If needed, classify or annotate these classes as configuration/operational signals so they do not get over-read as product logic bugs.

## Reporting rule

When this pattern appears, always separate:
- fact: exact code path and raise point;
- hypothesis: why the runtime environment is missing the prerequisite;
- patch candidate: smallest local change that improves UX or reduces noise without pretending the environment is already fixed.
