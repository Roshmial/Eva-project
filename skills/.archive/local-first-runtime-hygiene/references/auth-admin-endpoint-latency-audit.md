# Endpoint latency audit after fixing over-fat health paths

Use this note when a Hermes-style local-first backend still feels slow after `/health` is cleaned up.

## What to suspect next

The next bottlenecks are often authenticated GET endpoints, not the browser shell and not the obvious write paths.

Typical hidden costs:
- `hermes_list_jobs()` or another runtime bridge inside a normal list/overview GET;
- `N+1` per-row serialization queries for owner/subscriber/count metadata;
- registry reconciliation like `sync_data_source_registry()` executed inside a read path;
- broad reference builders that materialize whole runtime dictionaries when the caller only needs one narrow slice.

## Safe audit pattern

1. Measure cheap public routes first:
- `/api/service-info`
- `/api/health`
- `/api/setup/status`
- any other public diagnostics route

2. If the live backend holds a DuckDB lock, copy the DB file to a temp path.

3. Import the backend app against the DB copy with scheduler/chat processor disabled.

4. Create or reuse an admin user in the copied DB.

5. Use the Flask test client to time authenticated/admin endpoints 5 times each and sort by mean latency.

This gives a stable ranking without perturbing the live contour.

## Ranking signals that matter

If you see results shaped like this, focus on backend path cost before blaming the host:
- `/api/jobs` far slower than `/api/admin/health`
- `/api/admin/user-sources` or `/api/admin/jobs` much slower than other admin screens
- `/api/bootstrap` and `/api/jobs/meta` slower than expected because they rebuild large reference payloads

## Concrete remediation heuristics

### `/api/jobs`
Usually means both of these are happening:
- local DB list path;
- remote/Hermes jobs bridge mixed into the same request.

Plus each job may trigger several extra SQL lookups in the serializer.

Fix direction:
- do not mix remote/Hermes jobs into the default list if the screen can lazy-load them;
- collapse per-job count/owner/subscription lookups into pre-aggregated queries where practical.

### `/api/admin/user-sources`
Usually means a diagnostics/settings GET is doing both sync and bridge work.

Fix direction:
- remove registry sync from normal GET;
- run sync at startup, on explicit refresh, or behind a short cache;
- remove `hermes_list_jobs()` from the default payload unless the screen truly needs it on first paint.

### `/api/admin/jobs`
Usually slow by design because it is a bridge view.

Fix direction:
- avoid pulling it into broad bootstrap/overview requests;
- prefer tab-local loading or a short TTL cache.

### `/api/feedback/reasons` or similar narrow lists
If a narrow endpoint is still slow, inspect whether it reuses a whole reference-building pipeline.

Fix direction:
- replace whole-runtime builders with a narrow query for the exact dataset the endpoint needs.

## Rule of thumb

Before a migration, remove hidden expensive work from hot GET paths first. It gives real user-facing relief without forcing a bigger architecture move.
