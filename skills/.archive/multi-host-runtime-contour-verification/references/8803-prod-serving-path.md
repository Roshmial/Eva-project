# 8803 production serving path for Hermes Web split runtime

When a public frontend host is still running `react:dev` / Vite HMR, treat that as a rollout blocker even if backend acceptance is green.

## Durable pattern

1. Keep the split contour stable:
   - public frontend host continues to serve the user-facing port
   - backend host remains the `/api` upstream
2. Replace the public dev server with a small production-serving path:
   - serve `dist/frontend-react` as static assets
   - proxy `/api` to the backend base
   - use SPA fallback to `index.html`
3. Make frontend startup mode explicit in the launcher:
   - `HERMES_WEB_FRONTEND_MODE=dev` -> Vite dev server
   - `HERMES_WEB_FRONTEND_MODE=prod` -> static/proxy server
4. Switch the user systemd unit to production mode and restart it.
5. Verify the contour end-to-end, not just with a healthcheck.

## Minimum verification set

- `npm run react:build` succeeds before restart.
- systemd unit is `active (running)` after restart.
- main process is the production server, not Vite.
- listener on the public port is present.
- both local and public `GET /` return production HTML with static asset bundle references.
- both local and public `GET /api/service-info` return `status=ok`.
- acceptance through the public contour exercises auth + read + write, for example:
  - `POST /api/auth/login`
  - `GET /api/me`
  - `GET /api/jobs/meta`
  - `POST /api/threads`
  - `GET /api/threads`
- temporary acceptance users are cleaned up from prod DB after the check.

## Pitfalls

- A plain `200 OK` on `/` is not enough; require `/api` proxy and at least one write path.
- A public contour is not production-ready if the unit still runs `react:dev`, even when the backend is already good.
- When switching a launcher to a production script, re-check path resolution from inside the systemd unit; relative paths that work in manual runs can fail under the unit.

## Session-proven implementation shape

A simple Node server is sufficient when you need a low-moving-parts fix:
- static serving from `dist/frontend-react`
- `/api` fetch proxy to backend
- SPA fallback routing

This is a good default when the user prefers local-first / current-stack reuse over introducing nginx, extra containers, or a separate frontend platform layer.
