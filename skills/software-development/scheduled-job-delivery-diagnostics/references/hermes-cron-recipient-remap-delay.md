# Hermes cron → Web delivery delay after recipient remap

Use this reference when a user says a scheduled digest was supposed to go at a fixed time, but the visible Web/job-thread message appeared much later, especially after editing recipients.

## Diagnostic pattern

Check these timestamps separately:
1. Hermes scheduler start time.
2. Hermes cron output file mtime.
3. Web delivery state time: `hermes_job_delivery_state.last_delivered_at`.
4. Target thread message `created_at`.
5. `hermes_job_recipients.created_at` for the active recipient set.

If (1) and (2) are close to the scheduled time, but (3)/(4)/(5) cluster much later, the problem is usually not the scheduler. It is delayed Web delivery after recipient mapping became available or changed.

## Concrete prod pattern observed

Runtime: prod host `178`, Hermes Web backend.

Observed sequence:
- Hermes cron job `64f6e352b557` (`ТГ Дайджест`) scheduled for `09:30 МСК`.
- Scheduler started around `06:30 UTC`.
- Output file `/home/hermes/.hermes/cron/output/64f6e352b557/2026-06-18_06-31-06.md` was written at `06:31:06 UTC`.
- User-facing message for Victoria appeared at `06:53:20 UTC` in the Web job thread.
- Active `hermes_job_recipients` rows for that Hermes job had `created_at` around `06:53:33 UTC`.
- `hermes_job_delivery_state.last_delivered_at` was also around `06:53:20 UTC`.

Interpretation:
- cron generation was on time;
- the late visible message was tied to Web-layer recipient state, not to cron execution time.

## Code path to remember

In `services/backend/app.py`, `reconcile_hermes_job_delivery(...)` only proceeds when Hermes recipients include `fixed_user` or `fixed_thread` targets. If those recipients are absent or only updated later, ready output can sit undelivered to Web threads until recipient mapping is refreshed.

Also inspect update flows that call:
- `replace_hermes_job_recipients(...)`
- `sync_hermes_job_threads(...)`
- `reconcile_hermes_job_delivery(...)`

A recipient edit can effectively become the moment when an already-generated cron output finally gets mirrored into user job threads.

## Reporting guidance

Do not say "cron was late" unless the scheduler start time or output generation time was actually late.

Prefer wording like:
- "Cron отработал вовремя; задержка возникла позже на этапе доставки в Web-контур после обновления списка получателей."
- "Нужно разделять время генерации output и время, когда Web-контур смог разложить его по пользовательским тредам."