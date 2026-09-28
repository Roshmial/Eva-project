# Prod interaction audit and Postgres LIKE gotchas

## When this reference applies

Use for live Hermes-style prod audits where the user asks to inspect recent user interactions for errors, regressions, or incorrect agent behaviour across a split frontend/backend contour.

Typical contour:
- real frontend entrypoint on one host/port
- canonical backend/API on another host/port
- browser/UI access may be available only for the frontend shell, while the decisive evidence lives in backend logs and DB state

## Fast audit pattern

### 1. Confirm the contour first
- Verify the real frontend entrypoint responds (for example `95:8803`).
- Verify the canonical backend health/API responds (for example `178:8791`).
- Do not treat frontend availability as proof that post-login user flows work.

### 2. Pull backend evidence in this order
1. `journalctl` for the live backend service
2. recent `app.chat_tasks`
3. recent `app.messages` joined with `app.threads` and `app.users`
4. only then narrow into browser/UI reproduction if still needed

This gives a reliable picture of:
- hard runtime exceptions
- timeouts / stuck tasks
- which users were affected
- whether the assistant produced the wrong artifact or wrong route outcome

### 3. What to look for in `app.chat_tasks`
Minimum fields:
- `id`
- `thread_id`
- `user_id`
- `status`
- `created_at`
- `started_at`
- `finished_at`
- `last_error`

Useful audit questions:
- Which users have the most recent `status='error'` tasks?
- Are failures clustered in one thread?
- Is the error class repeated (`timed out`, routing failure, etc.)?
- Did the task complete only after a long queue delay?

### 4. What to look for in `app.messages`
Join messages to threads and users. Inspect:
- user request text
- assistant response text
- `message_kind`
- `downstream`
- `source`
- attachment metadata
- `generated_from_request`
- `processing_status`

This reveals user-visible defects that health checks miss, for example:
- repeated `clarification_request` although the request was already sufficiently specified
- `processing_status=error` after a seemingly valid follow-up
- generated file format mismatch (`pptx` requested, `docx` delivered)
- generic fallback/error text where a route-specific response was expected

### 5. Classification pattern for findings
Separate findings into:
- runtime failure: exception / 500 / timeout
- routing defect: wrong branch selected, unnecessary clarification, generic chat instead of specialized route
- output contract defect: user asked for one artifact/format, another was delivered
- UX shell healthy but post-login/business flow broken

## Important Postgres / psycopg gotcha

If the backend uses a query translator that converts `?` placeholders to psycopg `%s`, do **not** embed raw SQL patterns containing `%...%` directly inside the query string unless they are escaped for psycopg or parameterized.

Danger pattern:
- `LIKE '%"message_kind":"file_response"%'`
- `LIKE '%"source":"job_run"%'`

Why it breaks:
- psycopg parses `%` as placeholder syntax
- literal JSON-like `LIKE '%"..."%'` fragments can trigger errors such as:
  - `only '%s', '%b', '%t' are allowed as placeholders, got '%"'`

Safer patterns:
- pass the pattern as a SQL parameter
- or escape literal percent signs as `%%` when a raw string is unavoidable
- or better, stop string-matching JSON blobs and use structured JSON/JSONB access where the schema/runtime allows it

## Split-contour reporting rule

If frontend logs are unavailable on the frontend host, do not overstate frontend conclusions.
Report precisely:
- frontend shell / entrypoint status is confirmed
- backend/API defects are confirmed from logs and DB
- user-visible post-login breakage is strongly implied or proven by backend evidence
- direct frontend-host logs were not inspected if you lacked access
