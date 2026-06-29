# Live store split: Postgres investigation vs DuckDB live runtime

Date: 2026-06-25

## Why this reference exists

Concrete prod lesson: a convincing delivery investigation in `Postgres app.*` turned out not to describe the live Web UI at all. The running backend on `:8791` was serving from backend-local DuckDB:
`services/backend/data/hermes_web_app.duckdb`

## Symptoms

- Postgres contained plausible `users / threads / messages / hermes_job_*` rows for the target digest.
- Repairs in Postgres looked successful.
- Browser/live verification still did not show the expected chat.
- Fresh API tokens inserted into Postgres stayed `invalid_token` in the live backend.
- Inspecting the running backend process and querying its local DuckDB showed a different user universe and thread set.

## Root cause pattern

The operator assumed there was one canonical app DB because the hostname and codebase matched. In reality there were two materially different contours:

1. a Postgres contour with one set of users/threads;
2. the actual running Web backend contour on backend-local DuckDB with a demo user (`victoria-pilot@demo.local`) and no preexisting `ТГ Дайджест` thread.

## Correct diagnostic sequence

1. Confirm the live backend process.
   - Inspect `ps eww -p <pid>` and launcher path.
   - Do not rely only on nearby files or old notes.

2. Confirm the real DB driver and target used by the running service.
   - Check `HERMES_WEB_BACKEND_DRIVER`, `HERMES_WEB_BACKEND_DSN`, `HERMES_WEB_BACKEND_DB_PATH` if present.
   - If env is sparse, infer from runtime behavior and service startup path.

3. Query the actual live store for:
   - target user row;
   - target thread existence;
   - current messages in that thread;
   - current sessions in that same store.

4. Only after that decide whether the correct action is:
   - repair an existing delivery in-place;
   - re-run reconcile;
   - or create/seed the missing job thread in the actual live store.

## Practical repair pattern from this case

In the live DuckDB contour:
- the expected `ТГ Дайджест` thread did not exist;
- the right fix was to create the job thread for the live demo user and insert restored digest messages there;
- backend code was also patched so TG digest delivery prefers payload/CSV reconstruction over raw cron reasoning output.

## Important framing rule

Do not conflate these as one bug:
- missing/incorrect digest content;
- live auth/runtime instability that blocks browser verification.

You can successfully restore the content in the real store and still be blocked from final browser acceptance by a separate runtime/session issue.

## Reusable takeaway

When a repair in DB A looks correct but the live UI still behaves as if nothing changed, treat “wrong live store” as a first-class hypothesis before blaming the renderer or repeating DB edits.
