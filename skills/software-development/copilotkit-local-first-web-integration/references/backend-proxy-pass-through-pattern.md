# Backend proxy pass-through pattern for local CopilotKit runtime

Use this when the frontend already points to `/api/copilotkit`, the local runtime sidecar is alive on another port (for example `8794`), but the main backend still does not expose a working CopilotKit route.

## Durable symptom pattern

- frontend dev server injects `VITE_COPILOTKIT_RUNTIME_URL=/api/copilotkit`;
- local runtime answers on its own port, for example `http://127.0.0.1:8794/copilotkit/info`;
- main backend health is green;
- but `http://127.0.0.1:<backend-port>/api/copilotkit/info` returns `404`.

This usually means configuration exists only in launcher env vars, but `app.py` does not actually proxy the route.

## Preferred fix

Keep the local-first contour canonical:

- frontend -> `/api/copilotkit`
- backend -> proxy/pass-through
- sidecar runtime -> internal implementation detail

Do not switch the frontend default to a direct sidecar URL just because the proxy layer is missing.

## Minimal backend shape

1. Add backend env/config such as `HERMES_WEB_COPILOTKIT_RUNTIME_BASE_URL`.
2. Add a small proxy helper that:
   - forwards `GET` and `POST`;
   - preserves `Content-Type`, `Accept`, and `Authorization` headers when present;
   - forwards raw request body for `POST`/`PATCH`/`PUT`;
   - returns upstream status and body as-is;
   - converts upstream connectivity failure into a clear `502` class error.
3. Expose backend-owned routes:
   - `/api/copilotkit`
   - `/api/copilotkit/<path>`
4. Restart the backend via the project launcher, not a random ad-hoc python command.

## Verification

After the patch and restart, confirm all of these separately:

1. `GET /api/health` -> `200`
2. `GET /api/copilotkit/info` -> `200`
3. existing product-specific chat flow still works after the proxy addition
4. frontend build still passes

Important: do not treat `copilotkit/info` success as enough. Re-run at least one real app scenario that depends on structured assistant metadata or existing chat logic, to make sure the new proxy route did not break the main backend path.

## Practical lesson

A very common half-finished state is:
- `run_backend_service.sh` exports the CopilotKit runtime base URL;
- sidecar runtime is alive;
- frontend is correctly configured for `/api/copilotkit`;
- but backend source never consumes that env value.

When you see this pattern, fix the backend-owned canonical route instead of moving more logic into the frontend.
