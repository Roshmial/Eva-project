# React parity runtime checklist for local-first Vite migrations

Use this when a legacy web UI has a parallel React/Vite surface and the task is to prove parity by live runtime, not just by source diffs.

## What to confirm first

1. Find the real npm root before running any build command.
- Do not assume `package.json` lives next to `src/`.
- Check the project root for `package.json` and `vite.config.*`.
- If Vite uses `root: 'services/frontend-react'` or similar, run build/dev from the npm root, not from the `src/` subtree.

2. Separate three confidence levels.
- `build green`
- `live runtime opens`
- `deep flows verified`

Do not collapse them into one verdict.

## Parity verification pattern

1. Build the React surface from the real npm root.
- Example class of command: `npm run react:build`

2. Check whether the target port already serves a live runtime.
- If the port is occupied but the page answers successfully, treat that as an existing verification surface, not automatically as a blocker.
- Verify that the page title/app shell matches the intended React surface before proceeding.

3. Prefer live browser verification when automation contracts are stale.
- If existing smoke scripts still target legacy selectors/DOM ids, do not force the new React UI to satisfy old automation blindly.
- Use browser navigation and per-screen snapshots to verify the actual React contract.

4. Verify screens one by one, not in a single burst.
- Chat
- Profile
- Jobs
- Admin overview
- Admin users
- Admin operations
- Admin references

Capture a fresh snapshot after each transition.

5. Treat legacy smoke mismatch as a test-contract issue until proven otherwise.
- Old scripts that expect selectors like legacy `#promptInput`, `#screenAdmin`, `#adminUsersTable` are evidence of a stale acceptance harness, not immediate evidence that React parity failed.

## Useful acceptance language

Use wording like:
- "build passed, runtime visible, deep parity not yet fully proven"
- "screen renders and is interactive, but legacy-parity on IA/table contour is still pending"
- "functional regression reduced, final parity verdict still requires screen-by-screen acceptance"

Avoid wording like:
- "fully parity with no regressions" unless all critical flows were verified live.
