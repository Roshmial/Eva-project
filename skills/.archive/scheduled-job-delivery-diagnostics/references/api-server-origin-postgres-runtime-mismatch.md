# API-server origin delivery: runtime DB mismatch pitfall

Use this when Hermes cron delivery into Web job threads appears broken, but the investigation mixes file-backed DB assumptions with a live Postgres-backed backend.

## Symptom pattern

- Hermes cron jobs run on time and `last_status='ok'`.
- Separate job-thread delivery is expected in Web.
- Manual recipient inserts into a nearby DuckDB file appear correct.
- Backend reconcile endpoint still reports only fallback recipients like `delivery_target=origin` or `delivery_target=local`.
- This makes it look like `fetch_hermes_job_recipients(...)` is broken when the real problem is that the live backend is not reading that DuckDB file at all.

## What to check first

1. Find the live backend PID from systemd.
2. Inspect `/proc/<pid>/environ` for `HERMES_WEB_BACKEND_DSN`, `HERMES_WEB_BACKEND_SCHEMA`, and related DB env.
3. Check open files / service env before trusting any adjacent `hermes_web_app.duckdb` path.
4. Probe the actual live DB with the service venv/interpreter, not ambient `python3`.

## Why this matters

A Hermes Web service may have repo-local DuckDB defaults in code, while the live runtime is actually launched with:
- `HERMES_WEB_BACKEND_DSN=postgresql:///...`
- schema overrides such as `HERMES_WEB_BACKEND_SCHEMA=app`

In that case:
- writing `hermes_job_recipients` into DuckDB proves nothing about live reconcile;
- empty DuckDB reads are not evidence that prod recipients are missing;
- a false-negative e2e test can waste a lot of time on the cron side even when the remaining issue is simply the wrong DB target.

## Reliable test pattern

1. Confirm the live DSN from the running backend process.
2. Insert the test recipient into that DB and schema using the backend service venv.
3. Commit explicitly.
4. Verify the inserted row from a second connection to the same DSN.
5. Only then evaluate the reconcile endpoint / automatic delivery behavior.

## Related product reminder

For Web-created recurring jobs, the expected target may be a dedicated `thread_kind='job'` conversation, not the original request chat. A failure to reply in the request thread is not by itself proof of delivery failure.
