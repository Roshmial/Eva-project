# Backend-owned canonical CopilotKit route

Use this pattern when a local-first React app already has a working sidecar/runtime on a separate port, but the product should expose a single stable CopilotKit entrypoint.

## Preferred final contour

- frontend UI uses `runtimeUrl=/api/copilotkit`
- backend owns `/api/copilotkit`
- backend forwards to local runtime/adapter
- runtime port remains internal and directly callable only for diagnostics

## Why this is better than keeping frontend `/copilotkit -> runtime`

- one canonical route for the product;
- fewer contradictions between UI behavior and backend health/status;
- easier auth, logging, timeout, and future context injection in backend;
- less drift between launcher scripts, Vite proxy, and runtime wiring.

## Migration pattern

1. Keep direct frontend-to-runtime proxy only while backend route is still preview-only.
2. Add backend proxy/passthrough for `/api/copilotkit`.
3. Switch frontend default `runtimeUrl` to `/api/copilotkit`.
4. Remove frontend default `/copilotkit` proxy as the primary path.
5. Align backend default port/envs with the actually used deployment port.
6. Recheck CORS, smoke scripts, and runtime health URLs.

## Audit checklist for suspicious extra frontend ports

If you notice an extra port such as `8824`:
- inspect the listener PID;
- inspect command line;
- inspect process working directory;
- confirm whether it is just another `vite` instance of the same repo.

Do not treat the extra port as a separate deployed version until those checks are done.

## Minimal verification after canonicalization

- `GET /api/service-info` returns 200 from the intended backend
- `GET /api/copilotkit/info` returns runtime metadata through backend
- frontend build still passes
- only the intended frontend port remains active
- direct runtime port is optional for diagnostics, not required by frontend defaults
