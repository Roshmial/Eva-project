# Local browser runtime stabilization and UI regression smoke

Use this pattern when a local-first web/admin MVP appears broken in live browser verification, but it is still unclear whether the defect is in the product or in the local browser/runtime path.

## Practical sequence

1. Prove backend/auth correctness first.
   - Check the real auth path with direct API calls before editing frontend code.
   - Verify bootstrap-adjacent endpoints separately (`auth/session`, `bootstrap`, `me`, core list endpoints, admin endpoints if relevant).

2. Find the real frontend storage/session contract.
   - Confirm the actual localStorage/session key used by the app instead of guessing legacy names.
   - Wrong client-side bootstrap keys can create false-negative UI conclusions.

3. Stabilize the existing local browser path before changing architecture.
   - Prefer the already available Playwright/browser stack.
   - If the environment is missing local browser prerequisites, solve them in user space and wrap the fix in a reusable script/env layer.
   - Do not leave the working recipe only in chat history.

4. Use layered probes, then promote the winner.
   - Plain browser probe: can the browser open the page at all?
   - Auth bootstrap probe: can the session/token bring the shell up?
   - Full acceptance smoke: chat/files/profile/admin or the equivalent real user flow.
   - Once a probe proves the path, move the end-to-end one out of `tmp/` into a canonical project script.

5. Verify fixes on two levels.
   - Reproduce the buggy flow directly against the API when possible.
   - Re-run the same flow through the real browser/UI after the fix.

## What to codify after success

- One canonical browser/runtime launcher script.
- One canonical UI acceptance smoke command.
- README section with the official commands.
- Regression assertions for the exact flow that failed (not just status code success).

## Typical anti-patterns

- Patching frontend logic while backend auth is already healthy.
- Assuming a browser crash proves a product bug.
- Keeping the only useful smoke in `tmp/` after the incident is resolved.
- Verifying a repaired multipart/message flow only by HTTP status and not by returned payload shape.
