# Hermes Cron job UI contract mismatch

Session-derived durable pattern:

## Symptom cluster
- job rename looks editable in Jobs UI but does not persist as expected;
- recipients block suggests user assignment, but runtime delivery still follows another path;
- problem appears on jobs mirrored from Hermes Cron rather than native web jobs.

## Root cause pattern
`source_of_truth = hermes_cron` means the job is translated from Hermes cron into web shape.
The web UI may expose generic job controls, but the real mutable fields are constrained by the cron bridge.

## Fields to compare
- UI field: `display_name`
- Cron writable field: `name`
- Web recipients expectation: `fixed_user` / `fixed_thread`
- Cron delivery reality: `deliver` -> delivery target(s)

## Safe handling rule
- map `display_name` to `name` only where that is truly the cron-side writable title;
- if recipient editing cannot be translated faithfully, reject it with an explicit API error;
- update UI copy and action visibility so admins do not think unsupported operations are available.

## Minimum live checks
1. GET job detail and inspect `source_of_truth`.
2. PATCH rename using the UI-facing field and verify backend mapping.
3. PATCH unsupported recipient shape and verify explicit failure, not silent success.
4. Re-open the live UI and confirm the invalid recipient affordance is hidden or reframed.
