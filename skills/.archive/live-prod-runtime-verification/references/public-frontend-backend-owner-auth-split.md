# Public frontend ↔ backend-owner auth split

Use when a public web frontend appears healthy, but auth, user state, or exported artifacts disagree between:
- the public frontend proxy path;
- local/localhost backend probes;
- a separately reachable backend host.

## Fast diagnosis

1. Confirm the public frontend owner service and its proxy target.
   - Check the serving unit / launcher.
   - Look for `HERMES_WEB_FRONTEND_BACKEND_BASE` or equivalent.

2. Compare the same login against both paths.
   - `frontend_host/api/auth/login`
   - `backend_host:port/api/auth/login`

3. If responses differ, stop treating localhost fixes as evidence for the public UI.
   - The contour is split.
   - You must operate on the real backend-owner.

4. On the backend-owner, inspect the running process env.
   - Read `/proc/<pid>/environ` for DSN/runtime storage.
   - Confirm whether it is Postgres, DuckDB, SQLite, etc.

5. Only then seed/reset a smoke user.
   - Create or reset the user in the actual backend-owner datastore.
   - Re-check both direct backend login and public proxy login.
   - Only after both succeed run browser acceptance.

## Why this matters

A common false path is:
- local backend login works;
- local password reset works;
- API export works locally;
- but the public frontend still returns `401`.

That usually means the public frontend is not using the local datastore/backend you just changed.

## Minimal acceptance after repair

- public frontend login succeeds;
- direct backend login succeeds with the same smoke user;
- a real browser-driven action through the public UI succeeds;
- any exported artifact is verified by actual download, not only by API status.
