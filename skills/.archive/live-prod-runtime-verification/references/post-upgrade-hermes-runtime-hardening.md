# Post-upgrade Hermes runtime hardening on a live contour

Use this reference after upgrading Hermes itself on a live Hermes Web / gateway contour.

## What to verify after the version bump

Do not stop at `hermes --version`.
Verify four layers separately:
1. Hermes runtime version really changed.
2. `~/.hermes/config.yaml` was migrated and still matches the intended operating mode.
3. Dependent live services (gateway, backend, copilotkit/runtime sidecars) are still under the intended supervisor and not replaced by orphaned processes.
4. Real user-path probes still work after restart.

## Concrete failure classes seen in practice

### 1) Orphaned backend process makes systemd look broken

Symptom:
- backend health still answers on `8791`;
- but `systemctl --user status hermes-web-backend-8791.service` is failed/inactive;
- journal shows repeated `Address already in use`.

Interpretation:
- an old `waitress` process survived outside the intended unit;
- the real service cannot bind, so prod is serving from a stray process.

Fix pattern:
- identify listener PID on the port;
- kill the stray process;
- `systemctl --user reset-failed ...`;
- start backend and dependent sidecars again;
- verify live listeners and unit status after restart.

### 2) Smoke probes fail with `401` because credentials/probe flow are stale, not because auth is down

Symptom:
- `/api/auth/login` returns `401 invalid_credentials`;
- older probe scripts still assume obsolete demo credentials or legacy token acquisition.

Interpretation:
- auth endpoint is alive;
- acceptance fixtures drifted.

Fix pattern:
- inspect real users in the live DB/runtime env;
- use an existing smoke user or reset a known temporary password in the real runtime DB;
- update probe scripts to use the current `/api/auth/login` flow instead of stale token hacks.

Important nuance:
- if you reset passwords or inspect users off-process, source the same runtime env as the running backend first. Otherwise you can modify the wrong DB and create a fake contradiction where login still fails.

### 3) Runtime-env mismatch causes false verification failures

Symptom:
- direct imported backend probes say a password/session/token is valid;
- live HTTP still returns `401`.

Interpretation:
- your probe did not run under the same `runtime_env.sh` / DSN / secrets as the live service.

Fix pattern:
- source the service runtime env;
- use the same `.venv` as the live service;
- only then inspect/update users, sessions, or app DB state.

### 4) Gateway is up but user access is effectively closed after restart

Symptom:
- gateway starts successfully;
- logs warn that no allowlists are configured and unauthorized users will be denied.

Interpretation:
- service health is green but the real messaging path is not actually usable.

Fix pattern:
- inspect the gateway env for platform allowlists;
- for Telegram-backed contours, set `TELEGRAM_ALLOWED_USERS` (or the contour-appropriate allowlist) before closing the upgrade.

## Acceptance baseline after upgrade

A post-upgrade hardening pass should prove at least:
- login works through the live HTTP path;
- `/api/me` and `/api/bootstrap` work;
- a plain chat request completes;
- one action route completes (for example job creation);
- one artifact-producing or collection route completes with a real result;
- gateway/user allowlist warnings are gone if the contour expects restricted access.
