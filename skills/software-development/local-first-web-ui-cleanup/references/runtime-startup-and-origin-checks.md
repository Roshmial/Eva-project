# Runtime startup and origin checks for local-first web UI

When a local-first web UI looks broken after login, verify runtime wiring before assuming the feature code is wrong.

## What to check first

1. Confirm the frontend is opened on the canonical allowed origin, not an ad-hoc static server origin.
2. Confirm the backend process serving the expected port is the current build, not an older leftover process.
3. If the UI boot path does several authenticated fetches at once, reduce startup concurrency before deeper debugging.

## Proven debugging pattern

- If login succeeds by API but the UI stays on the login screen, inspect the startup sequence (`restoreSession`, `bootAuthenticated`, equivalent).
- Probe individual authenticated refresh calls one by one before blaming a single endpoint.
- If individual calls pass but the full boot path fails, suspect a startup race or overly broad `Promise.all(...)` on critical screen-loading requests.
- Check whether two app-start paths run in parallel (for example public-screen init and session restore).

## Durable fixes that worked here

- Replace parallel startup of public init and session restore with one controlled `startApp()` flow.
- Load critical authenticated boot data sequentially first; only defer or parallelize clearly non-critical follow-up work.
- For mixed-source UI surfaces, verify live data only after confirming the browser is pointed at the same backend process that contains the new code.

## Port and process pitfall

A false negative can come from testing against a stale backend process that still owns the port. Symptom: file contents are updated but runtime behavior still matches the old implementation. Before concluding the patch failed, verify which process actually listens on the backend port and restart the correct one.

## Jobs-specific verification lesson

For "all jobs" UI changes, verify with real mixed data instead of assuming both sources exist. If the environment only has Hermes cron jobs, create one local Web MVP job so the UI can prove mixed rendering, source labels, and read-only/editable differences on live data.
