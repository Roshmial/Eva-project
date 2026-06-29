---
name: scheduled-job-delivery-diagnostics
description: Diagnose Hermes-style scheduled jobs when users report that a digest/task looks completed in UI but no delivery appeared.
---

# When to use

Use this for live diagnosis of scheduled digests, recurring briefs, or chat-created jobs when a user says:
- "задача выполнена, а рассылки нет"
- "job completed but nothing arrived"
- "did it deliver to the wrong place or not run at all?"

This skill is about separating four different states that users often conflate:
1. chat request processed;
2. scheduled job created or reused;
3. an existing job manually triggered right now from chat (`run now` / `запусти сейчас`);
4. scheduled or manual execution actually delivered output.

# Core rule

Do not treat a completed chat/task row as proof of delivery.

In Hermes-style runtimes, `chat_tasks.status='completed'` can mean only that the chat request was handled successfully — for example, a weekly job was created. That does **not** prove the scheduled run happened.

# Verification sequence

0. Inspect the final delivered artifact first when the complaint is about a missing block/section rather than a missing message.
   - Read the latest saved cron output markdown under `~/.hermes/cron/output/<job_id>/...`.
   - Compare it with the collector report / payload inputs.
   - If the section is already absent in the cron output, classify the issue as generation-contract / prompt shaping, not delivery loss.
   - Only escalate to thread/reconcile/routing checks if the cron output contains the section but the user-facing delivery does not.

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
   - If the user wording is `запусти сейчас` / `run now`, do not stop at job creation state: explicitly check whether the chat route is supposed to create/reuse a recurring job or manually execute an existing one.
   - When a duplicate-looking row exists, separate "historical duplicate already present in DB" from "the current route just created a fresh duplicate again".

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

Pattern F:
- user reports duplicate digests / duplicate monitoring jobs
- `jobs` contains several active rows with the same owner, same normalized subject, same schedule kind, same weekday set, same time, same timezone
- newer chat threads now answer with `job_reused` / "Новый дубликат не создаю"

Conclusion:
- treat this first as a historical duplicate backlog, not automatically as a live regression still creating duplicates on every request.
- Separate two questions:
  1. are there duplicate rows already present in `jobs`?
  2. does the current recurring-job creation path still create new duplicates under the same prompt?
- If later chat evidence shows reuse behavior, classify the incident as "old duplicates remain in prod DB" until new reproductions prove otherwise.

Pattern G:
- scheduler/gateway is healthy and one-shot or `deliver=local` jobs produce output files on schedule
- the failing jobs have `deliver='origin'`
- those jobs were created from Web/API, so `job.origin.platform == 'api_server'`
- `last_status='ok'`, but `last_delivery_error` contains `API server uses HTTP request/response, not send()`

Conclusion:
- do not diagnose this as a scheduler outage.
- execution succeeded; the failure is specifically in the delivery bridge from cron output into the Web/UI contour.
- `api_server` is not a normal messaging adapter for cron return delivery, so `deliver=origin` is the wrong mechanism when origin points at `api_server`.

Pattern H:
- user says `запусти сейчас` / `run now`
- chat thread answers with `job_created` / `job_reused` semantics instead of a run result
- an existing matching recurring job is already present in `jobs`
- `job_runs` later show a successful `manual` run when triggered directly

Conclusion:
- this is not evidence that the scheduler is broken.
- classify first as a chat-intent routing bug: the runtime treated `run now` like create/reuse recurring setup instead of manual execution of an existing job.
- verify whether the product contract expects the run result in the original request thread or in a dedicated `thread_kind='job'` thread before calling the behavior a delivery outage.

Pattern I:
- generic chat collection says `не смог` / `could not`
- but at least one independent outbound probe or search source works from the same runtime
- some target sites return `401/403/503` or similar anti-bot / availability responses

Conclusion:
- do not collapse this into `no external access` or `browse is broken`.
- classify it as partial source reachability / anti-bot friction unless broader probes show total egress failure.
- the debugging question becomes `which sources and paths fail` rather than `is the server offline from the internet`.

# Live-prod practice

- Prefer the backend service virtualenv and runtime env bootstrap when probing with Python so imports and DB driver selection match the real service process.
- Check service env / launcher scripts before querying the DB.
- On prod, avoid mixing contours: use the live host that actually runs the backend.
- When the user's complaint contains action wording (`создай`, `поставь на еженедельную основу`, `запусти сейчас`, `выполни сейчас`), classify the intent explicitly before you read success/failure from `chat_tasks`: setup-intent and run-now-intent go through different correctness criteria.
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

# Additional pitfall: do not use `threads.updated_at` as user-visible freshness for job threads

For `thread_kind='job'`, `threads.updated_at` is often an operational touch timestamp, not a trustworthy "last real digest" timestamp.

Why it drifts:
- job-thread sync helpers such as `ensure_job_thread_for_user(...)` / `ensure_hermes_job_thread_for_user(...)` may update `threads.updated_at` while only rewriting title/preview/archive state;
- ordinary follow-up actions inside the same thread can also move `updated_at` without meaning a new scheduled digest arrived.

Diagnostic implication:
- if an admin says "why did this mailing chat jump to the top?", check whether there is a newer delivery message at all before treating it as a fresh run.
- compare `threads.updated_at` with message-derived timestamps like `MAX(messages.created_at)` and, more importantly, the last assistant delivery message tied to job execution.

Preferred freshness model:
- for chat threads, generic `updated_at` / last-message sorting is acceptable;
- for job threads, prefer a dedicated `last_delivery_at` or an equivalent derived from the latest assistant message whose meta indicates real delivery (for example `source='job_run'` or `source='hermes_cron'`), excluding service-only message kinds such as `processing_status` and `file_response`.
- if the backend already computes a derived field such as `freshness_at`, verify that the frontend sidebar / thread timestamp renderer actually uses that field instead of falling back to raw `thread.updated_at`; otherwise the UI can still show "vacuum time" even when the API is already correct.

If the product question is "can we stop refreshing mailing chats on every touch?", the answer is usually yes: keep operational `updated_at` for writes, but sort user-visible mailing threads by last real delivery, with `created_at` as fallback when no delivery exists yet.

# Additional pitfall: separate job-thread delivery vs replying in the original chat

For recurring jobs created from Web/UI conversations, do not casually describe the expected behavior as "replying back into the same chat" unless the product contract for that specific contour really says so.

In the Hermes Web contour, scheduled jobs often deliver into a dedicated `thread_kind='job'` conversation rather than the original request thread.

Diagnostic implication:
- separate these questions explicitly:
  1. did the request chat successfully create the job?
  2. did the scheduled run execute?
  3. was the result written into the dedicated job thread?
- do not misclassify "result did not appear in the original chat" as a failure when the agreed UX is a separate job dialog.
- when `deliver='origin'` with `origin.platform='api_server'`, the concrete bug may still be a bad delivery bridge into that dedicated job thread — but the conceptual target remains the job thread, not necessarily the original chat.

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

# Additional pitfall: `deliver=origin` with `origin.platform=api_server` is not a normal adapter-send path

In Hermes Web contours where scheduled outputs are supposed to appear in a separate job thread, not in the original request chat, `deliver=origin` can be misleading when the origin platform is `api_server`.

Why this matters:
- `cron/scheduler.py` resolves `deliver=origin` back to the stored origin target;
- for Web-created jobs that target may be `origin.platform='api_server'`;
- `gateway/platforms/api_server.py` does not support `send()` delivery and intentionally returns `API server uses HTTP request/response, not send()`;
- the real user-facing delivery path is the backend reconcile flow (`reconcile_hermes_job_delivery(...)`) that reads `~/.hermes/cron/output/<job_id>/` and writes an assistant message into a separate `thread_kind='job'` thread.

Diagnostic implication:
- if a Hermes cron job shows `last_status=ok` but `last_delivery_error = delivery error: Adapter send failed: API server uses HTTP request/response, not send()`, do not misclassify this as a scheduler outage;
- first separate two questions:
  1. did cron fire and produce output?
  2. did Web reconcile publish that output into the separate job thread?

Live-prod rule:
- in a contour where Telegram is intentionally separated from the runtime host, do not enable or test Telegram delivery just to prove scheduler health;
- verify scheduler with `deliver=local` / output-file evidence first, then inspect Web reconcile separately;
- before stopping or disabling `hermes-gateway.service`, inspect systemd dependencies: Web backend / copilotkit units may still `Require=` the gateway even when Telegram itself must stay off on that host.
- before writing test recipients or querying delivery state, inspect the running backend process env (`/proc/<pid>/environ`, `ps eww`, unit env, launcher script) and confirm the real DB target. A nearby DuckDB file may exist while the live backend is actually on Postgres via `HERMES_WEB_BACKEND_DSN`; conversely, a familiar Postgres contour may be irrelevant while the live backend is actually serving from backend-local DuckDB. Writing probes into the wrong store creates convincing false negatives and fake "restores" that never reach the user.
- when validating recipient visibility, confirm the row from a second connection against the same live DSN before concluding that `fetch_hermes_job_recipients(...)` is ignoring it.
- if the live runtime contour turns out to be a different demo/pilot store, do not assume the user-facing thread already exists there just because it existed in another DB. First inspect the real `users`, `threads`, and `messages` in that live store. In the wrong contour the correct action may be to create the missing job thread and seed the restored delivery there, not to keep patching a different database.

Practical mitigation:
- scheduler-side: treat `origin=api_server` as a reconcile-owned path, not a direct adapter-send path, so successful runs are not marked with a false delivery failure;
- backend-side: if output still does not appear automatically in the separate job thread, inspect whether the backend reconcile worker is truly running autonomously or only after API/UI traffic.

# References

See `references/job-creation-vs-delivery.md` for a compact checklist and a concrete diagnostic pattern from a live prod investigation.
See `references/hermes-cron-web-delivery-reconcile.md` for the concrete prod pattern where cron output was on time but Web delivery happened only after recipient remapping / jobs-API-side reconcile.
See `references/hermes-cron-recipient-remap-delay.md` for a concrete prod pattern where cron output was generated on time but user delivery lagged until recipient rows were updated.
See `references/job-duplicates-and-thread-freshness.md` for a concrete prod pattern on historical duplicate monitoring jobs and why `threads.updated_at` is the wrong user-visible freshness signal for mailing/job chats.
See `references/api-server-origin-reconcile.md` for the split-contour pattern where `deliver=origin` points to `api_server`, cron execution is healthy, and the real delivery path is Web reconcile into a separate job thread.
See `references/api-server-origin-delivery-vs-job-thread.md` for the live pattern where scheduler execution was healthy but `deliver=origin` failed because origin resolved to `api_server`, plus the reminder that the product target may be a separate job thread rather than the original chat.
See `references/api-server-origin-postgres-runtime-mismatch.md` for the specific false-negative pattern where reconcile tests were mistakenly written into DuckDB while the live backend actually used Postgres via `HERMES_WEB_BACKEND_DSN`.
See `references/live-store-split-postgres-vs-duckdb-2026-06-25.md` for the inverse pattern: investigation started in Postgres, but the live Web backend actually served from backend-local DuckDB with a different demo user/thread universe, so the real repair had to be applied there.
See `references/run-now-vs-create-and-partial-egress.md` for the concrete pattern where `запусти сейчас` was misrouted into recurring job creation/reuse and where partial outbound access looked like a total browse outage until sources were probed separately.
