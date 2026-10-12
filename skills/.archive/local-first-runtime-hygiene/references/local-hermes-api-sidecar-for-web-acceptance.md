# Local Hermes API sidecar for Web acceptance

Use this when Hermes Web runs in `hermes-api` mode locally, but the main Hermes gateway process cannot be restarted because it owns the current operator session.

## Symptoms
- local backend `8791` is up;
- `service-info` may still return `mode=hermes-api`;
- `127.0.0.1:8642` is closed;
- chat tasks fail with API-path errors or equivalent missing-key behaviour;
- acceptance starts looking like a sprint regression even though the blocker is contour wiring.

## Safe recovery pattern
1. Keep the current operator gateway session untouched.
2. Create an isolated temporary Hermes home, for example by copying:
   - `config.yaml`
   - `.env`
   - auth/session state needed for model access
3. Launch a separate Hermes gateway/API-server process against that temporary home with explicit env:
   - `HERMES_HOME=<temp-home>`
   - `API_SERVER_ENABLED=true`
   - `API_SERVER_KEY=<temp-key>`
   - `API_SERVER_PORT=8642`
   - `API_SERVER_HOST=127.0.0.1`
4. Verify:
   - `127.0.0.1:8642` accepts TCP;
   - `/v1/models` returns 200 with the bearer key;
   - `/health` returns 200.
5. Restart only the local Web backend with:
   - `HERMES_WEB_HERMES_API_BASE_URL=http://127.0.0.1:8642/v1`
   - `HERMES_WEB_HERMES_API_KEY=<same temp-key>`
6. Run one real chat round-trip before resuming deeper acceptance.

## Why this matters
This isolates contour repair from product debugging:
- no need to weaken backend routing;
- no need to kill the main gateway session;
- no false claim that the sprint code itself is broken when only the local dependency chain is incomplete.
