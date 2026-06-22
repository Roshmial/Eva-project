---
name: scheduled-job-delivery-diagnostics
description: Diagnose Hermes-style scheduled jobs when users report that a digest/task looks completed in UI but no delivery appeared.
---

# When to use

Use this for live diagnosis of scheduled digests, recurring briefs, or chat-created jobs when a user says:
- "задача выполнена, а рассылки нет"
- "job completed but nothing arrived"
- "did it deliver to the wrong place or not run at all?"

This skill is about separating three different states that users often conflate:
1. chat request processed;
2. scheduled job created;
3. scheduled job actually executed and delivered output.

# Core rule

Do not treat a completed chat/task row as proof of delivery.

In Hermes-style runtimes, `chat_tasks.status='completed'` can mean only that the chat request was handled successfully — for example, a weekly job was created. That does **not** prove the scheduled run happened.

# Verification sequence

1. Verify the real runtime contour first.
   - Check the live backend service, not just local assumptions.
   - Confirm which DB driver and DB target the running service actually uses.
   - On prod/split-host contours, a nearby DuckDB file may exist while the live service is actually on Postgres.

2. Resolve the target user.
   - Find the real user row.
   - Use stable identifiers: email, user id, role, created_at if needed.

3. Inspect the user conversation path.
   - Find the relevant chat thread.
   - Read the latest user/assistant messages around the request.
   - Confirm whether the assistant said the job was created, scheduled, or supposedly already sending.

4. Inspect `chat_tasks` for the originating chat thread.
   - Confirm whether the request-processing task completed.
   - Interpret this only as "request handled", not "digest delivered".

5. Inspect `jobs`.
   - Verify owner, status, schedule kind, days, time, timezone, `next_run_at`, `last_run_at`, `last_run_status`.
   - If `next_run_at` is still in the future, a missing digest may simply mean first execution has not happened yet.

6. Inspect `job_runs`.
   - This is the execution truth.
   - No `job_runs` means the scheduled job has never executed.
   - Error rows mean execution happened but failed.
   - Success rows with empty delivery evidence mean delivery routing must be checked next.

7. Inspect the job thread and its messages.
   - Check `threads.thread_kind='job'` and `threads.job_id=<job_id>`.
   - Empty job thread plus no `job_runs` means creation succeeded but no execution happened yet.
   - Messages present in the job thread prove delivery to that thread.

8. Inspect recipients/subscriptions.
   - Check `job_recipients` and `job_subscriptions`.
   - Use this to distinguish "not delivered" from "delivered to another intended recipient".

# Interpretation patterns

Pattern A:
- chat task completed
- job exists and is active
- `next_run_at` is in the future
- no `job_runs`
- empty job thread

Conclusion:
- not a delivery outage;
- this is a semantics / expectation mismatch: the request was completed, but the first scheduled run has not happened yet.

Pattern B:
- job exists
- due time passed
- `job_runs` absent or stale

Conclusion:
- scheduler is the likely fault domain.

Pattern C:
- `job_runs` exist with `status='error'`

Conclusion:
- execution failed; inspect error text and runtime contour.

Pattern D:
- `job_runs` success exists
- delivery thread/messages absent for expected user
- recipients/subscriptions differ from expectation

Conclusion:
- routing / recipient configuration issue.

Pattern E:
- Hermes cron output file exists on time
- Hermes scheduler log shows the job finished on time
- user-facing Web/thread message appears much later
- `hermes_job_recipients` were inserted or replaced around that later timestamp
- `hermes_job_delivery_state.last_delivered_at` also moves only then

Conclusion:
- not a slow cron run;
- this is delayed Web delivery caused by late or changed recipient mapping.
- The useful timeline is: cron generation time, output file mtime, recipient update time, final thread/message creation time.

# Live-prod practice

- Prefer the backend service virtualenv and runtime env bootstrap when probing with Python so imports and DB driver selection match the real service process.
- Check service env / launcher scripts before querying the DB.
- On prod, avoid mixing contours: use the live host that actually runs the backend.
- For Hermes-managed cron jobs mirrored into a Web UI, inspect both layers separately:
  1. Hermes cron layer: scheduler logs, output file timestamp, Hermes `last_run_at`.
  2. Web delivery layer: `hermes_job_recipients`, `hermes_job_delivery_state.last_delivered_at`, target thread messages.
- If the complaint starts with "после обновления списка получателей", treat recipient remapping as a first-class suspect before blaming the scheduler.

# Product/UX pitfall to call out

A common false alarm is timezone wording drift:
- assistant text says something like "09:00 UTC"
- but the stored job uses `timezone='Europe/Moscow'`
- and `next_run_at` actually corresponds to 09:00 Moscow time

Treat this as a response-generation / wording bug, not as proof of scheduler failure.

# Recommended user-facing framing

When reporting findings, separate these states explicitly:
- request processed;
- job created;
- first run scheduled for <time>;
- delivery has / has not actually happened.
- if relevant, whether the delay happened before generation or only after recipient remapping in the Web layer.

Good phrasing:
- "Задача создана. Первый выпуск запланирован на ..."
- "В UI отмечено завершение обработки запроса, но это не означает, что рассылка уже была отправлена."
- "Cron отработал вовремя; задержка возникла позже, когда Web-контур обновил получателей и только после этого доставил готовый output в пользовательские треды."

# Additional pitfall: Hermes cron output vs Web delivery reconcile

In Hermes Web + Hermes cron integrations, separate these four timestamps before you diagnose a "late digest":
- cron/scheduler fired;
- output artifact/file was produced;
- recipient mapping existed and reconcile ran;
- final user-visible delivery record/message was written.

Diagnostic rule:
- If cron output was ready on time but the user-visible message appeared only after an admin opened `/api/jobs`, opened the job card, patched recipients, or manually re-saved the job, the root cause is not the cron schedule. It is a missing autonomous reconcile path between Hermes cron output and Hermes Web delivery.

What to check:
1. Compare output file mtime in `~/.hermes/cron/output/<job_id>/` with the user-visible `messages.created_at` in the Web thread.
2. Check when `job_recipients` / `hermes_job_recipients` rows were last rewritten.
3. Read backend code paths for `reconcile_hermes_job_delivery(...)` and confirm whether they run only from jobs UI/API handlers or from a background worker too.
4. If delivery only happens after recipients update or jobs screen access, classify it as a delivery-reconcile bug, not as acceptable scheduler behavior.

Mitigation hierarchy:
- Fast prod mitigation: background reconcile inside the existing backend runtime.
- Target architecture: event-driven callback from cron completion to backend reconcile/delivery, so delivery does not depend on UI/API access or polling.

# References

See `references/job-creation-vs-delivery.md` for a compact checklist and a concrete diagnostic pattern from a live prod investigation.
See `references/hermes-cron-web-delivery-reconcile.md` for the concrete prod pattern where cron output was on time but Web delivery happened only after recipient remapping / jobs-API-side reconcile.
See `references/hermes-cron-recipient-remap-delay.md` for a concrete prod pattern where cron output was generated on time but user delivery lagged until recipient rows were updated.
