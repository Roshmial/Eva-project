---
name: local-first-runtime-contour-hygiene
description: Keep a local-first multi-process web app in a single canonical runtime contour; eliminate stale ports/processes, verify live wiring, and treat session cleanup as maintenance rather than product-facing state.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [local-first, runtime, backend, frontend, copilotkit, sessions, cleanup, operations]
    related_skills: [copilotkit-local-first-web-integration, web-ui-runtime-verification, local-first-runtime-hygiene, operational-vs-analytical-data-architecture]
---

# Local-first runtime contour hygiene

## When to use

Use this skill when a local-first web app has several moving parts and any of these symptoms appear:
- multiple backend/frontend instances from old copies of the repo are still running
- the frontend points to the wrong backend port by default
- acceptance results are inconsistent because a stale process serves traffic
- admin pages start drifting toward operational/session counters instead of user-centric product data
- repeated test logins create a large pile of active sessions
- file/open-link flows work in one screen but fail in another because contracts differ

This is especially relevant for Misha-style local-first work: one canonical contour should exist at a time, and the system should be understood through `user_id`, `threads`, and `messages`, not through accidental process leftovers.

## Core principles

1. Pick one canonical contour and state it explicitly.
   Example shape: frontend port, backend port, runtime/proxy port, working tree path.

2. Before debugging product behavior, eliminate stale runtime ambiguity.
   If two repo copies or two ports can answer the same kind of request, fix that first.

3. Treat session state as maintenance data, not as a primary admin/business metric.
   For user/admin summaries, prefer aggregates based on users, threads, messages, jobs, and ownership.

4. Verify live behavior from the running contour, not only from source code.
   A correct patch in the file does not matter if the wrong process is listening.

5. File/open-link flows are product contracts.
   Verify both user file downloads and message attachment links end-to-end.

## Canonical workflow

### 1. Establish the contour of truth

Record all of the following before deeper debugging:
- frontend port
- backend port
- CopilotKit/runtime port if present
- exact repo path for each process
- expected proxy target from frontend to backend

If a legacy contour exists, stop it before continuing.

### 2. Verify listener ownership, not just open ports

For each relevant port:
- confirm that something is listening
- confirm the PID
- confirm the command/cwd belongs to the intended repo copy

Do not accept “port is open” as sufficient evidence.

### 3. Align frontend proxy defaults with the canonical backend

If Vite or another dev proxy still defaults to an old backend port, fix that immediately.
A common failure mode is a healthy frontend that silently proxies `/api` into a retired backend contour.

### 4. Re-check product contracts end-to-end

At minimum verify:
- backend health
- backend service info
- CopilotKit info through both runtime and backend proxy, if both exist
- user file list returns `download_url`
- direct file download works with auth
- message attachment open-link works with auth

If a message attachment route fails, inspect whether the stored payload uses `relative_path` vs `local_path`; support both if the model has drifted across versions.

### 5. Keep admin data user-centric

When an admin endpoint needs activity metrics:
- derive user activity from `messages -> threads -> user_id`
- avoid assuming `messages` directly contains `user_id`
- do not center admin summaries on session counts unless the endpoint is explicitly for auth/session maintenance

Pitfall:
A query like `COUNT(DISTINCT user_id) FROM messages` is structurally wrong if `messages` only stores `thread_id`.

### 6. Session hygiene policy

Use sessions as auth plumbing, not as product-facing summary state.

Recommended policy:
- TTL on sessions
- lazy expiry on authenticated requests
- maintenance cleanup on login and/or auth checks
- on successful login, revoke prior active sessions for that same user unless the product explicitly requires multi-device concurrency
- periodically delete revoked sessions older than a retention window

Why:
Test logins and acceptance runs otherwise create a large misleading pile of active sessions even when nothing is wrong with user behavior.

### 7. Add a regression test for the real failure mode

If you fix any of these issues, add a focused regression test for the exact bug class:
- admin health/user metric query uses proper joins
- repeated login does not grow active sessions beyond policy
- message attachment route resolves stored paths correctly
- file list returns `download_url`

## Pitfalls

- Debugging the latest code while traffic is still served by an old process
- Accepting a legacy backend because the port responds with `200`
- Measuring admin health through session counters instead of user/message activity
- Fixing only `local_path` while stored attachments actually contain `relative_path`
- Leaving old frontend instances alive on adjacent ports so acceptance accidentally targets the wrong build
- Treating session accumulation as the product model instead of an auth-maintenance leak

## Verification checklist

A task is not done until all are true:
- only the canonical frontend/backend/runtime ports remain listening
- old contours are stopped
- frontend proxy default points to the canonical backend
- admin health responds without query errors
- admin user payload does not expose accidental session-derived noise unless intentionally designed
- repeated login follows the intended session policy
- file download and message attachment links both work on the live contour

## References

- `references/runtime-contour-and-session-hygiene.md` — concrete failure modes, fixes, and live-check patterns from a Hermes Web / CopilotKit cleanup pass
