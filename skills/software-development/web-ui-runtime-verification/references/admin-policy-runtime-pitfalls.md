# Admin policy live-acceptance pitfalls for local-first runtime

Use this when a React/local-first admin screen looks broken or half-hydrated during live verification, especially around policy/source registry forms.

Key lesson from Hermes Web React `8793/8791/8794` acceptance:

1. Do not assume an empty or partially rendered admin policy block is a frontend-only bug.
   - In this session, the real blocker was backend runtime degradation before the policy form logic ran.
   - `GET /api/setup/status` returning `500` left the frontend in an error/bootstrap state.
   - Later, `PATCH /api/admin/dashboard-policy` failed before policy validation because `require_auth()` hit transient DuckDB lock / attach conflicts.

2. Acceptance order for policy/source screens:
   - First verify bootstrap endpoints used before the admin screen hydrates (`/api/service-info`, `/api/setup/status`, auth/session/me/bootstrap paths).
   - Then verify the admin read path (`GET /api/admin/dashboard-policy`).
   - Only after that verify the write path (`PATCH /api/admin/dashboard-policy`).
   - Final proof is save -> reread -> restore, not just seeing controls in the DOM.

3. For strict policy acceptance, prove filtering from backend data, not just labels in the UI.
   - `local_only` must leave only local/internal sources.
   - `global_only` must leave only external/global sources.
   - `local_first` may expose both layers, but local remains the default priority.

4. When browser acceptance is noisy, combine live UI and API evidence.
   - Use UI to prove the screen hydrates, shows the expected registry, and can submit changes.
   - Use API reread immediately after save to prove the new state actually persisted.
   - Restore the original setting at the end so the acceptance run is reversible.

5. Durable runtime hardening pattern for this class of app:
   - bootstrap/readiness endpoints should degrade gracefully instead of taking down the whole frontend on a brief DB lock;
   - auth gates on hot admin/read paths should retry short-lived DuckDB lock/attach conflicts instead of surfacing random `500` errors.

Canonical inventory confirmed in this session for dashboard policy:
- top-level: `user_attachment_dataset`, `local_dataset_registry`, `internal_connector`, `external_connector`, `web_research`
- internal connectors: `hermes_api`, `copilotkit_runtime`, `telegram_analytics_workspace`
- external connectors: `telegram_api`, `google_api`, `public_procurement_api`
