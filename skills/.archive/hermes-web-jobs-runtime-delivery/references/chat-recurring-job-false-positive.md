# False-positive recurring job creation from chat context

## When this reference matters

Use this when a user reports that a normal chat request was silently turned into a scheduled monitoring task.

## Confirmed prod pattern

Observed on Hermes Web prod `178.104.207.89` with user Elena (`user_id=8`).

Conversation pattern:
- user asked ordinary research questions about Telegram channels;
- no explicit scheduling request was present;
- assistant still replied with `Создала задачу ...` and created daily monitoring jobs.

Example non-scheduling user phrases that must NOT create recurring jobs on their own:
- `Подбери перечень телеграмм-каналов, который актуально мониторить для технологической практики`
- `найди перечень каналов крупных вендоров и интеграторов для мониторинга`

Counter-example that SHOULD still create a recurring job:
- `Можешь поставить сбор этой информации на еженедельной основе?`

## Root cause

In `maybe_create_recurring_job_from_chat()`, the classification path used `recent_context or user_text`.

That widened the decision surface from:
- current user intent

to:
- recent thread context, including previous assistant replies.

If the assistant had talked about monitoring, recurring tracking, or setup capabilities, that text could contaminate classification and make an ordinary research request look like a scheduling request.

## Safe rule

For chat-created recurring jobs:
1. Decide whether to create a recurring job from the current user message only.
2. Allow recent context only after recurring intent is already established, and only for extracting the subject / schedule refinement.

## Regression checks

Minimum pair of tests:
1. Positive: explicit schedule request still creates a recurring job.
2. Negative: ordinary research/search phrasing about channels/sources does not create a recurring job.

## Operational cleanup

If false-positive jobs were already created in prod:
- inspect all jobs for that user;
- pause or remove the unintended jobs;
- clear `next_run_at` if pausing;
- verify backend logic before leaving the runtime, so the same user is not re-exposed on the next message.
