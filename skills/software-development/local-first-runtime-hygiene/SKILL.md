---
name: local-first-runtime-hygiene
description: Verify, restart, and harden local-first multi-process web runtimes without mixing contours or trusting stale processes.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [local-first, runtime, acceptance, debugging, copilotkit, web-ui, backend, frontend, security]
    related_skills: [web-ui-runtime-verification, copilotkit-local-first-web-integration, local-browser-runtime-hardening, systematic-debugging]
---

# Local-first runtime hygiene

## When to use

Use this skill when a local-first web app has several moving parts and any of these are true:
- frontend, backend, and AI/runtime sidecar run on separate local ports;
- there may be sibling repos, old contours, or stale listeners on nearby ports;
- browser acceptance fails in ways that may be caused by the wrong process, wrong proxy target, or stale code;
- file/open-link flows or message-attachment flows must work end-to-end on a live runtime;
- admin screens, dashboards, jobs, or CopilotKit-like proxy flows must be checked on the real contour, not by code inspection alone.

This skill is especially useful for Misha-style work: local-first, Russian-facing UI, live runtime acceptance, minimal duplicate infrastructure, and no drifting back into already-settled naming debates.

## Core rule

Treat runtime verification as a contour-management task first and a feature-debugging task second.

Do not diagnose product bugs until you have proved all of the following:
- which repo owns each running process;
- which port each component actually listens on;
- which proxy target the frontend uses by default;
- which backend database/data directory the live backend is using;
- that the browser/session is hitting the canonical contour, not a sibling one.

## Canonical workflow

1. Establish the canonical contour.
- Write down the intended tuple: frontend port, backend port, runtime/sidecar port.
- Check live listeners and map each listener back to cwd or process command line.
- If a sibling repo is still listening on an old port, mark it as contamination risk immediately.

2. Verify the backend before touching the UI.
- Hit health/service-info endpoints.
- Hit AI proxy info endpoint from the backend side, not only the sidecar side.
- For auth-protected resources, verify both unauthorized and authorized behavior.

3. Verify the frontend-to-backend contract.
- Inspect default proxy config and compare it to the canonical backend port.
- If a launch script overrides the proxy target, still fix stale defaults when they create future ambiguity.
- Do not accept “works when launched a special way” as the only valid state if the in-repo default points at the wrong backend.

4. Parameterize the contour before polishing acceptance.
- Put canonical host/port/base-URL values behind one shared runtime env layer, not scattered literals across launchers, Vite config, sidecar scripts, and browser smoke files.
- Derive `FRONTEND_URL`, backend base, `/api` base, CORS allow-origin, and sidecar/runtime URL from the same small set of variables.
- Treat `works only when launched with ad-hoc overrides` as unfinished hygiene if in-repo defaults still point at legacy ports.
- When server deploys may use different ports, fix this once in launcher/env composition instead of editing many files.
- Before any stop/restart/disable action, write a plain host→role→port matrix for the live contour, for example: `frontend surface`, `prod backend`, `dev backend`, `runtime sidecar`. Do not act until each target port is mapped to an explicit role.

5. Verify open-link flows end-to-end.
- Check list payloads for download/open URLs.
- Call the returned URL on the live backend with auth.
- Do this for both user-file flows and message-attachment flows.
- If the frontend expects a route that does not exist in the backend, treat it as a real product bug and fix the backend contract, not the acceptance script.

6. Only then run browser acceptance.
- Prefer existing project smoke/acceptance scripts first.
- If smoke fails, distinguish between product failure and acceptance-script drift.
- If labels/placeholders/tabs changed but the feature still works, patch the smoke script to the real UI contract.

6. Finish with a hygiene pass.
- Remove or stop stale legacy listeners that can steal traffic or create false diagnostics.
- Record the restart order and the canonical contour in a runbook and decision log.
- Note any dangerous duplicate DB files, backup DBs, or legacy data directories that may confuse future runs.

## Restart order

When all components may have changed, restart in this order:
1. AI/runtime sidecar
2. backend
3. frontend
4. browser acceptance

Reason: the backend often proxies to the sidecar, and the frontend often proxies to the backend. Restarting bottom-up reduces false negatives.

## Acceptance pitfalls

### Pitfall: stale sibling contour looks like a product bug
A nearby repo listening on an old backend port can make it appear that a fix “did not deploy”.

Countermeasure:
- always inspect live listeners;
- map ports to process cwd/command;
- kill or isolate legacy listeners before concluding the fix failed.

### Pitfall: outdated frontend proxy defaults
If `vite.config.js` or equivalent still points to an old backend port, acceptance can silently hit the wrong contour unless launched with special env overrides.

Countermeasure:
- align the default proxy target with the canonical backend for the active contour;
- treat proxy drift as architectural debt, not just a launch-script problem.
- prefer one shared runtime env file or equivalent composition layer that feeds launcher scripts, Vite proxy, sidecar runtime, and smoke scripts from the same variables.

### Pitfall: hardcoded ports survive in smoke and sidecar scripts
Even after the main frontend/backend are fixed, browser smoke, sidecar metadata, or debug probes can keep old literals like `8792/8793/8794` and send future acceptance back into a mixed contour.

Countermeasure:
- sweep launchers, smoke scripts, sidecar entrypoints, and diagnostic probes for legacy literals;
- centralize them behind shared env variables and derived URLs;
- verify both the default contour and one alternate-port composition path before calling the runtime portable.

### Pitfall: smoke script drift vs product bug
UI smoke often breaks on renamed buttons, tabs, or placeholders even when product behavior is fine.

Countermeasure:
- patch the smoke selectors after verifying the feature manually or through API/runtime evidence;
- do not misclassify selector drift as backend breakage.

### Pitfall: attachment/download route mismatch
It is common for the frontend to construct a file/attachment URL that the backend does not expose, or for backend records to store `relative_path` while the download route only looks for `local_path`.

Countermeasure:
- verify the exact URL returned to the UI;
- verify the route exists in the backend;
- support both canonical stored-path shapes when migrating data models;
- add regression coverage for both user files and assistant/message attachments.

### Pitfall: auth/session writes conflict under DuckDB concurrency
A local-first backend can look healthy in unit tests yet still throw intermittent 500s on `login`, `bootstrap`, or session restore when multiple requests mutate `sessions` concurrently. In DuckDB this often surfaces as `TransactionContext Error: Conflict on tuple deletion!` during revoke/cleanup/touch paths.

Countermeasure:
- treat session maintenance as a serialized critical section, not as harmless background bookkeeping;
- protect cleanup, revoke, issue, touch, and logout writes with one process-level lock when the backend runs threaded;
- after the fix, run a small concurrent login stress check instead of trusting one successful manual login;
- if the symptom appears on `login`, inspect revoke-old-sessions and cleanup-before-login first.

### Pitfall: registry sync updates payload but leaves canonical sources inactive
When a registry evolves from legacy item keys to canonical source classes, sync code may update labels/payload/sort order but fail to reactivate existing inactive rows. The API then returns a narrowed live registry even though the code knows about the broader inventory.

Countermeasure:
- in sync paths, treat `inactive` or soft-deleted canonical rows as candidates for reactivation, not as already-synced rows;
- when a canonical item is present in the computed inventory, set `is_active = 1` and clear soft-delete markers during sync;
- validate the fix through the live API (`bootstrap`, admin policy endpoints), not only by inspecting code;
- keep legacy aliases as compatibility inputs, but do not let them remain the source of truth for the visible registry.

### Pitfall: admin metrics query assumes the wrong schema
Admin/health endpoints often drift because they query columns that exist in related tables but not in the queried one.

Countermeasure:
- verify aggregate queries against the real schema;
- for “active users from messages”, join through threads/users when messages only carry `thread_id`;
- beware of inflated metrics from multi-join aggregation and use `COUNT(DISTINCT ...)` where appropriate.

### Pitfall: health endpoint is slow because it does real work, not because the whole server is saturated
In small local-first runtimes a `health` route can become the loudest latency signal even when CPU, RAM, and disk are mostly fine. A common cause is that the endpoint synchronously does expensive DB work and then shells out to another runtime bridge (for example, listing Hermes cron jobs through a subprocess on every request). Under parallel probes this looks like a resource crisis, but the primary issue is an over-fat health path.

Countermeasure:
- measure endpoint latency separately for `health`, `service-info`, frontend shell, and sidecar info instead of assuming one slow endpoint means the whole contour is overloaded;
- when `health` is much slower than `service-info`, inspect the endpoint body for synchronous subprocess calls, job enumeration, or heavy aggregate queries;
- keep liveness/readiness probes cheap: DB connect, basic app status, and minimal contract checks only;
- move job counts, deep diagnostics, and expensive bridge calls into a separate diagnostics/admin endpoint;
- if you stress-test concurrency, compare 1/2/4/8-worker latency so you can distinguish architecture/path cost from raw host saturation.

### Pitfall: auth/admin GET endpoints hide expensive bridge calls or registry sync work
After `health` is fixed, the next latency offenders are often not the obvious write paths but "read-only" auth/admin screens that quietly do too much per request. Common patterns are:
- list endpoints that mix local DB rows with `hermes_list_jobs()` or another runtime bridge on every GET;
- per-item serializers that trigger several follow-up SQL queries per row (`N+1` behavior on jobs/users/threads);
- settings/diagnostics endpoints that run `sync_data_source_registry()` or another mutating reconciliation step inside the normal GET path;
- broad reference builders that construct whole runtime dictionaries when the caller only needs one narrow list.

Countermeasure:
- after public-path checks, rank authenticated/admin endpoints by live latency instead of assuming the slowest work is in the browser;
- if the live DB is locked by the running backend, copy the DB to a temp path and run authenticated timing probes against that copy so you can profile safely without mutating production;
- separate concerns: keep normal GET paths read-only, move bridge refresh/sync work to explicit admin actions, startup hooks, or short-lived caches;
- for list endpoints, inspect serializers for owner/subscription/count lookups done per row and replace them with pre-aggregated queries where practical;
- if one endpoint mixes local records with remote/Hermes jobs, consider lazy-loading the remote slice only on the dedicated tab instead of on every overview request.

### Pitfall: moving the frontend to another server is treated like a full-stack migration
In this contour, moving the frontend off-host is usually a resource-isolation step, not a reason to replatform backend, sidecar, auth, or storage. Teams often overcomplicate the move by exposing internal sidecars directly to the browser or by keeping a dev server as the long-lived production surface.

Countermeasure:
- treat frontend relocation as a narrow step: ship a production static build and keep backend-owned `/api` and `/api/copilotkit` as the browser contract;
- prefer reverse proxying `/api/*` from the frontend host to the backend host instead of teaching the browser about internal backend/sidecar ports;
- do not expose the CopilotKit/runtime sidecar directly to users when the backend already owns the proxy contract;
- update backend CORS allow-origins for the new frontend origin before acceptance;
- after the move, re-run live checks for auth, bootstrap, admin flows, and authorized file/download flows specifically in the cross-origin contour.

### Pitfall: a new frontend surface is needed, but the old `8791/8793/8794` contour must stay alive as dev
A common migration mistake is to treat “raise frontend on a new port/server” as permission to duplicate or move backend/runtime too early. That creates contour drift and doubles the amount of moving pieces without adding real validation value.

Countermeasure:
- first classify the old contour explicitly: if `8791/8793/8794` is still needed as dev, leave it intact instead of "cleaning it up" out of habit;
- when only the browser entrypoint must change, clone only the frontend surface: create a second frontend unit/process with overridden `HERMES_WEB_FRONTEND_HOST` and `HERMES_WEB_FRONTEND_PORT`, while reusing the same backend and backend-owned `/api` proxy contract;
- prefer a dedicated systemd user unit for the second frontend surface instead of ad-hoc shell launches, so both entrypoints can coexist and survive restarts predictably;
- before stopping any contour, build and verify a host→role→port matrix in plain terms (`frontend surface`, `prod backend`, `dev backend`, `runtime sidecar`) so you do not treat a frontend host as if it were the backend host or vice versa;
- audit the unit dependency graph for the new frontend surface: if it proxies a remote backend, it must not keep `Requires=` or `After=` on the old local backend/runtime units, otherwise stopping dev services will also kill the production-facing frontend entrypoint;
- if the frontend uses a dev-server proxy like Vite, add an explicit proxy error handler for `/api` so upstream backend failures return short JSON/text errors rather than HTML error pages from the frontend shell;
- verify shutdown isolation explicitly: stop the dev units, then confirm the new frontend port still serves `/` and still proxies `/api/service-info` to the intended backend;
- verify both surfaces independently: the old dev frontend and the new frontend should each return `200`, and the new one must successfully proxy `/api/service-info` (or equivalent) to prove it is attached to the intended backend;
- record the split in the decision log as `dev contour` versus `new entrypoint`, so later cleanup does not accidentally shut down the wrong surface.

## Security checks for local-first acceptance
Do these on the live contour, not just by code reading:
- unauthorized request to protected endpoint returns 401/403;
- authorized request to file/attachment route returns 200;
- file routes verify ownership/visibility;
- backend normalizes relative paths and prevents escaping data dir;
- CORS is restricted to the intended frontend origin;
- response headers at least include frame/referrer protections appropriate to the app;
- secrets are not written into decision logs or long-lived notes.

## User-specific operating preference
For this class of task with Misha:
- do not loop back into already-decided naming or wording questions unless new evidence changes the decision;
- before asking again for a target host, port, or server role during a cutover, first re-read the current conversation and the existing contour notes/decision log, then inspect the live unit overrides or runtime env; if the target was already fixed earlier, act on it and verify instead of bouncing the question back to the user;
- if the user says `исправь на боевом` or equivalent, default the execution scope to the live remote contour, not just the local workspace copy or a temporary staging runtime; make the fix on the active service and verify it through the live endpoint;
- focus on live backend/frontend/runtime acceptance, operational cleanliness, and working open links;
- when the bug is real, fix the product contract and add regression coverage;
- when the problem is only stale runtime or stale smoke selectors, say that plainly and fix the operational/test layer.

## Deliverables
A good outcome should leave behind:
- one canonical contour description;
- one restart algorithm;
- stale listeners stopped or clearly isolated;
- live checks for health/admin/open-link/auth behavior;
- regression coverage for any backend contract bug fixed;
- a concise decision-log entry;
- backlog/runbook/doc updates when the runtime status materially changed (for example, when a former acceptance blocker is now closed and only hardening tails remain);
- optional reference notes under `references/` for contour-specific quirks.

## References
- `references/restart-safe-hermes-web-contour.md` — restart-safe pattern for Hermes Web + CopilotKit + TG-API: systemd user units, launcher PATH, private env files, sidecar venv bootstrapping, and simulated-restart verification.
- `references/8793-copilotkit-runtime-hygiene.md` — concrete lessons from the Hermes Web `8793/8791/8794` contour: stale sibling backend, proxy drift, file/message open-link fixes, admin health schema bug, and browser-runtime path discipline.
- `references/runtime-env-and-acceptance-account.md` — canonical contour parameterization via shared env, alternate-port portability, dedicated acceptance account, and onboarding-modal handling in live browser acceptance.
- `references/duckdb-session-conflicts-and-registry-reactivation.md` — live failure pattern for threaded DuckDB auth/session writes plus the registry-sync reactivation rule for canonical source classes.
- `references/runtime-diagnostics-and-frontend-relocation.md` — how to separate endpoint-path latency from whole-host saturation, plus the narrow-step rules for moving frontend to a different server.
- `references/auth-admin-endpoint-latency-audit.md` — post-health audit pattern for ranking authenticated/admin endpoints, spotting hidden bridge/sync work, and choosing the next pre-migration backend fixes.
