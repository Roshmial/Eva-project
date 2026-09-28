# Multi-user hardening: version contract and shared write-path acceptance

Use when a local-first MVP must become safe for several concurrent users/tabs without changing the stack.

## Core pattern

1. Backend compare-and-swap
- Apply optimistic locking on shared mutable routes like `/api/me`, `/api/jobs/<id>`, admin user update paths, and similar write endpoints.
- Stale payloads should return `409` with a stable machine code such as `version_conflict`.

2. Frontend propagation
- Carry `version` through draft/edit state, not only list/detail payloads.
- Include `version` in all real write flows, including small side actions:
  - profile save;
  - admin user edit;
  - full entity save modal;
  - rename/display-name/alias update;
  - pause/resume or other status toggles.
- Map `version_conflict` to a Russian human-readable message.

3. DB-level shared-entity invariants
- If the product model says there should be exactly one materialized helper object (for example, one `job` thread per `(user_id, job_id)`), enforce it in the database.
- Safe rollout order:
  - detect/dedupe old duplicates;
  - then create the unique index.

4. Migration safety
- When extending old local operational tables with new `NOT NULL` fields, add explicit default/backfill logic for legacy SQLite/DuckDB rows.
- Otherwise migration can fail before runtime verification even starts.

## Minimal acceptance set

- syntax check frontend and backend;
- backend smoke with at least one stale-update regression;
- health check on live backend;
- live login into the real UI shell;
- live open of the key edited surfaces (for example: profile, jobs, admin);
- confirm browser console has no JS errors after the hardening pass.

## Practical note

For Misha's local-first web/admin tasks, this belongs under the existing MVP delivery umbrella rather than a separate narrow skill, because it is usually one phase of the larger end-to-end delivery, not an isolated specialty.