# Hermes web MVP session pattern

Use this reference when a user asks for a separate-server design plus a concrete web-facing artifact.

## Durable takeaways

- For multi-user agent products, backend must own user identity and thread mapping.
- Hermes should run as an internal agent runtime, not as the main user/account registry.
- PostgreSQL is the right default for app-layer OLTP data; DuckDB stays as analytics hub.
- Public edge should expose only reverse proxy; Hermes API Server and databases stay internal.
- A useful delivery package is: architecture write-up + visual diagram + interactive MVP frontend.

## Example deliverables produced in session

Artifacts created under `/home/hermes/workspace/hermes-web-mvp/`:
- `ARCHITECTURE.md`
- `architecture-diagram.html`
- `frontend-mvp/index.html`
- `README.md`

## MVP UI slices that proved useful

- login screen with role switch;
- thread list;
- chat panel with streaming-like response state;
- profile/personalization screen;
- feedback screen;
- admin health screen;
- runtime sidebar showing user/thread/profile mapping.

## Practical implementation note

If possible, also launch a minimal local static test environment for the MVP and verify that the page is reachable over HTTP, even if a full backend is not yet implemented.
