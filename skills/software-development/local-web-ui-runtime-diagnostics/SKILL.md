---
name: local-web-ui-runtime-diagnostics
description: Diagnose and verify local-first web UIs when browser wrappers, frontend proxy processes, login flows, and app boot state can fail at different layers.
---

# Local Web UI Runtime Diagnostics

Use this when a local web UI must be verified end-to-end and the main uncertainty is *which layer is failing*:
- browser wrapper / CDP session;
- independent browser runtime;
- frontend static/proxy server;
- backend API/auth;
- frontend post-login boot and screen visibility.

This skill is for class-level runtime diagnosis, not for one project only.

## Core rule

Always separate these questions in order:
1. Is the backend API alive?
2. Is the frontend origin itself returning HTTP?
3. Can an independent browser runtime open the page?
4. Does login/auth work at the API layer?
5. After auth, does the UI actually transition from login state to app shell?

Do not blur these into one vague "UI is broken" conclusion.

## Recommended workflow

1. Verify backend health directly.
   - Check service/health endpoints first.
   - Verify the exact API routes needed for the smoke scenario.
2. Verify the frontend origin directly with HTTP, before using a browser tool.
   - If the port listens but `curl` hangs with no bytes, treat the frontend server/proxy process as hung and restart that process.
3. If the built-in browser wrapper or CDP session is flaky, run an independent Playwright probe.
   - Use this to distinguish app defects from wrapper defects.
4. If browser launch fails because of missing local libs, prefer user-space browser libs and env vars over adding external infrastructure.
5. Authenticate against the backend API directly.
   - Confirm auth works independently of the login form.
6. For UI-state verification, inject the real token into localStorage, reload, and inspect DOM state markers.
   - This isolates post-login boot from form-submission issues.
7. Only after the shell becomes visible should you continue to feature-specific visual smoke.

## CORS / origin mismatch pattern for local-first UIs

A frequent local-runtime failure is not "backend down" but a hostname mismatch between the frontend origin and the backend CORS/config contract.

Typical symptom:
- the page opens;
- backend health checks via terminal/curl look healthy;
- but the browser shows `Failed to fetch` during startup or `service-info` / `setup/status` bootstrap.

High-probability check order:
1. Identify the exact browser origin actually used by the page.
   - `http://127.0.0.1:8790` and `http://localhost:8790` are different origins.
2. Inspect frontend runtime config, not just source assumptions.
   - Check `window.__APP_CONFIG__`, `apiBaseUrl`, and `serviceInfoPath` in the live page.
3. Probe backend CORS with the real `Origin` header.
   - A backend that always returns `Access-Control-Allow-Origin: http://127.0.0.1:8790` will still look healthy from terminal, but browser requests from `http://localhost:8790` will be blocked.
4. Distinguish direct backend access from frontend proxy access.
   - If direct `http://127.0.0.1:8788/api/...` works but browser bootstrap still says `Failed to fetch`, suspect origin/CORS first.

Durable fix pattern:
- For local-first frontend config, prefer deriving backend origin from `window.location.hostname` instead of hard-coding only `127.0.0.1`.
- For local backend CORS defaults, allow both common local origins when appropriate:
  - `http://127.0.0.1:<port>`
  - `http://localhost:<port>`
- When multiple local origins are allowed, echo back the matching request origin and add `Vary: Origin`.

Acceptance check:
- open the UI from both `localhost` and `127.0.0.1` when both are realistic entry points;
- confirm startup no longer shows `Failed to fetch`;
- verify the live runtime config now points to the correct backend host for the current origin.

## DOM-state diagnostic pattern

When the app uses a login screen plus hidden app shell, inspect exact state markers:
- whether the login screen is hidden;
- whether the app shell is hidden;
- whether privileged nav/buttons exist in DOM;
- whether role-specific controls exist in DOM.

Interpret carefully:
- token present + admin DOM nodes exist + app shell still hidden => likely frontend boot / restore-session / visibility-switch defect;
- login API 200 but form flow stays on login screen => narrow the issue to frontend login/boot path, not backend auth;
- browser page closes/crashes before DOM inspection => browser runtime instability, not yet an app verdict.

## Stale-runtime / stale-DOM pattern

A frequent local UI trap is: the file on disk is correct, the frontend origin serves the correct bytes, but the live browser DOM still shows the old screen.

Use this check order:
1. Verify the source file on disk contains the new marker strings.
2. Fetch the served asset over HTTP directly and compare it with the local file when needed.
   - Good probes: presence/absence of unique strings such as new button labels, new class names, or new placeholders.
   - If needed, compare hashes of local and served `app.js` / `index.html`.
3. Separately inspect the live DOM in the browser.
   - Example: `document.getElementById(...)`, `document.querySelector(...)`, or a short `outerHTML` slice of the target section.
4. If served asset is new but DOM is old, treat it as a stale runtime/browser-state problem before concluding the patch failed.
5. Force a clean runtime reload with cache-busting navigation, e.g. `/?v=<timestamp-or-token>`, then re-check the DOM.

Important distinction:
- "served file is old" => deployment/proxy/source-of-truth problem;
- "served file is new, DOM is old" => stale browser/runtime state;
- "served file and DOM are new, but screen still wrong" => actual app logic/rendering defect.

## Browser-wrapper vs real app execution pattern

If browser tools report `(empty page)` or a white screen, do not jump straight from that symptom to "React did not render".

Use this separation:
1. Fetch the live `index.html` and built JS/CSS assets directly from the target origin.
2. Confirm the mount path exists in the served JS.
   - Good probes: `createRoot(`, `document.getElementById("root")`, unique login/onboarding strings.
3. Execute the served bundle in an isolated DOM runtime such as `jsdom` with minimal browser shims.
   - The goal is not visual acceptance.
   - The goal is to answer a narrower question: does the live bundle populate `#root`, and with what first screen?
4. Compare the results across layers.
   - `jsdom` populates `#root` but browser wrapper still shows white/empty page => likely visual/layout/browser-runtime artifact, not proof of early mount failure.
   - `jsdom` also leaves `#root` empty or throws during eval => now you have evidence for a real frontend boot/runtime defect.
5. Report that distinction explicitly.
   - "served bundle executes and mounts login DOM" is different from "screen is visually acceptable in a real browser".

Important: treat `jsdom` execution as a diagnostic discriminator, not as a substitute for final UX acceptance.

## Verification standard

A runtime pass is only complete when you have all of these:
1. backend/API proof;
2. frontend-origin proof;
3. browser-runtime proof;
4. UI-state proof;
5. feature-specific proof for the target screen.

## React controlled-state / handler-scope pitfall

When fixing a live React UI bug around a form control or mode selector, do not stop at "make the input controlled". Also verify that the state lives in the same component scope as the code that consumes it.

High-risk symptom chain:
- a `select` or input used to be uncontrolled or read from DOM directly;
- the fix introduces `useState(...)` inside a child component;
- submission or side effects still happen in the parent component;
- runtime then fails with `X is not defined` or the chosen value silently resets.

Safe correction order:
1. Identify where the authoritative action happens.
   - Example: `submitChatMessage` lives in `App`, not in `ChatScreen`.
2. Store the controlling state in the lowest common owner that can both render the control and execute the action.
3. Pass value + setter/callback down to the presentational child.
4. Replace DOM reads such as `document.getElementById(...).value` with state-derived request building.
5. After the code fix, rebuild, restart the exact live frontend service, and verify the served source on the target port contains the new state/prop markers.

Verification probes:
- confirm the live code exposes the parent-level state, e.g. `const [chatSourceMode, setChatSourceMode] = useState(...)`;
- confirm the child receives `value` and `onChange`/callback props;
- confirm the submit path uses the same state variable, not a DOM lookup or out-of-scope symbol.

This pattern prevents a common regression: fixing reset behavior in the child while introducing a scope error in the parent submit path.

## Chat composer / sidepanel ergonomics pattern

When a chat UI uses a separate sidepanel composer on desktop, do not assume the issue is only visual preference. Treat these symptoms as a class-level usability defect worth structural correction:
- the composer appears to "disappear" or get visually lost;
- the user must scroll awkwardly to find the input area;
- the message list consumes too little vertical space while the composer consumes too much width or height;
- desktop behavior is worse than the already-working mobile layout.

Preferred correction order:
1. Check whether the mobile stacking model is already the better interaction.
   - If yes, prefer reusing that structure on desktop instead of fighting a fragile right-column layout.
2. Move the composer below the message list when the sidepanel is the source of loss/confusion.
3. Make the composer sticky to the bottom of the viewport or chat shell.
4. Add bottom padding to the message list so the last messages are not hidden behind the sticky composer.
5. Increase message-panel height/width so the conversation becomes the dominant surface again.
6. Trim composer chrome before adding new controls.
   - Reduce heading size, internal padding, and default textarea rows before changing workflow.

Implementation heuristics:
- Prefer a single-column chat workspace (`messages -> composer`) over a two-column (`messages -> sidepanel`) layout when reliability beats density.
- Sticky composer usually needs both `position: sticky` and a parent container that does not clip it unexpectedly.
- If the composer is sticky at the bottom, leave explicit space inside the scrollable messages panel.
- Update any helper copy that still says the next action is "on the right" after moving the composer below.

## Twin frontend instance verification pattern

When two frontend ports are supposed to represent different runtime contours, do not trust the port numbers alone.

Verify in this order:
1. Check the live service/unit definitions and process environment.
   - Confirm `WorkingDirectory`, launch script, and backend-target env vars such as `HERMES_WEB_FRONTEND_BACKEND_BASE`.
2. Hash the served source/assets from each port.
   - If hashes match, they are serving the same frontend bytes even if the ports differ.
3. Verify the backend target from the live process environment, not only source config.
4. Only after that conclude whether the user is seeing the same data because of shared frontend code, shared backend target, or both.

This avoids the common false assumption that a "new port" automatically means a distinct environment.

## Hung frontend proxy pattern

If the frontend port is listening but the UI still does not open, explicitly test for a wedged static/proxy process:
- `ss` may show `8790` as listening while `curl http://127.0.0.1:8790/` hangs or times out;
- backend `8788` may still answer `service-info` with `200`, so the failure is not backend health;
- browser navigation may time out with a vague page-load failure even though the process still exists.

In that situation:
- treat the frontend server as unhealthy even if the PID is alive;
- read its log and look for request-handling exceptions such as `BrokenPipeError`;
- do not assume "port open" means "UI usable".

For lightweight Python local proxies/servers, a durable fix can be concurrency rather than another restart. A useful pattern is switching from `socketserver.TCPServer` to `socketserver.ThreadingTCPServer` and enabling `daemon_threads = True`, so one stalled client or broken pipe does not wedge the whole frontend origin.

Also keep origin handling explicit:
- if the UI may be opened via both `127.0.0.1` and `localhost`, verify both config and backend CORS behavior;
- prefer frontend config derived from `window.location.hostname` over hard-coding one hostname when the contour is otherwise local-first.

## Notes

See `references/react-controlled-state-live-runtime.md` for a concise recipe for React controlled-state fixes where submit logic lives in a different component scope. See `references/hermes-web-admin-runtime-smoke.md` for a concrete Hermes Web pattern using a frontend proxy on `8790`, backend auth on `8788`, and token-based shell verification. See `references/frontend-proxy-hang-pattern.md` for the specific hung-proxy diagnostic and fix pattern. See `references/browser-empty-page-vs-jsdom-mount.md` for the discriminator pattern where browser tools show an empty page but direct execution of the served bundle still mounts DOM. This reference overlaps partially with browser-debugging skills; keep the overlap focused on local web-app runtime diagnosis rather than generic browser setup.
