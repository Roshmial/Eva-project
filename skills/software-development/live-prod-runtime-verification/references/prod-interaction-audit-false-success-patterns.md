# Prod interaction audit: false-success and side-effect verification patterns

Use this note when a user asks to inspect recent production interactions for errors, strange behavior, or "what actually happened yesterday".

## Core rule

Do not stop at assistant prose like:
- "создана задача"
- "файл готов"
- "собрала данные"
- "отправила результат"

In Hermes-style runtimes these claims must be checked against the actual side-effect tables and artifacts.

## Audit order for recent-day slices

1. Fix the date window from the live server clock.
2. Exclude any out-of-scope users the operator named.
3. Summarize activity by user first:
   - count `chat_tasks`
   - count completed vs error vs pending/started
4. Pull non-completed tasks and non-empty `last_error`.
5. Read the corresponding `messages` to inspect the exact user-visible assistant text.
6. Verify side effects separately:
   - recurring/scheduled actions -> `app.jobs`
   - exported file claims -> attachment/export metadata and stored file records
   - data-collection claims -> collection result metadata and produced artifact
7. Only after that classify the problem as:
   - source-stage failure
   - export/delivery failure
   - false-success orchestration bug
   - runtime/service incident

## Concrete patterns seen in practice

### 1. Claimed scheduled job was not actually created

Symptom:
- assistant says a recurring monitoring/digest job was created
- no corresponding row appears in `app.jobs`

Classification:
- false-success orchestration defect

Why it matters:
- this is worse than a normal error message because the user is told the system already acted

### 2. Export flow falls back to useless file output

Symptom:
- request is about transforming/refactoring content into a useful deliverable
- runtime emits errors like `message_export_target_missing`
- later it exports an intermediate chat reply as `.xlsx` / `.docx` / similar
- filename may look malformed or generic

Classification:
- export/delivery defect, not successful completion

### 3. Collection request fails, then degrades to contract-only flow

Symptom:
- first request fails with collection/source-stage error
- retry produces only a `collection_contract` acknowledgement instead of the requested result

Classification:
- source materialization or acquisition-stage blocker, not completed collection

## Service-layer cross-check

After user-level DB inspection, scan the backend journal for the same window.
Pay special attention to:
- `Address already in use`
- repeated restart loops
- DB adapter exceptions (`InvalidDatetimeFormat`, placeholder/SQL issues)
- parsing/output-contract exceptions

This separates user-request defects from runtime incidents that can affect many interactions at once.

## Reporting pattern

When you finish, separate:
- confirmed user-facing defects
- infrastructure/runtime incidents
- cases that completed successfully
- cases where text claimed success but side effects were missing
