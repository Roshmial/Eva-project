# Hermes jobs as single source of truth — migration reference

Use this pattern when a web MVP accidentally created a second operational job model beside Hermes cron.

## Symptom
- Hermes has the real scheduled jobs.
- Web backend stores synthetic `app.jobs` rows.
- Analytics mirrors `app.jobs`, so reporting shows the synthetic list rather than the real execution layer.
- UI create/edit flows speak the synthetic schema, not the Hermes cron schema.

## Correct target
- Hermes cron = canonical operational truth for jobs.
- Web backend = projection/API facade over Hermes jobs.
- Frontend = admin-facing view first; read-only until Hermes-compatible editing exists.
- Analytics = downstream mirror of Hermes job state.

## Safe migration sequence
1. Stop treating `app.jobs` as the list of real jobs.
2. Add a backend bridge that reads Hermes cron directly.
3. Make `/jobs`, `/jobs/<id>`, and admin job endpoints return projected Hermes jobs.
4. Hide jobs from non-admin users by default in MVP.
5. Disable synthetic create/edit/subscribe flows rather than keeping incompatible writes alive.
6. Rebuild analytics job snapshots from Hermes cron data, not from `app.jobs`.
7. Verify counts line up across:
   - Hermes cron list
   - backend `/api/jobs`
   - analytics `app_jobs_raw`

## Important design rule
If the UI needs additional metadata later, store it as projection data keyed by Hermes `job_id`. Do not recreate a second scheduler truth.

## What to verify after migration
- backend health job count matches Hermes job count;
- `/api/jobs` and `/api/admin/jobs` match Hermes count;
- job detail payload clearly marks source of truth;
- analytics rows for jobs reflect Hermes ids and statuses;
- legacy synthetic rows no longer drive the UI.

## Practical UI rule
If the existing web form was designed around synthetic fields, disable it until a Hermes-native form exists. A temporary read-only admin UI is safer than silent drift.
