# React isolated migration baseline

Use when a local-first web UI must migrate to React without breaking the currently working runtime.

## Recommended pattern

1. Do not rewrite the working frontend in place by default.
   - Create an isolated project copy for the migration branch.
   - Give the new frontend its own dev/preview port.
   - Keep the existing backend API contract unchanged unless backend migration is explicitly part of the task.

2. Build the first milestone as a real runtime baseline, not a scaffold.
   - A Vite/React app that only renders login or a placeholder is not enough.
   - The first meaningful milestone is: authenticated shell + all main screens wired to real backend data.
   - For Hermes Web MVP this meant at least: `Чаты`, `Профиль`, `Задачи`, `Управление`.

3. Verify with live runtime, not just build success.
   - `npm run build` (or equivalent) is necessary but insufficient.
   - Open the React runtime in the browser and confirm login plus screen-level data rendering.
   - Check browser console for JS errors during the live pass.

4. Be explicit about parity boundary.
   - Separate what is already migrated from what still remains in the legacy frontend.
   - Typical remaining gaps after the baseline milestone: create/edit/bulk admin flows, full job create/edit contours, edge-case microflows, canonical React smoke.
   - Do not imply full migration completion when only the baseline milestone is complete.

5. Leave durable breadcrumbs.
   - Save launch instructions for the React copy.
   - Add a migration status file in the copied project.
   - Update decision-log with: why isolation was chosen, where the React copy lives, which port it uses, what was verified live, and what remains to reach parity.

## Why this works

This pattern minimizes risk to the working runtime while still forcing honest progress. It avoids both extremes:
- reckless in-place rewrites on the only working frontend;
- fake progress where only scaffolding exists and no real screen is wired.

## Concrete example shape

- working runtime stays on its existing port
- copied project hosts React branch on a new port such as `8792`
- React branch proxies to the same `/api` backend
- live verification confirms login + main screens + no console JS errors
