---
name: remote-runtime-migration-cutover
description: "Migrate an existing self-hosted app stack to a remote VPS with minimal rewrite: inventory current runtime, bootstrap the host, preserve backward compatibility during DB cutover, move sidecar services, and verify the real deployed contour end to end."
---

# Purpose

Use this skill when moving an already-working app or agent-adjacent stack from one environment to a new VPS, especially when the goal is to reuse the current architecture, avoid unnecessary rewrites, and complete a safe cutover with real verification.

Typical fit:
- existing backend/frontend already work and should be moved, not redesigned;
- embedded/local DB must be migrated to PostgreSQL or another server DB;
- sidecar services such as Telegram auth/parsing, schedulers, or agent gateways must move together;
- the user wants a practical deployment path before any bigger architecture cleanup.

# Default stance

Prefer evolutionary migration over rewrite.

1. Reuse the current stack first.
2. Keep the current runtime path working until the new one is verified.
3. Separate infrastructure problems from code-compatibility problems.
4. Do not declare success from code changes alone; require live service checks.

# Delivery standard

A migration is not complete when:
- packages are installed;
- a new server is reachable;
- code compiles locally;
- a migration script exists but has not been run.

A migration is complete only when the target contour is actually running and the main user flows have been exercised on the new host.

# Recommended sequence

## 1. Inventory before touching the server

Capture the minimum set of facts needed to avoid blind deployment:
- repo paths;
- runtime entrypoints;
- current DB file/path and approximate size;
- uploads or state directories;
- env files and secret locations;
- auth/session artifacts for sidecar services;
- current reverse proxy or port layout;
- health/bootstrap endpoints worth testing after deploy.

If there are multiple components, split them explicitly:
- main app/backend;
- frontend;
- DB;
- Hermes/API/gateway layer if present;
- Telegram or other sidecar services.

## 2. Bootstrap the remote host first

Do the boring server work early:
- create a dedicated service user;
- establish SSH key access;
- install base packages;
- create workspace/data directories;
- enable required base services such as PostgreSQL and nginx;
- enable user linger when user-level services are expected.

Reason: this removes deployment noise before you debug app logic.

## 3. Preserve backward compatibility during DB migration

When moving from an embedded DB to PostgreSQL, do not force an all-at-once rewrite if the codebase already has a custom DB layer.

Preferred pattern:
- add a dual-driver path;
- keep old DB path/env support intact;
- introduce DSN-based server DB support;
- normalize placeholder differences centrally if possible;
- add an explicit one-shot migration script;
- add sequence repair/sync after import when integer IDs are involved.

This keeps rollback simple and limits the blast radius.

## 4. Move code compatibility first, remote data cutover second

Order matters:
- make the code capable of speaking to the new DB;
- validate syntax/tests locally if available;
- only then create DB/user/schema on the target host;
- transfer data and run migration;
- cut runtime over to the new DSN;
- verify the app on the target host.

## 5. Treat sidecar services as first-class migration items

For services like Telegram parsing/auth:
- move code;
- move env/secrets;
- move session/state files;
- move channel/config YAMLs or similar config;
- define service boundaries and ports;
- verify auth flows, not just process startup.

A sidecar that starts but cannot use its session/auth artifacts is not migrated.

## 6. Verify the deployed contour end to end

Minimum verification should include:
- service process status;
- reverse proxy reachability if applicable;
- health endpoint latency and correctness;
- one real authenticated flow;
- one main business flow such as parsing, import/export, job start, or thread/message creation;
- log review for hidden errors.

Local tests are supporting evidence, not deployment proof.

# Pitfalls

## Hermes gateway / user-systemd pitfall

When installing Hermes gateway for a dedicated non-root service user, do not assume that running `hermes gateway install` indirectly via `runuser` from root is equivalent to a real user session. User-level systemd operations such as `systemctl --user daemon-reload` may fail if the user bus/session context is missing.

Preferred approach:
- run gateway install/start/enable in the actual target user's environment and user-systemd context;
- if root is used for bootstrap, treat that as file/setup work only;
- perform final user-service activation from the service user's own session or an equivalent user-bus-aware invocation.

See `references/hermes-user-systemd-gateway.md`.

## Hermes API-only migration mode

When the new server should host Hermes only as an internal agent/API runtime, do not carry over messaging integrations just because the old contour had them.

Preferred approach:
- keep Hermes API Server enabled;
- keep gateway only as the local runtime wrapper if the install needs it;
- explicitly leave Telegram and other messaging platforms unconfigured on the new host unless the user asked for them there;
- verify the target shape with `hermes status --all` and service/port checks, not assumptions from copied config.

Reason: during migration, inherited gateway/platform config creates accidental coupling and makes it harder to separate the web app cutover from messaging cutover.

## App-owned profile memory vs Hermes global memory

If the web product is supposed to own per-user memory/personalization, do not leave Hermes global memory and user-profile memory acting as a second, shared memory plane on the new server.

Preferred approach:
- define the assistant identity in server-level `SOUL.md`;
- store user-specific memory and personalization in the application data model, scoped to the frontend user/account;
- inject that user-scoped context into the downstream Hermes request from the backend;
- disable Hermes-side global memory/user-profile features on that host when they would otherwise create shared cross-user bleed.

Reason: for multi-user web products, the durable user context must belong to the app account model, not to one shared Hermes home.

## Concurrency is part of migration acceptance

When cutting over a chat/backend runtime to a new host, do not treat concurrency as a later optimization if the user explicitly expects simultaneous requests.

Minimum migration actions:
- set backend serving threads/workers intentionally rather than relying on defaults;
- set the app-level async/background processor concurrency explicitly;
- verify health/runtime after the concurrency knobs are applied;
- keep a note in the deploy env/example files so the target contour is reproducible.

This is especially important for chat-style products where one user talking to the agent should not serialize the entire app.

## False sense of progress from infra-only work

Installed packages, created users, and copied files can look like major progress. They are necessary but not sufficient. Keep a separate checklist for:
- host bootstrap;
- code readiness;
- data migration;
- live runtime verification.

## Hidden DB cutover risk

If the old embedded DB path is removed too early, you lose rollback and make diagnosis harder. Keep the old path available until the new runtime passes live checks.

## DuckDB WAL recovery before migration

When a remote cutover starts from a live DuckDB file, do not assume the file will always open cleanly after service interruptions or concurrent writes. A stale `.wal` can block both the app and the migration script with replay/conflict errors.

Preferred approach:
- stop the app services before the final export/cutover;
- make a timestamped backup of the `.duckdb` file before touching anything;
- check whether a sibling `.wal` file exists;
- if DuckDB fails specifically during WAL replay, preserve the original DB, move the stale WAL aside for forensic recovery, and retry against the preserved DB copy;
- only then run the one-shot migration into PostgreSQL.

Reason: the durable lesson is not "DuckDB is broken", but that remote cutovers need an explicit WAL check and backup step before migration.

## Clean-slate product cutover after successful import

Sometimes the user wants the new server to inherit structure and accounts but not early chats, sessions, jobs, or historical runs.

Preferred approach:
- first complete the real DB migration so the target schema and compatibility path are proven;
- then perform a deliberate cleanup in the target DB instead of skipping migration entirely;
- preserve users and curated reference data unless the user explicitly asks to wipe them too;
- truncate conversational/runtime tables intentionally and verify counts after cleanup.

Reason: this yields a clean product surface without losing the benefit of a verified DB cutover path.

## Sidecar underestimation

Telegram, auth, cron, parsing, or gateway services often contain the most fragile state: env, sessions, tokens, channel lists, or historical cursors. Inventory and migrate those deliberately.

## Sidecar service boundary for Telegram auth/parsing

If the user wants Telegram parsing on the new server but wants to avoid re-login disruption, do not silently collapse "move TG-API" into "move interactive login".

Preferred approach:
- separate three concerns explicitly: parsing/export API, login/session ownership, and web-app auth-link orchestration;
- decide whether session files stay on the old host or are intentionally copied to the new one;
- if secrets/env are loaded from a private env file, reference that file from the service unit instead of baking credentials into `ExecStart` or scattered shell wrappers;
- for the web backend, point to the TG sidecar through explicit env/config such as internal base URL, public auth-link base URL, and admin token/header contract;
- after startup, verify not only that the sidecar process is `active`, but also that the expected profile/config pair can serve a real export/auth request.

Reason: a running TG sidecar is only infrastructure success. Product success requires the profile/config/session contract to match the intended auth ownership model.

## Split-host contour discipline: do not promote the staging host into the target architecture

When a migration uses one host as a temporary verification or build surface, do not let that convenience mutate the declared target contour.

Preferred approach:
- restate the target ownership explicitly before calling anything "done": which host owns frontend, which owns backend/runtime, and which owns login/session state;
- if the agreed contour is split-host (for example old host keeps frontend/login/session and new host keeps backend/runtime), verify against that split even if a temporary frontend also runs on the new host;
- classify any off-contour runtime as a technical stand or staging surface, not as evidence that the production contour is ready;
- phrase status carefully: "code fixed", "verified on temporary host", and "verified in target contour" are different states and must not be blurred.

Reason: otherwise a convenient staging runtime creates a false sense of cutover progress and the user has to correct the architecture back to the agreed split.

## Remote backend reachability: fix the primary service bind, not a duplicate listener

When a frontend is repointed to a remote backend and starts returning `ECONNREFUSED`, do not jump straight to browser/CORS debugging. First prove whether the remote backend is externally reachable.

Preferred approach:
- test the remote backend directly from the frontend host with `curl`/TCP checks before changing frontend code;
- if SSH works but the backend port refuses connections, inspect the remote listener (`ss -ltnp`) and the primary service unit, not only application logs;
- if the service listens only on `127.0.0.1`, patch the main systemd unit or its drop-in/env to bind the intended external interface (commonly `0.0.0.0`), then restart that main unit;
- avoid spinning up a second "public" copy of the same backend on the same port unless you intentionally move it to another port, because the common outcome is `Address already in use` and more contour drift;
- after the bind fix, verify in three hops: loopback on the remote host, external URL from the frontend host, and finally the frontend's own `/api/...` proxy path.

Reason: the durable lesson is that many cutover failures are listener-scope problems on the remote host, not frontend bugs.

# Concrete checklist

1. Inventory current runtime, data, secrets, state, and ports.
2. Bootstrap target VPS and service user.
3. Establish passwordless SSH.
4. Prepare app code for dual runtime compatibility where needed.
5. Add migration utilities before cutover.
6. Validate code locally.
7. Create target DB/user/schema.
8. Transfer app data and state directories.
9. Transfer sidecar session/auth/config artifacts.
10. Start services under the intended runtime user.
11. Configure reverse proxy.
12. Run live endpoint and user-flow verification.
13. Only then report migration status.

# Output expectations for the user

Report in four sections:
- what is definitely done;
- what is partially prepared but not yet verified;
- blockers or risks;
- exact next step.

Keep facts separate from assumptions. Do not blur 'prepared' into 'running'.

# Support files

- `references/hermes-user-systemd-gateway.md` — concrete notes on the Hermes gateway user-systemd activation pitfall during remote VPS setup.
- `references/hermes-api-only-profile-memory-cutover.md` — API-only Hermes target shape, app-owned per-user memory split, and cutover verification notes for multi-user web products.
- `references/split-host-contour-and-remote-bind.md` — split-host verification discipline and the preferred fix path for remote backends that only listen on loopback.
