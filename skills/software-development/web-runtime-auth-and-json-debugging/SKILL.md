---
name: web-runtime-auth-and-json-debugging
description: Diagnose and fix web runtimes where authorization appears to reset unexpectedly, session restore is brittle, or API failures surface as HTML/non-JSON in the UI.
---

# Purpose

Use this skill when a local-first or self-hosted web runtime shows one or more of these symptoms:
- users appear to be logged out "at random"
- session restore fails after reload
- UI shows raw HTML, `Unexpected token '<'`, or "service returned non-JSON"
- auth endpoints behave differently from other API routes
- backend health looks fine, but live login/send flows are still broken

This skill is for end-to-end runtime debugging across frontend, backend, and live process environment.

## Triggers

Use when:
1. login works sometimes but reload/restore drops the session
2. a frontend clears stored token during bootstrap
3. same-origin `/api/...` requests return HTML instead of JSON
4. backend uses multiple possible data sources and the live process may not be reading the one you are editing
5. you need to prove the fix with real runtime calls, not code inspection alone

## Core principle

Treat this as a contract debugging task, not just an auth task.

You must verify all three layers:
- frontend token lifecycle
- backend auth/session semantics
- live runtime wiring: process env, DB/DSN, same-origin API path, real HTTP responses

## Workflow

1. Confirm the live runtime you are actually debugging.
- Inspect running process `cwd`, `cmdline`, and env.
- Check frontend host/port, backend host/port, and any runtime DSN/DB variables.
- Do not assume the edited repo and the live process use the same tree or the same database.
- If the backend was restarted or re-deployed, verify the effective listen host from the live service/unit env. A backend that comes up on `127.0.0.1` instead of `0.0.0.0` can re-create frontend proxy failures and look like a fresh auth/UI regression.

2. Prove the response contract first.
- Check direct backend `service-info`.
- Check same-origin frontend `/api/service-info`.
- Check a guaranteed-missing route like `/api/does-not-exist`.
- Required outcome: API routes must return JSON even on errors.

3. Before blaming the frontend, verify the user record in the live database when the problem is account-specific.
- Query the production DB for the exact email/login.
- Confirm the account exists and inspect `is_active` / `deleted_at` / role fields.
- If the user exists, is active, and is not deleted, then the likely causes narrow to credentials or request formatting rather than UI visibility or account state.
- Use the backend runtime's own venv/interpreter for DB probes if that environment carries `psycopg` and the service DSN; do not rely on system Python.

3. Inspect frontend session handling.
- Find where token is stored and cleared.
- Verify whether token is removed only for explicit auth failures (`invalid_token`, `auth_required`) or for any bootstrap error.
- If token is cleared on generic init/data-loading failures, fix that first.

4. Harden bootstrap/restore.
- Route public boot calls such as `service-info` and `setup-status` through the same JSON-safe request path used for authenticated API calls.
- Make non-critical bootstrap reads tolerant with partial-failure handling where appropriate.
- Do not let optional data (for example files/jobs meta) invalidate an otherwise good session.

5. Check backend error handling.
- If framework-level 404/405/500 pages can bypass JSON handlers, add explicit HTTP-exception handling.
- A generic catch-all exception handler is not always enough; verify with a real 404 request after deploy.

6. Verify live auth with real requests.
- `login` -> expect 200 JSON with token
- `auth/session` -> expect 200 JSON
- create thread/resource -> expect success JSON
- send message/action -> expect success JSON
- invalid token -> expect JSON error, not HTML
- missing route -> expect JSON error, not HTML

7. Only after live verification, report success.

## Pitfalls

- False logout: the frontend may clear token because bootstrap failed for unrelated reasons. This looks like auth expiry but is not.
- Split data source: password or test-user changes in DuckDB/local files do nothing if the live backend is pointed at Postgres via DSN.
- 404 trap: Flask/framework default HTML pages can survive unless `HTTPException` is handled explicitly.
- Shell-quoting noise can fake API problems during SSH smoke tests. If curl-in-shell becomes fragile, switch to a short Python HTTP probe on the remote host.
- Health checks alone are insufficient. A green `service-info` does not prove login/reload/send works.

## User-specific delivery rule

For this user, prefer finishing the live runtime verification end-to-end instead of stopping at "fix applied". If a live smoke requires a real admin/test account and the user authorizes using an existing admin, use it rather than asking for another path.

## Reference files

- `references/runtime-auth-json-contract.md` — condensed checklist and lessons from a live Hermes Web auth/reset + HTML-to-JSON debugging pass.
- `references/live-account-triage-and-bind-checks.md` — compact checklist for split-host runtimes: verify external bind after restart and separate account-state problems from bad credentials.

## Completion standard

Do not stop at code patching. The task is complete only when live runtime evidence shows:
- stable auth/session behavior
- no raw HTML/non-JSON surfacing from API routes
- successful real action after login
