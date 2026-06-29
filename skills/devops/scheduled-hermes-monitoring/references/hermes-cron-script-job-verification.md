# Hermes cron script jobs: practical verification notes

Use this reference when creating `no_agent=true` Hermes cron jobs backed by a local script.

## Durable lessons

- Hermes cron script jobs do not accept an arbitrary absolute script path at creation time.
- The script must live under `~/.hermes/scripts/` and the job should reference only that filename or a relative path inside the scripts directory.
- If the real editable script belongs in a project workdir, keep two copies intentionally:
  - workspace/project copy for normal development and direct testing;
  - `~/.hermes/scripts/` copy for the scheduler.
- After `cronjob action='create'`, do not stop at create success.
- After `cronjob action='run'`, do not stop at `last_status=ok` alone.
- Verify the persisted output artifact in `~/.hermes/cron/output/<job_id>/` and inspect the actual report text.

## Good verification sequence

1. Run the script directly from the project workdir and confirm the report text is sensible.
2. Copy or write the scheduler copy under `~/.hermes/scripts/`.
3. Create the cron job with:
   - `no_agent=true`
   - `script=<filename under ~/.hermes/scripts/>`
   - explicit `workdir`
4. Trigger `cronjob action='run'` once.
5. Confirm:
   - `last_status=ok`
   - a fresh file exists under `~/.hermes/cron/output/<job_id>/`
   - the output file contains the expected user-facing report.

## Why this matters

Without checking the persisted output, you can mistakenly report success when only the trigger succeeded but the scheduler later failed, rendered the wrong script copy, or delivered empty/unhelpful text.
