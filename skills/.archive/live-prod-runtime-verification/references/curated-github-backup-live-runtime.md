# Curated GitHub backup for a live Hermes Web contour

When the user wants a backup of a live runtime contour to GitHub, do not back up the whole home directory or the whole runtime state. Build a curated repository from the live contour.

## What to include

For a Hermes Web runtime like `hermes-web-mvp-react-8793`, include:
- project code for backend/frontend/runtime components
- deploy/package files
- launcher scripts such as `run_backend_service.sh`, `run_frontend_react_service.sh`, `run_copilotkit_runtime_service.sh`
- root manifests like `package.json`, `package-lock.json`, `vite.config.js`, `docker-compose.yml`
- operational docs and runbooks
- live `systemd --user` unit files actually used by the contour
- important service drop-ins that carry bind host, timeout, CORS, or similar runtime-critical overrides

## What to exclude

Exclude runtime and sensitive state by default:
- `node_modules/`
- `.venv/`
- `dist/`
- backend data directories and DB files
- `.env*`
- logs, caches, `__pycache__`, test artifacts
- session dumps, screenshots, temp outputs

## Verification sequence

1. Verify the live contour first on the named host.
2. Read the actual unit files from `~/.config/systemd/user/`.
3. Identify the real project root and launcher scripts from those units.
4. Build the curated backup repo from the live source of truth, not from memory and not from an old local copy.
5. Make an initial local commit before attempting remote push.
6. If GitHub auth is not ready on that host, still finish the local backup repo and the scheduled refresh; then ask for the single SSH-key step.

## Weekly refresh pattern

A good low-friction pattern for remote hosts:
- keep a standalone Python backup script on the host
- let it rebuild the curated tree, commit only on changes, and push if `origin` is configured
- schedule it weekly at `06:00 UTC` when the user wants `09:00 MSK`
- prefer silent local execution over chat delivery for recurring backups

## SSH auth pitfall

A remote server may not yet trust GitHub even if another machine already does. Typical durable path:
- generate a dedicated SSH key on that host if none exists
- add `github.com` to `known_hosts`
- provide the public key to the user
- only then finish the first push from that host

## Why this matters

This preserves the actual deploy logic and runtime contour without leaking operational state or secrets, and it keeps weekly refreshes maintainable.