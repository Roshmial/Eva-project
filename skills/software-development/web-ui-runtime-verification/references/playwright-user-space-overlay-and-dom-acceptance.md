# Playwright user-space overlay and DOM-first acceptance

When live browser acceptance is blocked by missing Chromium shared libraries and root package install is unavailable, use a local overlay instead of stopping the verification.

## Durable pattern

1. Confirm the blocker is native browser startup, not app logic.
- Run the browser binary directly or inspect `ldd`.
- Separate `missing .so` failures from app/runtime failures.

2. Pull only the needed runtime libs into user-space.
- Download the required Ubuntu/Debian packages with `apt-get download`.
- Extract them with `dpkg-deb -x` into a workspace-local directory such as `.local-libs/...`.
- Build `LD_LIBRARY_PATH` from all extracted `usr/lib/x86_64-linux-gnu` directories.
- Re-run `ldd` and the browser binary until Chromium itself starts.

3. Once Chromium starts, stop treating this as an OS-deps task.
- If browser launch now works but the script still fails, switch immediately to DOM/runtime debugging.
- Do not keep iterating on package guesses after `--version` works.

4. If the first Playwright scenario fails on selectors, inspect the live DOM before changing product code.
- Dump actual `textarea`, `input`, `button`, and `main/#root` signals from the running page.
- Do not assume CopilotKit popup selectors if the canonical contour is chat-first.
- Re-target the probe to the real composer placeholder and real send button used by the product UI.

5. If screenshot crashes after the page already rendered, do not throw away the acceptance run.
- Some headless setups can render DOM and process input but still crash on screenshot/font paths.
- In that state, treat screenshot as an optional artifact, not the primary proof.
- Accept the run on DOM signals plus network events when they are stronger than the screenshot path.

## Good acceptance signals without screenshot

For a chat/dashboard flow, prefer this bundle:
- browser opened the real frontend URL;
- a real textarea accepted the typed message;
- a real send action triggered the expected POST request;
- backend returned the expected status code;
- the page DOM now contains the expected artifact container/text/section count.

Examples of strong DOM evidence:
- `dashboardSections > 0`
- `messageBubbles` increased
- `document.body.textContent` contains the expected dashboard title and assistant answer
- captured network event shows `POST /api/threads/.../messages -> 201`

## Practical takeaway

If browser launch is fixed via user-space libs and the page already proves the user flow through DOM plus network logs, the task is complete enough to report as live runtime verified even if screenshot capture itself remains unstable.