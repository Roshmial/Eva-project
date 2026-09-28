# Frontend proxy backend base configuration pattern

For Hermes Web MVP React, the frontend production server (`serve_frontend_prod.mjs`) proxies all `/api/*` requests to a backend base URL controlled by the `HERMES_WEB_FRONTEND_BACKEND_BASE` environment variable.

## How it works

The production frontend (`scripts/serve_frontend_prod.mjs`) reads:
```javascript
const backendBase = (process.env.HERMES_WEB_FRONTEND_BACKEND_BASE || `http://${process.env.HERMES_WEB_BACKEND_HOST || '127.0.0.1'}:${process.env.HERMES_WEB_BACKEND_PORT || 8791}`).replace(/\/$/, '');
```

All requests to `/api/*` are forwarded to `${backendBase}${req.url}`.

## Common failure

If `HERMES_WEB_FRONTEND_BACKEND_BASE` is not set and the frontend runs on a different host than the backend, the proxy defaults to `http://127.0.0.1:8791` (local backend), causing `frontend_proxy_upstream_unavailable` because there's no backend on the frontend host.

## Fix

Set the environment variable in the frontend systemd unit:

```ini
[Service]
Environment=HERMES_WEB_FRONTEND_BACKEND_BASE=http://178.104.207.89:8791
```

Then reload and restart:
```bash
systemctl --user daemon-reload
systemctl --user restart hermes-web-frontend-8803.service
```

## Verification

After restart, confirm via the frontend port:
```bash
curl http://95.182.85.233:8803/api/service-info
# Should return: {"mode":"hermes-api","service":"Hermes Web","status":"ok"}
```

The response should come through the frontend proxy (not direct to backend), proving the `/api/*` path is correctly wired.

## Note on runtime env layers

The `run_frontend_react_service.sh` wrapper sources `scripts/runtime_env.sh`, which in turn sources `~/.hermes/.env`. This shell layer can silently override systemd `Environment` lines. Always verify the effective environment by checking the live process (`/proc/$PID/environ`) if the proxy target still doesn't match expectations after a restart.