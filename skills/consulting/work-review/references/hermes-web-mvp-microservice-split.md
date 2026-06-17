# Hermes web MVP: microservice split for painless migration

Use this when building a shared Hermes-backed web MVP that may later move off the current Hermes host.

Recommended portability boundary:
- frontend service
- backend API service
- Hermes API Server as downstream dependency of backend, not of frontend

Key rules:
1. Frontend must be static and replaceable.
   - Serve HTML/JS as a separate service.
   - Keep backend base URL in external config (`config.js`, env-injected JSON, or reverse proxy), not hardcoded to the current host layout.
2. Backend must not serve frontend assets if migration flexibility matters.
   - Otherwise the UI becomes coupled to backend deploy paths and host decisions.
3. Backend owns user/session/thread/profile/feedback state.
   - This state should move with the backend and its volume, independently of Hermes.
4. For MVP, SQLite is acceptable if it lives in the backend's own data directory / volume.
   - Later swap to Postgres without changing the frontend contract.
5. Enable CORS explicitly when frontend and backend are split by port or host.
6. Validate portability with a real cross-origin check, not only same-origin local serving.

Minimal practical shape:
- frontend: static host, no server-side dependency on Hermes machine
- backend: Flask/FastAPI service, env-configured host/port/data path/CORS
- integration seam: backend adapter that can switch `mock` -> `real Hermes API Server`

Migration benefit:
- frontend can move to nginx/static hosting without moving Hermes
- backend can move with its DB volume without moving frontend
- Hermes can remain on the old box temporarily while backend repoints downstream
