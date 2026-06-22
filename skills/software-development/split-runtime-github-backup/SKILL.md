---
name: split-runtime-github-backup
description: Build and automate curated GitHub backups for live runtimes whose frontend/backend/deploy contour spans multiple hosts.
version: 1.0.0
author: Eva
---

# When to use

Use this skill when the user wants a backup repository for a live app/runtime, but the real contour is split across hosts or ports.

Typical triggers:
- frontend runs on one host/port, backend on another host
- a “project backup” must include code plus real deployment logic
- the user wants scheduled GitHub backups of a live contour
- there are multiple systemd units / launcher scripts that together form the real app

# Goal

Create a curated private GitHub backup that captures the working contour, not just a source tree copy.

The backup should preserve:
- app code that matters operationally
- deploy/package logic
- launcher scripts
- runtime systemd units and drop-ins
- key runbooks/docs

The backup must exclude:
- secrets and `.env*`
- runtime databases and data directories
- logs, caches, screenshots, dumps
- `node_modules`, `.venv`, `dist`, `__pycache__`

# Core rule

For split contours, map the LIVE contour first and back up according to the runtime shape, not according to repo naming or old ports mentioned in chat.

Always separate:
- code state
- deployed state
- runtime topology

# Workflow

## 1. Confirm the live contour

Before building the backup, verify:
- which host serves the frontend
- which host serves the backend
- which ports are live now
- which systemd units are actually active
- which launcher scripts those units call
- which project directory is the real working directory

Do not assume `8803`, `8793`, or any named port from memory. Check the active services first.

## 2. Choose the backup topology

Use one of two patterns:

### A. Single-host backup
Use when one host contains the full live contour.

### B. Combined split-host backup
Use when different hosts own different runtime parts.

In the combined case, prefer a CENTRAL backup job on the host that can reliably read both sides of the contour. This is better than independent weekly backups on each host because it avoids drift and keeps one repository as the source of truth.

### C. Dual-topology backup in one GitHub repo
Use when the user needs BOTH:
- a combined split-host backup that reflects the real production contour, and
- a standalone backup for one host (for example, the backend/runtime server by itself).

In that case, do not force both shapes into the same branch.

Recommended pattern:
- keep the combined production contour on `main`
- publish the standalone host backup to a dedicated branch such as `standalone-178`

Reason:
- the two backups answer different recovery questions
- pushing the standalone host snapshot into `main` will silently destroy the combined contour model
- branch separation preserves both operational views without duplicate repositories

## 3. Build a curated repository, not a raw home-directory dump

Create a dedicated backup repo directory and copy only the allowed scope.

Recommended sections:
- `local-<host>/project/`
- `local-<host>/runtime-systemd/`
- `remote-<host>/project/`
- `remote-<host>/runtime-systemd/`
- `README.md`
- `BACKUP_SCOPE.md`

When the contour has adjacent operational layers that are required for a practical rebuild, include them explicitly instead of pretending the app repo alone is enough.
Common examples:
- `tg-api/` or another Telegram/data-ingest contour
- `hermes-runtime/` with `config.yaml`, `cron/jobs.json`, and reusable scripts
- dedicated root docs for architecture, logic, zero-start deployment, and model fallback

The README should explain:
- what each host contributes
- what is intentionally excluded
- where the live services point
- what scheduler updates the backup

## 4. Copy files safely

For local files, normal filesystem copy is fine.

For remote files:
- list the allowed files first
- exclude volatile/runtime directories before copying
- support binary files like `.docx` by copying bytes, not text

If a remote project contains mixed text and binary docs, never use a text-only SSH read path for everything.

## 5. Preserve deployment logic explicitly

In addition to project code, include:
- systemd unit files
- systemd drop-ins / overrides
- launcher shell scripts
- deploy/package manifests
- runtime runbooks / deployment guides

A “backup of the project” is incomplete if it omits how the live services are actually started.

## 6. GitHub connection strategy

Prefer pushing from the host that runs the scheduled backup.

If a remote host must push directly, it needs its own SSH key and `known_hosts` setup. But if one central host can assemble the full contour, prefer central push from that host rather than maintaining multiple GitHub auth paths.

## 7. Automate the refresh

For recurring updates:
- write a deterministic script that rebuilds the curated tree
- commit only if there are changes
- push to `origin/main`
- schedule it weekly

For split contours, the scheduled job should run where the combined snapshot is assembled.

When the user gives a Moscow-time window, convert it explicitly from the host timezone. If the host runs in UTC, document the conversion in the job setup.

If the repository carries multiple backup topologies:
- combined contour on `main`
- standalone host contour on another branch

then each topology needs its own deterministic refresh script and its own scheduler entry. Keep the branch target explicit inside the script so a later edit cannot accidentally push the wrong topology into `main`.

## 8. Verify after setup

Do not stop after writing the script.

You must verify:
- local script run succeeds
- repository has the expected remote
- push to GitHub succeeds
- scheduler/job is created with the intended time
- any superseded old scheduler on another host is removed to avoid double backups

# Pitfalls

- Backing up the wrong contour because an old port was mentioned in chat.
- Treating frontend and backend as one host when they are split in production.
- Forgetting systemd drop-ins, which often contain the real runtime overrides.
- Copying remote binary files through UTF-8 text reads.
- Recreating the backup directory by deleting the whole repo, including `.git`.
- Leaving two competing weekly jobs on different hosts.
- Backing up runtime data directories that contain live DB/state.
- Reusing the same Git branch for both combined and standalone backup shapes.
- Forgetting adjacent operational layers like TG API or Hermes cron/scripts, which makes the backup look complete but not actually deployable.

# Output contract

When finished, report:
- what host(s) the backup covers
- what repository received the push
- what schedule was configured in both host timezone and Moscow time
- what old scheduler, if any, was removed

# References

- See `references/combined-contour-checklist.md` for a concise checklist for split frontend/backend GitHub backups.
- See `references/dual-topology-branching.md` for the pattern where one GitHub repo carries both a combined production contour and a standalone host backup on separate branches.
