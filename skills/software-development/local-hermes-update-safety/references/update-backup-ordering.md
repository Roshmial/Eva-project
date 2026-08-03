# Hermes update backup ordering — July 2026 reference

## Problem

The update flow created a pre-update backup before it even knew whether there were any new commits to install. On a machine with regular scheduled backups, this produced unnecessary backup churn for no-op `hermes update` runs.

## Agreed operational rule

- Check availability first.
- Create pre-update backup only when the command is about to mutate checkout or runtime.
- Keep backup on runtime-repair path even when the checkout is already current.

## Concrete implementation pattern

In `hermes_cli/update_cmd.py`:

1. Replace eager `pre_update_snapshot_id = _run_pre_update_backup(args)` with `pre_update_snapshot_id = None`.
2. Add a local helper that runs `_run_pre_update_backup(args)` only once.
3. Compute `commit_count` before stash/checkout-driven mutation logic.
4. Call the helper:
   - before applying real updates
   - before repair when `_venv_core_imports_healthy()` is false
5. Never call the helper on the healthy no-op path.

## Backup overlap assessment used in this session

### Not duplicates

- `eva-hub-daily-backup`: backs up `eva_hub.duckdb`; unrelated to Hermes runtime rollback.
- `cons-project-backup-weekly`: curated web/TG/prod contour backup; different recovery target.

### Partial overlap, still justified

- `eva-github-backup-weekly`: curated Git snapshot of skills, `config.yaml`, `cron/jobs.json`, `scripts/*`.
- Overlaps with some pre-update backup contents but excludes live runtime state like `state.db`, sessions, logs.
- Therefore it is not a substitute for pre-update rollback backup.

## Regression tests added

Target file: `tests/hermes_cli/test_cmd_update.py`

Added coverage for:

1. no-op update does not create backup
2. real update does create backup
3. runtime repair on current checkout does create backup

Useful pattern:
- patch `_run_pre_update_backup`
- make it raise a sentinel `RuntimeError("backup called")`
- assert that the exception appears only on mutation paths

## Verification commands that passed

- `pytest -q tests/hermes_cli/test_cmd_update.py::TestCmdUpdatePreUpdateBackupTiming`
- `pytest -q tests/hermes_cli/test_cmd_update.py tests/hermes_cli/test_update_venv_health.py`
- `python3 -m compileall hermes_cli/update_cmd.py tests/hermes_cli/test_cmd_update.py`

## Takeaway

For self-update flows, backup timing should align with mutation boundaries, not command start. This preserves rollback safety without turning every no-op availability probe into backup noise.
