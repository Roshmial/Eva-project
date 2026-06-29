# API-server origin delivery vs dedicated job-thread delivery

## Why this note exists

A recurring diagnostic pitfall is to conflate three different statements:
1. "the scheduler did not run";
2. "the result did not appear in the original request chat";
3. "the result did not reach the dedicated job thread".

In Hermes Web contours these are not equivalent.

## Confirmed pattern

On the live `178` contour:
- `hermes-gateway.service` was active and `hermes cron status` reported that jobs fire automatically;
- a one-shot `no-agent` probe job with `deliver=local` produced an output file on schedule without manual `cron run`;
- existing `deliver=local` jobs also showed successful `Last run` values.

So the scheduler path itself was healthy.

## What actually failed

The failing jobs had this shape:
- `deliver='origin'`
- `origin.platform='api_server'`
- `last_status='ok'`
- `last_delivery_error='delivery error: Adapter send failed: API server uses HTTP request/response, not send()'`

This means execution succeeded and the failure happened only during the return-delivery step.

## Mechanical cause

`cron/scheduler.py` resolves `deliver='origin'` by sending the result back to `job.origin.platform/job.origin.chat_id`.

For Web-created jobs, origin may be:
- `platform='api_server'`
- `chat_id='api-...'`

But `gateway/platforms/api_server.py` intentionally does not behave like a normal messaging adapter for cron returns:
- `send()` returns `API server uses HTTP request/response, not send()`.

So the scheduler is healthy, but `deliver=origin` is the wrong bridge when origin points at `api_server`.

## UX/product framing

Do not automatically describe the target as "the same chat".

For Hermes Web recurring jobs, the agreed UX may be:
- request starts in a normal chat thread;
- execution result lands in a separate `thread_kind='job'` dialog.

Therefore the correct diagnostic sequence is:
1. Was the job created from the request chat?
2. Did the scheduler execute it?
3. Was the result reconciled into the dedicated job thread?

## Practical conclusion

When this pattern appears, frame it as:
- not a scheduler outage;
- not necessarily a wrong-UX complaint about "not replying in the same chat";
- specifically a broken delivery bridge from cron output into the Web job-thread contour.
