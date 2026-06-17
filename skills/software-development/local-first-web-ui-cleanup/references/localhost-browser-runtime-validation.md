# Localhost browser runtime validation for local-first web UI

Use this when a local web app appears to have a broken login or frozen shell, but static code review is inconclusive.

## Durable lessons from Hermes Web MVP

1. Separate input-simulation issues from product logic.
   - In headless browser runs, an input can receive focus and still fail to retain `keyboard.type()` or `fill()` text.
   - Verify DOM state directly before concluding the form is broken.
   - Fallback: set `el.value` inside `page.evaluate(...)` and dispatch `input` + `change` events.

2. Distinguish successful auth from failed post-login boot.
   - A `200` from `/api/auth/login` does not prove the authenticated UI is healthy.
   - Trace the full boot chain after login and log every `/api/*` response.
   - If the shell stays hidden, inspect parallel bootstrap requests before editing the login UI.

3. When frontend expects JSON but receives HTML, suspect a failing downstream endpoint.
   - Symptom: frontend banner or console shows `Unexpected token '<'`.
   - Usual meaning: an API route returned an HTML 404/500 page while frontend tried to parse JSON.
   - Next move: identify the exact route and reproduce it directly against backend.

4. Validate runtime state, not only source code.
   - If source contains an endpoint but live backend returns 404, check whether an old or mis-started process is serving traffic.
   - Restart backend using the project's canonical run script before rewriting code.

5. Keep a deterministic browser fallback for localhost acceptance.
   - If the primary browser wrapper is unreliable for localhost, use a direct Playwright probe.
   - Include: login, post-login API tracing, app-shell visibility, and critical user flows.

## Suggested fallback probe structure

- `focus/type` probe: confirm whether headless typing changes `input.value`.
- `input-props` probe: capture `readOnly`, `disabled`, `outerHTML`, and manual value assignment.
- `login-debug` probe: submit login, capture auth response, inspect banner and shell classes.
- `boot-debug` probe: log all `/api/*` responses after login to isolate the exact failing request.
- `ui-smoke` probe: once boot succeeds, verify chat, files, profile, and admin sections end-to-end.

## Practical decision rule

Before patching frontend login UX, answer these in order:
- Did the auth endpoint return success?
- Did the frontend store/show the submitted values?
- Which post-login API call fails first?
- Is the failure in current source, or only in the running process state?

If those answers point to backend/runtime, fix that first; otherwise UI work risks being noise instead of progress.
