---
name: multi-host-runtime-contour-verification
description: Verify and operate split frontend/backend runtimes across multiple hosts without mixing dev and prod surfaces.
---

# Purpose

Use this skill when a web app is split across hosts or ports and you need to debug, patch, restart, or verify the correct runtime surface without editing the wrong machine.

This is especially important for Hermes Web style deployments where dev and prod are intentionally split across different hosts and ports.

Reference files:
- `references/8803-prod-serving-path.md` — durable pattern for replacing a public Vite dev server with a production static/proxy frontend while preserving the existing split frontend/backend contour and verifying it through real auth/read/write traffic.

Reference: `references/hermes-web-runtime-contours.md`

# When to use

Trigger this skill when any of the following is true:

1. Frontend and backend live on different hosts.
2. Dev and prod use the same repo but different host:port contours.
3. The user says a fix was applied "not there" or corrects which server owns which surface.
4. Browser/API failures may come from hitting the wrong contour rather than broken code.
5. You need to change model routing, proxying, or UI behavior in a multi-host runtime.

# Core rule

Before editing, restarting, or SSH-ing anywhere, write down the canonical runtime contour as a host:port map and classify each surface:

- dev frontend
- dev backend
- dev auxiliary services
- prod frontend
- prod backend
- prod auxiliary services

Do not proceed until each target surface is mapped to a specific host and port.

# Required workflow

## 1. Build the contour map first

Create a small working map in your notes or response:

- host
- port
- role
- environment
- local vs remote relative to the current machine

Explicitly mark when a host is the current machine. If the target surface is on the current host, do not waste time trying to SSH into that same machine as if it were external.

## 2. Verify ownership before patching

For each requested fix, answer these questions first:

- Which host owns the frontend actually shown to users?
- Which host owns the backend API actually serving that frontend?
- Is the requested fix frontend-only, backend-only, or cross-surface?
- Is the active service the dev contour or the prod contour?

If frontend and backend are split, treat them as separate deploy targets even if they share one repository.
If you patch locally, do not assume prod changed: first copy the changed files to the owning host, verify a few exact patch markers in the remote file contents, then restart or rebuild only the service that owns that code.
For Hermes Web style contours, verify deployment per surface: backend prompt/API changes can be validated on the backend host with targeted tests and health checks even when the prod frontend lives on a different host.

## 3. Patch the correct surface only

- Frontend/UI text, selectors, layout, labels, build artifacts, proxy config: patch the frontend-owning host.
- API routing, queue workers, model fallback, auth, jobs, bootstrap payload: patch the backend-owning host.
- If a user-facing feature spans both, patch each side deliberately and verify them independently before doing end-to-end smoke tests.

## 4. Verify per surface, then end-to-end

Minimum verification order:

1. Service status on the owning host.
2. Local HTTP probe on that host for the exact port.
3. API probes for `/api/health`, `/api/service-info`, and `/api/bootstrap` when relevant.
4. Frontend runtime verification on the actual user-facing port.
5. One end-to-end user flow.

Do not treat a successful backend check as proof that the correct frontend was updated.

## 4a. For destructive production data cleanup, verify the live backend DB owner first and take a rollback snapshot

Use this when the user asks to clean production data such as users, sessions, jobs, or related records on a split runtime.

Required sequence:

1. Confirm that the requested action belongs to the backend-owning host, not the frontend host.
2. Inspect the live backend unit and listener on the target host (`systemctl --user status`, `ss -ltnp`, process cmdline).
3. Inspect the live process environment to confirm the actual DB/backend DSN and project root used by the running service.
4. Query the live DB first to see the exact rows that will be affected.
5. Take a DB backup before deletion (`pg_dump` or equivalent) and record the backup path in the final reply.
6. If the schema does not enforce foreign keys/cascade cleanup, delete dependent rows explicitly in a safe order before deleting the primary rows.
7. Re-query the DB after cleanup and verify the backend health endpoint still returns OK.

Why this matters:

- In split deployments, it is easy to clean the wrong host or the wrong database if you trust a nearby checkout instead of the live unit.
- For one-off production cleanup, direct DB deletion can be safer and more complete than partial app-level status changes, but only after backup and row-level verification.

## 5. Resolve the live runtime owner before trusting repo files

When verifying backend routing, limits, model chains, or feature flags, do not start from an arbitrary repo checkout or a nearby `runtime_env.sh` and assume it is authoritative.

Use the live listener first:

1. Identify the process bound to the target port.
2. Capture `PID`, `cmdline`, `cwd`, `exe`, and `/proc/<pid>/environ`.
3. Find the actual systemd unit or wrapper script that launched it.
4. Read the wrapper script to see which env file it sources.
5. Only then inspect the code and env files that the live process actually uses.

This avoids false conclusions when:

- multiple similar repos exist on the host;
- the unit starts from a wrapper script instead of directly from the backend directory;
- `services/backend/runtime_env.sh` exists but the real service sources `scripts/runtime_env.sh` or another parent-level env file;
- raw env variables suggest a fallback chain, but the deployed parser or routing code collapses that chain at runtime.

For model fallback verification, confirm three layers separately:

- configured env values;
- parsed effective candidate chain inside deployed code;
- externally visible runtime state from `/api/health` or equivalent metadata.

A value present in environment is not proof that the running backend will actually attempt the next model.

Reference: `references/live-runtime-owner-and-env-source.md`.

# UI model-selector rule

When exposing model routing to end users, prefer semantic user-facing modes over raw provider/model names.

Good pattern:

- "Текущая работа"
- "Глубокое исследование"

Avoid exposing the entire internal fallback chain in the UI unless the user explicitly wants a low-level selector.

Internal routing can still map those semantic modes to multiple concrete models.

# Fallback routing rule

For agent-style work, default to free-first routing when quality is acceptable:

1. Try free models first.
2. Keep paid models as fallback for quota exhaustion, rate limits, or provider failure.
3. Keep the UI stable while backend routing handles fallback internally.
4. When the backend resolves attempt chains from the currently requested model, ensure the primary model is the first item in its own candidate list. If the requested model is not the head of the ordered chain, the retry path may silently collapse or start from the wrong model.
5. After changing candidate order, verify the live process environment, not just files on disk.

Capture fallback decisions in backend metadata such as:

- selected default model
- candidate chains
- reasoning candidate chains
- limit/blocked reason
- usage counters

# Pitfalls

## Pitfall: confusing current host with remote target

If the current machine already is the host for the requested frontend port, do not start with SSH discovery. First inspect local services, local systemd units, local port listeners, and local runtime files.

## Pitfall: verifying config from the wrong execution context

A split deployment can look correct on disk and still run with different live values.

Before concluding that routing or limits are wrong, check the effective environment of the actual listening process and confirm which user owns the systemd unit. In practice this means:

- identify the PID bound to the target port;
- inspect `/proc/<pid>/environ` for the live variables;
- inspect `/proc/<pid>/cgroup` to find the real unit name;
- restart/query the unit as the owning user, not as root running an unrelated `systemctl --user` session.

Do not trust ad hoc shell imports under the wrong user as proof of runtime state.

## Pitfall: verifying only one side of a split deployment

A backend `200 OK` does not prove the user-facing frontend was rebuilt or restarted. A frontend build does not prove its `/api` target points to the intended backend.

For file-open / attachment fixes on split contours, verify the exact user-facing frontend path, not only the backend download endpoint. A direct backend `GET` returning `200` can still leave the user with a broken open-flow if the frontend uses a fragile browser pattern.

Practical rule:
- if the frontend opens files via `fetch -> blob -> window.open(objectUrl)`, treat that as a likely instability point for production webviews and popup-restricted browsers;
- prefer opening the real backend attachment URL directly from the frontend, ideally with the auth token already embedded in the query string when the backend explicitly supports tokenized `GET` downloads;
- after changing the open-flow, verify the actual public frontend bundle/asset hash changed on the user-facing port, not only that the backend code was deployed.

## Pitfall: showing internal model names to users by default

Users usually need stable work modes, not a long model list. Hide internal fallback chains behind semantic modes unless low-level control is explicitly requested.

# Minimal verification checklist

- Confirm canonical dev/prod contour.
- Confirm whether the target surface is local or remote.
- Confirm the exact systemd unit for that surface.
- Confirm the exact host:port answering requests.
- Confirm frontend proxy target if frontend and backend are split.
- Confirm `/api/health` and `/api/bootstrap` reflect the intended routing state.
- Confirm one live user flow on the actual user-facing contour.

# References

- `references/hermes-web-runtime-contours.md` — concrete example of split dev/prod contour mapping and verification notes.
