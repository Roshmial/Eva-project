# Prod runtime env-preserving restart for Hermes Web backend

Use this when backend code is patched directly on a live local-first/prod contour and you must restart the process without silently changing runtime mode or routing.

## Why this matters
A naked restart of `waitress-serve` can come back in the wrong environment (for example `mock-hermes` instead of `hermes-api`) even though the process is up and `/api/health` still returns `200`.

## Safe sequence
1. Verify the live process before touching it:
   - command line (`pgrep -af 'waitress-serve|8791|app:app'`)
   - cwd / venv
   - effective env if needed (`/proc/<pid>/environ`)
2. Prefer the project’s canonical env bootstrap, not a bare process launch.
   - In this session the safe path was `source scripts/runtime_env.sh` from project root before launching backend.
3. Only then restart the backend process.
4. After restart, verify not only liveness but the semantic runtime state via `/api/health`.
   - confirm `mode=hermes-api`
   - confirm expected scheduler/chat-processor shape
   - confirm counts look like the prod contour, not a fallback/mock contour
5. If you changed files on prod, run targeted backend tests on prod too, not only locally.

## Concrete prod pattern used here
- Project root: `/home/hermes/workspace/hermes-web-mvp-react-8793`
- Backend path: `services/backend`
- Restart pattern:
  - `cd /home/hermes/workspace/hermes-web-mvp-react-8793`
  - `export HERMES_WEB_BIND_HOST=0.0.0.0`
  - `source scripts/runtime_env.sh`
  - `cd services/backend`
  - `nohup ./.venv/bin/python ./.venv/bin/waitress-serve --threads=8 --listen=${HERMES_WEB_BACKEND_HOST}:${HERMES_WEB_BACKEND_PORT} app:app ... &`
- Post-check: `curl http://127.0.0.1:8791/api/health`

## Pitfall to encode
Do not report prod deployment as complete after copying files or after a process restart alone. Completion requires:
- code copied
- backend compiled
- targeted tests passed on the target contour
- runtime restarted through canonical env bootstrap
- `/api/health` verified in the correct mode
