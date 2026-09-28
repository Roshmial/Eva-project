# 8803 user-job modal hydration pattern

When a user reports that `Пользователи -> Назначить задачу` opens an empty or nearly empty modal on Hermes Web:

## First verify the named live contour

- If the user names a concrete runtime like `95.182.85.233:8803`, use that exact surface as the acceptance target.
- Confirm `/api/service-info` on that contour.
- Confirm which process owns the frontend port, its cwd/project root, and the command line.
- Confirm which built assets are currently referenced by `dist/frontend-react/index.html`.
- After rebuild, verify the new asset filenames/timestamps so you know the live surface is actually serving the new bundle.

## Do not jump straight to backend blame

A blank modal can be caused by frontend hydration order:

- modal opens
- screen switches to `jobs`
- `jobsMeta` has not loaded yet
- form controls render with empty template/options, so the window looks blank or broken

## Durable fix shape

Prefer both parts together:

1. preload jobs context before opening create/assign modal
   - ensure `jobsMeta` exists
   - if jobs list is still empty, load jobs state too
2. keep modal non-empty while metadata loads
   - show a visible loading/fallback note
   - disable metadata-dependent controls until templates/users/threads are ready

## Acceptance when credentials are unavailable

If you cannot complete the authenticated click-path in the current session, still verify these facts before reporting progress:

- live frontend port responds
- console has no startup JS crash
- source file contains the new preload/fallback logic
- production build succeeds
- live dist asset names/timestamps changed as expected

This does not replace full authenticated acceptance, but it is materially better than claiming a runtime fix from code inspection alone.
