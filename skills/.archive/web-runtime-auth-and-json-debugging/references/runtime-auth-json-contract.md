# Runtime auth + JSON contract smoke checklist

Use when a web runtime shows random logout, session loss after reload, or raw HTML/non-JSON errors in the UI.

Session lessons captured here:
- A frontend can create a false "session expired" symptom by clearing the stored token on any bootstrap failure. Only clear token for explicit auth errors such as `invalid_token` or `auth_required`.
- Public boot requests like `service-info` and `setup-status` should use the same JSON-safe request path as authenticated calls, so HTML/framework pages are normalized before reaching UI state.
- Secondary bootstrap reads (`files`, `jobsMeta`, and similar) should be tolerant; partial failure should not destroy a valid restored session.
- Same-origin checks matter. Verify `/api/...` through the frontend host, not only direct backend port checks.
- If a backend already has a generic exception handler but `/api/does-not-exist` still returns HTML, add explicit `HTTPException` handling and re-test 404 live.
- Before changing credentials for smoke tests, confirm the live datasource from process env. A repo-local DuckDB file may exist while the live backend actually uses Postgres via DSN.

Minimal live smoke sequence:
1. `POST /auth/login` -> 200 JSON
2. `GET /auth/session` -> 200 JSON
3. `POST /threads` or equivalent create action -> success JSON
4. `POST /threads/{id}/messages` or equivalent action -> success JSON
5. invalid token -> JSON error
6. missing route -> JSON 404 error, not HTML

Why this matters:
Health endpoints alone can stay green while the real user path still fails on reload, send, or framework-level error pages.
