# Restart-safe local-first web contour for Hermes Web / CopilotKit / TG-API

Use this when a local-first web stack looks healthy in the current shell session but must also survive a full server restart or a Hermes upgrade.

## Scope
- Hermes gateway managed separately
- Web backend, web frontend, CopilotKit runtime, and adjacent local services like TG-API
- Single-host local-first deployments on Linux

## Durable lessons from this session
1. `health=200` is not enough. A contour can be green only because manual shell processes are still alive.
2. Canonical runtime ports must be aligned across code defaults, launcher scripts, smoke scripts, docs, and service units. If old defaults remain, the next clean boot drifts back into legacy paths.
3. For Node-based services under `systemd --user`, explicitly export `PATH=$HOME/.hermes/node/bin:$PATH` in launchers when Hermes-managed Node tooling lives there.
4. A sidecar service like TG-API should not depend on the parent shell's Python environment. Give it its own launcher, `.venv`, `requirements.txt`, and env source.
5. Remove hardcoded secret fallbacks from repo code before making restart-safe units. Put secrets in a private env file outside the repo and bind local services to `127.0.0.1` unless external access is intentional.
6. Simulated restart is mandatory: stop/restart via `systemctl --user` and re-check all health endpoints.

## Practical checklist
### 1) Canonicalize the contour
Lock one operational contour, for example:
- frontend: `127.0.0.1:8793`
- backend: `127.0.0.1:8791`
- CopilotKit runtime: `127.0.0.1:8794`
- TG-API: `127.0.0.1:8001`

Then update all of the following if they still point to legacy values:
- backend default port / CORS defaults
- frontend default backend base URL and default frontend port
- run scripts / launcher scripts
- smoke and acceptance scripts
- docker-compose and deployment docs
- runtime runbooks

### 2) Make launchers systemd-safe
For Node-based launchers:
- export `PATH=$HOME/.hermes/node/bin:$PATH`

For Python sidecars:
- create `requirements.txt`
- create a dedicated launcher that:
  - creates `.venv` if missing
  - installs or refreshes dependencies when requirements change
  - loads a private env file
  - `exec`s the real service process

### 3) Move secrets out of code
- remove fallback API IDs / hashes / tokens from source code
- store them in a private env file such as `~/.hermes/tg-api.env`
- restrict permissions (for example `chmod 600`)

### 4) Add `systemd --user` units
Create one unit per long-lived component:
- backend
- frontend
- CopilotKit runtime
- TG-API or other local sidecars

Prefer `Restart=always` and loopback binds for local-only components.

### 5) Verify by simulated restart
Do not stop at file edits. Restart through `systemctl --user` and verify:
- backend health
- CopilotKit info / health
- frontend root URL
- sidecar export endpoint
- `systemctl --user is-enabled ...`
- `systemctl --user list-units --type=service`

## Pitfalls
- Do not declare restart readiness from live shell processes alone.
- Do not leave operational defaults on legacy ports even if the active process currently overrides them.
- Do not keep secrets in repo code just because the service is local-only.
- Do not bind helper services to `0.0.0.0` unless there is a real external caller.
- Do not assume `node`, `npm`, or Python packages are visible inside user-systemd just because they work in the interactive shell.

## Example corrective actions from this session
- Added user-systemd units for backend, frontend, CopilotKit runtime, and TG-API.
- Added explicit Hermes Node PATH in launchers so CopilotKit/frontend survive systemd restart.
- Moved Telegram API credentials out of `login.py` into a private env file.
- Added a self-sufficient TG-API launcher with `.venv` bootstrapping and dependency installation.
- Re-verified the whole contour with live HTTP checks after `systemctl --user restart ...`.

## When to cite this reference
Use this reference when the user asks for:
- readiness for reboot
- readiness for Hermes upgrade
- removal of legacy runtime links
- local service hardening without introducing extra SaaS or orchestration
