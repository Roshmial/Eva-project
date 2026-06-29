# Job duplicates and thread freshness on prod Hermes Web

Use this reference when an admin reports duplicate mailings/monitoring tasks or when mailing chats jump in recency without a new digest.

## Duplicate audit query shape

For Web-managed jobs, group by:
- `user_id`
- normalized subject from `parameters_json`
- `schedule_kind`
- `days_of_week_json`
- `time_of_day`
- `timezone`

Interpretation:
- multiple active rows in one group = historical duplicate backlog in `jobs`
- this alone does **not** prove the current create-path still duplicates
- verify later chat evidence: if newer threads return `job_reused` / "Новый дубликат не создаю", the guard is already active and the remaining problem is cleanup of old rows

## Concrete prod pattern captured

Observed on prod:
- one admin had multiple active `research_watch` jobs with the same schedule and same subject semantics;
- older rows were created from repeated recurring requests across different chat threads;
- later chat threads already returned reuse wording instead of creating another job.

Practical conclusion:
- classify first as "old duplicates left in DB";
- only call it a live regression if you can reproduce creation of a new duplicate after the guard should exist.

## Freshness pitfall for mailing/job chats

Do not use `threads.updated_at` as the user-visible recency signal for `thread_kind='job'`.

Why:
- sync helpers for job threads can rewrite `updated_at` while only touching title/preview/archive state;
- a user asking something inside the same thread can also move recency without meaning a new digest arrived.

## Better recency signal

For `thread_kind='job'`, prefer one of these:
1. persisted `last_delivery_at`
2. derived timestamp of the latest assistant message whose meta shows real delivery, e.g. `source='job_run'` or `source='hermes_cron'`

Exclude service-only assistant messages such as:
- `message_kind='processing_status'`
- `message_kind='file_response'`

Fallback:
- if no delivery exists yet, use `created_at`

## Product framing

If asked "can we stop refreshing mailing chats on every touch?":
- yes;
- keep `updated_at` as an operational write timestamp;
- sort mailing/job chats by last real delivery instead.
