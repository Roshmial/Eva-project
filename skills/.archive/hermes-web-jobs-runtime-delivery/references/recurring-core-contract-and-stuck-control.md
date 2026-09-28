# Recurring core contract and stuck control

Use this reference when Hermes Web recurring/jobs work is broader than a one-off fix and needs a stable product contract across backend, jobs UI, and chat delivery.

## Session pattern

A productive order for recurring-core work was:
1. backend run/result contract;
2. jobs detail/history UI;
3. delivery route vs personal subscription separation;
4. recurring message summary envelope;
5. stuck/pending recovery;
6. targeted smoke + `py_compile` + frontend build.

This order mattered because UI work became simpler once backend semantics were explicit.

## Backend contract that proved useful

### Job runs
Normalize user-visible run state instead of exposing only raw `success/error`:
- `running`
- `completed`
- `completed_with_limitations`
- `empty_result`
- `failed`

Useful serialized fields:
- `public_status`
- `result_kind`
- `status_reason`
- `status_detail`
- `delivery_summary`
- `delivered_count`
- `has_result_text`
- `has_error`
- `finished_at`
- `duration_ms`
- `is_stuck` when applicable

Useful last-run fields on job payload:
- `last_run_public_status`
- `last_run_status_reason`
- `last_run_status_detail`
- `last_run_delivery_summary`
- `last_run_finished_at`

### Recurring message family
For `job_delivery` / `processing_status` or `source=job_run`, attach a compact recurring summary envelope in message metadata.

A minimal envelope that worked well:
- `status`
- `summary`
- `status_reason`
- `status_detail`
- `delivery_summary`
- `result_kind`
- `has_result`
- `has_limitations`
- `delivered_count`
- `is_stuck`

The point is not a universal schema engine. The point is one stable summary layer that both jobs UI and chat UI can trust.

## Important implementation pitfall: stale-state detection needs row timestamps

If a recurring message serializer tries to classify old `processing_status` rows as stuck, the helper must receive a real persisted timestamp such as `row.created_at`.

Do not assume parsed `meta_json` contains enough time context.

Failure mode:
- helper has stale-state logic,
- but `serialize_message()` passes only `meta`,
- so the helper never sees `created_at`,
- old pending messages still serialize as `running`.

Fix pattern:
- pass `created_at=row["created_at"]` (or equivalent) into the recurring-summary/surface helper explicitly,
- add a smoke test that feeds an old message row and expects stuck/failed serialization.

## Stuck/recovery policy that fit the existing local-first stack

Prefer reusing the current backend lifecycle over adding new infrastructure.

### Chat tasks
- add a threshold like `CHAT_TASK_STUCK_SECONDS`;
- find `chat_tasks` with `status='running'`, `finished_at IS NULL`, and stale `started_at`;
- move them back to `pending`;
- clear `started_at`;
- rewrite the assistant placeholder message back to pending state;
- annotate recovery in meta, e.g. `recovered_after_stuck=true` and a human status label.

A good integration point was the existing `claim_pending_chat_tasks()` path, which first recovers stale running tasks and only then claims pending work.

### Job runs
- add a threshold like `JOB_RUN_STUCK_SECONDS`;
- during serialization, if `status='running'`, `finished_at` is empty, and `started_at` is stale, surface it as failed/stuck for the UI;
- return explicit `status_reason='stuck'` and a delivery/detail string that says the run exceeded allowed time.

This gives the user an honest operational state even before deeper scheduler recovery exists.

## UI pattern that reduced ambiguity

### Jobs screen
Show for the active job / run history:
- public status,
- summary,
- status reason,
- delivery summary,
- result kind,
- timestamps,
- duration.

### Subscription vs delivery route
Do not mix these in one control block.
- `recipients` = where the job is configured to deliver;
- `subscription` = whether the current user personally receives it as a subscriber.

### Chat recurring rendering
If `meta.recurring_summary` exists, render it as a dedicated recurring result block instead of leaving meaning buried in free-form text.

## Verification subset that worked well

Targeted smoke tests were more informative than running a broad noisy suite:
- run serialization for completed / empty / degraded / failed;
- recurring summary envelope for `job_delivery` and `processing_status`;
- stuck `job_run` -> failed/stuck;
- stuck `processing_status` -> failed/stuck;
- stale `chat_task` recovery back to `pending`.

Then verify with:
- `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py`
- `npm run react:build`

If a wider suite still has unrelated red tests, do not let that block a truthful recurring-core acceptance report. Separate recurring-related proof from ambient suite noise.
