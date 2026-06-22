# Dual-topology branching for runtime backups

Use this pattern when the user needs two different backup views at once:

1. Combined production contour
- Example: frontend on one host, backend/runtime on another, plus related operational layers.
- Purpose: preserve the real live topology.
- Recommended branch: `main`.

2. Standalone host contour
- Example: the backend/runtime server by itself, with its local TG API, Hermes runtime, systemd units, and deploy docs.
- Purpose: make one host independently rebuildable.
- Recommended branch: `standalone-<host>` such as `standalone-178`.

## Why branches instead of one tree

If both shapes are pushed into the same branch, one of them will overwrite the other’s operational meaning.

The combined contour answers:
- how production is really split today
- which host contributes which runtime responsibility

The standalone contour answers:
- what is needed to rebuild this single host as a self-contained runtime layer

Those are different recovery questions.

## Minimum contents for the standalone host branch

- `project/**`
- `runtime-systemd/**`
- `tg-api/**` when that host owns a Telegram/data-ingest contour
- `hermes-runtime/**` when Hermes config, cron jobs, or reusable scripts matter operationally
- root docs:
  - `README.md`
  - `BACKUP_SCOPE.md`
  - `CONTOUR_MAP.md`
  - `DEPLOYMENT_AND_BACKUP_LOGIC.md`
  - `PROD_CONTOUR_ARCHITECTURE.md`
  - `PROD_CONTOUR_LOGIC.md`
  - `DISASTER_RECOVERY_RUNBOOK.md`
  - `MODEL_FALLBACK_LOGIC.md`
  - optional scope docs such as `TG_API_SCOPE.md` and `HERMES_RUNTIME_SCOPE.md`

## Scheduler rule

Treat the two topologies as separate products:
- separate refresh script
- separate working tree
- separate cron job
- explicit branch checkout/push inside the standalone script

This prevents a future maintenance edit from accidentally pushing the standalone snapshot into `main`.

## Verification checklist

After setup confirm:
- branch name is correct
- remote is correct
- commit exists on the intended branch
- weekly cron job exists and targets the standalone script
- key docs and runtime layers are present in the backup tree
