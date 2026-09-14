# CopilotKit local-first verification notes: canonical backend contour and thread-aware sidebar

Use these notes when a CopilotKit preview looks alive but the first real sidebar message still does not behave like a finished integration.

## Durable findings

1. Canonical local-first contour should be explicit:
- frontend UI -> `/api/copilotkit`
- backend -> sidecar/runtime
- runtime port stays diagnostic/internal

2. `info` success is necessary but not sufficient.
A live sidebar can do all of this in sequence:
- runtime metadata/discovery POSTs
- `GET /threads?agentId=default`
- optional `POST /threads/subscribe`
- message/run POSTs

3. If only discovery works, the UI can still look half-alive:
- sidebar opens
- welcome text renders
- runtime metadata returns 200
- first real user message stalls because thread endpoints are missing or unsupported

4. In a temporary compatibility contour, small backend fallbacks for thread endpoints can be acceptable if the goal is to keep the sidebar from breaking during incremental integration.
Typical minimal fallback shapes:
- `GET /threads` -> `{ "threads": [], "nextCursor": null, "joinCode": null }`
- `POST /threads/subscribe` -> `{ "joinToken": "..." }`
- no-op archive/delete/mutation endpoints -> `204`

Do not present that as full thread persistence. It is a shim.

5. If several backend instances share one DuckDB file, CopilotKit debugging becomes misleading.
Typical false signals:
- lock conflicts during login/setup
- one backend answers app health, another holds DB lock, a third serves an outdated route
- extra frontend port looks like another deployment but is only a duplicate Vite process

## Audit checklist before concluding anything

- Verify active listeners for all expected ports.
- Map each port to PID, command line, and working directory.
- Confirm whether extra frontend/backend ports are the same repo launched multiple times.
- Remove duplicate processes before route/runtme conclusions.
- Re-run runtime checks only after the contour is clean.
