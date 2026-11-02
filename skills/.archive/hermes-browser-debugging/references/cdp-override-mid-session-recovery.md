# CDP override mid-session recovery

Use when Hermes browser tools show a split outcome:
- `browser_navigate(...)` succeeds and reports the expected URL/title;
- the next `browser_snapshot(...)` or `browser_console(...)` fails with transport errors like:
  - `CDP WebSocket connect failed`
  - `Connection refused`
  - `connect call failed`

## Why this matters
A simple preflight health check is not enough. The configured CDP override can be alive during session creation and still die before the next command. That creates a poisoned task session: navigation looks good, but follow-up commands hit a dead socket.

## Durable debugging pattern
1. Reproduce on one task id with the exact sequence `navigate -> snapshot -> console/eval`.
2. Check whether the override is reachable *before* navigation.
3. Separately test whether it remains usable *after* navigation.
4. If direct websocket probing works but Hermes follow-up commands still fail, treat it as a session-durability / poisoned-session problem, not only a static endpoint problem.
5. Distinguish this from supervisor-only issues by testing whether the same failure appears even when supervisor attach is bypassed.

## Durable repair pattern
- Keep the preflight guard for obviously dead configured overrides.
- Additionally detect runtime failure shapes from command results.
- On runtime CDP failure for a `cdp_override` session:
  - stop the supervisor for that task;
  - replace the task session with local Chromium;
  - preserve the last successful URL in session state;
  - reopen that URL locally;
  - retry the failed command once;
  - annotate the recovered result/session with fallback metadata.

## Notes
- This is a browser-runtime repair pattern, not a frontend-app diagnosis.
- A passing `navigate` call is not enough evidence that the browser session is healthy.
- Keep runtime fallback metadata distinct from preflight fallback metadata so later triage can tell which branch fired.
