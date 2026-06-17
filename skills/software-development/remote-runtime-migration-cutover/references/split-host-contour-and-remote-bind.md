# Split-host contour and remote bind checks

Use this reference when a web stack is intentionally split across two hosts and the frontend must talk to a backend on another server.

## 1. Freeze the ownership map first

Write the contour in one short block before changing services:
- old host: frontend, login flow, session ownership;
- new host: backend/runtime;
- cross-host calls: exactly which URLs and auth/session dependencies cross the boundary.

Do not treat a temporary frontend raised on the new host for debugging as proof that the target contour is ready.

## 2. Triage `ECONNREFUSED` in the right order

From the frontend host:
1. `curl http://REMOTE_HOST:PORT/api/service-info`
2. if that fails but SSH works, inspect the remote host:
   - `systemctl --user status <service>`
   - `ss -ltnp | grep <port>`
   - `curl http://127.0.0.1:<port>/api/service-info`
3. compare local loopback success with external failure.

Interpretation:
- loopback works + external fails = listener/bind scope problem or firewall;
- both fail = service/runtime problem;
- external works but frontend `/api/...` fails = proxy or frontend-target problem.

## 3. Preferred fix pattern

If the remote backend listens only on `127.0.0.1`, patch the primary systemd user unit via drop-in:

```ini
[Service]
Environment=HERMES_WEB_BACKEND_HOST=0.0.0.0
```

Then:
- `systemctl --user daemon-reload`
- `systemctl --user restart <main-backend-service>`
- verify `ss -ltnp` shows `0.0.0.0:<port>` or the intended external interface.

Do not keep a duplicate "public" unit on the same port as the real service. If you tried that and saw `Address already in use`, remove or disable the duplicate and fix the real service instead.

## 4. Final proof chain

Call the contour healthy only after all three pass:
- remote host loopback: `curl http://127.0.0.1:<port>/api/service-info`
- external reachability from the frontend host: `curl http://REMOTE_HOST:<port>/api/service-info`
- frontend-origin proxy path: `curl http://FRONTEND_HOST:<front_port>/api/service-info`

This keeps "backend is up" separate from "frontend is really attached to that backend".
