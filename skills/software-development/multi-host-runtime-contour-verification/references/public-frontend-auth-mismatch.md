# Public frontend auth mismatch on split contours

Use this pattern when the public web surface returns `401 invalid_credentials`, while the same credentials succeed on a local or direct backend URL.

## What happened in this session

Observed contour:
- public frontend: `95.182.85.233:8803`
- public frontend proxy target: `http://178.104.207.89:8791`
- local backend under investigation earlier: `127.0.0.1:8791`

The misleading symptom was:
- local/direct login succeeded on one backend contour;
- login through the public frontend proxy failed;
- local DB/user changes had no effect on the public surface.

Root cause:
- the public frontend did **not** proxy to the local backend being modified;
- the real backend-owner used a different live DB (`postgresql:///hermes_web` on the remote backend host);
- smoke-user creation had to happen on the backend-owner, not in a nearby local repo DB / DuckDB / SQLite file.

## Fast verification sequence

1. Read the public frontend unit or launcher.
   - Confirm the effective proxy target (`HERMES_WEB_FRONTEND_BACKEND_BASE` or equivalent).
   - On Hermes Web prod frontend this may be visible both in `systemctl --user cat ...` and in the startup log line like:
     - `Hermes Web prod frontend listening on http://0.0.0.0:8803 -> http://178.104.207.89:8791`

2. Compare auth on both surfaces.
   - Direct backend login: `http://<backend-owner>:8791/api/auth/login`
   - Public proxy login: `http://<public-frontend>:8803/api/auth/login`
   - If these differ, do not reset passwords blindly on the local contour.

3. Inspect the backend-owner live process env.
   - Read `/proc/<pid>/environ` or the wrapper/unit env.
   - Confirm the actual DB owner (`HERMES_WEB_BACKEND_DSN`, `HERMES_WEB_BACKEND_DB_PATH`, etc.).

4. Create or reset the smoke-user on the backend-owner DB only.
   - For Postgres-backed Hermes Web, use the backend service venv and connect to the live DSN.
   - Re-test direct backend login first, then public proxy login.

5. Only after auth is proven on the public contour, run UI acceptance.
   - Create a fresh test thread/message on the same public contour.
   - Verify both API export/download and browser-driven UI download.

## Why this matters

Without this sequence, it is easy to:
- keep fixing the wrong DB;
- conclude that the frontend auth is broken when the real problem is contour ownership;
- mark UI acceptance blocked even though the product path is fine once the smoke-user is created on the correct backend-owner.
