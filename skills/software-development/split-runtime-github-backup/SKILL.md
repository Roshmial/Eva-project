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

## 3. Build a curated repository, not a raw home-directory dump

Create a dedicated backup repo directory and copy only the allowed scope.

Recommended sections:
- `local-<host>/project/`
- `local-<host>/runtime-systemd/`
- `remote-<host>/project/`
- `remote-<host>/runtime-systemd/`
- `README.md`
- `BACKUP_SCOPE.md`

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

# Output contract

When finished, report:
- what host(s) the backup covers
- what repository received the push
- what schedule was configured in both host timezone and Moscow time
- what old scheduler, if any, was removed

# References

- See `references/combined-contour-checklist.md` for a concise checklist for split frontend/backend GitHub backups.
