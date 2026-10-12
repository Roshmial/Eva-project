# API Server origin vs Web job-thread reconcile

Session date: 2026-06-23
Contour: `178.104.207.89`

## What was confirmed live

1. `hermes-gateway.service` can remain enabled/active as runtime + scheduler while Telegram is explicitly disabled on that host.
2. Hermes cron scheduler itself was healthy:
   - a one-shot `no-agent` probe with `deliver=local` fired on schedule;
   - output file appeared under `~/.hermes/cron/output/<job_id>/` without manual `cron run`.
3. Existing `deliver=origin` jobs created from Web/API had `origin.platform = api_server` and showed:
   - `last_status = ok`
   - `last_delivery_error = delivery error: Adapter send failed: API server uses HTTP request/response, not send()`
4. Direct backend reconcile on the same contour successfully created a separate `thread_kind='job'` thread and inserted an assistant message with:
   - `source = hermes_cron`
   - `message_kind = job_delivery`

## Root-cause split

Two different layers were involved and must not be conflated:

### A. Scheduler-side false delivery failure

`cron/scheduler.py` resolved `deliver=origin` back to `origin.platform='api_server'` and then tried adapter delivery.
But `gateway/platforms/api_server.py` intentionally does not support `send()` and returns:

`API server uses HTTP request/response, not send()`

So cron runs looked partly broken even when the output artifact had been produced successfully.

### B. Backend reconcile autonomy

The Web backend already had a real reconcile path:
- `reconcile_hermes_job_delivery(...)`
- `ensure_hermes_job_thread_for_user(...)`
- output source: `~/.hermes/cron/output/<job_id>/`

However, in this session the automatic backend reconcile did not prove fully autonomous in the short live window; direct reconcile created the separate job-thread successfully.

## Useful live pattern

If you see:
- `last_status = ok`
- output file exists on time
- `last_delivery_error` mentions `api_server ... not send()`

then classify it as:
- scheduler/execution = healthy
- direct adapter delivery path = wrong for this contour
- separate Web job-thread reconcile = the real user-facing path to verify next

## Operational rule for split contours

If Telegram is intentionally separate from the runtime host:
- do **not** turn Telegram back on just to prove scheduler health;
- first verify cron with `deliver=local` and output-file evidence;
- then verify Web reconcile into the separate job-thread.

Also inspect systemd dependencies before disabling gateway entirely: on this contour, Web backend/coplilotkit units still depended on `hermes-gateway.service` even though Telegram itself had to remain off.
