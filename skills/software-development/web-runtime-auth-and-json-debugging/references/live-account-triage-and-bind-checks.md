# Live account triage and bind checks

Use this when a split frontend/backend runtime shows login failures, random proxy breakage after restart, or account-specific auth complaints.

## 1. Re-verify the deployed contour
- Confirm the frontend host:port and the backend host:port that it proxies to.
- Read the live service/unit, not just the repo files.
- After any backend restart, verify the effective bind host. A service that starts on `127.0.0.1` instead of `0.0.0.0` can make the frontend show upstream-unavailable and look like a new UI/auth problem.

## 2. Check the backend from both sides
- Direct backend check: `.../api/service-info`
- Frontend same-origin check: `.../api/service-info`
- If direct backend works but frontend fails, suspect proxy target or external bind, not user auth.

## 3. For a single-user login complaint, inspect the live DB before changing UI code
Query the exact user by email/login and verify:
- row exists
- `is_active = 1`
- `deleted_at is null`
- role is what you expect

If all four are true, the likely causes narrow to:
- wrong password
- outdated password after admin/self update
- wrong login identifier
- malformed request payload

## 4. Use the runtime interpreter for DB probes
On remote runtimes, system Python may not have the same DB client packages as the running backend. Prefer the backend venv/interpreter so `psycopg` and related runtime dependencies match the service.

## 5. Report the cause class precisely
Do not say "login is broken" when the runtime facts show:
- account exists
- account is active
- account is not deleted
- backend returns `invalid_credentials`

In that case the right conclusion is: the auth path is alive, and the current failure is credential-specific, not a general frontend or account-state outage.
