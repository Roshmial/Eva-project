# Job creation vs delivery: compact checklist

Use when a user says a scheduled digest/task is "completed" in UI but no message appeared.

Checklist:
1. Verify the real live runtime DB target from the running backend service.
2. Find the target user.
3. Read the relevant chat thread and latest messages.
4. Check `chat_tasks` for the originating thread.
5. Check `jobs` for owner, schedule, timezone, `next_run_at`, `last_run_at`, `last_run_status`.
6. Check `job_runs`.
7. Check the job thread (`thread_kind='job'`, `job_id=<id>`) and its messages.
8. Check `job_recipients` / `job_subscriptions`.

Interpretation rule:
- `chat_tasks.completed` proves only that the request was processed.
- It does not prove that the scheduled job executed or delivered.

High-value pattern:
- job exists
- active
- `next_run_at` in the future
- no `job_runs`
- empty job thread

Meaning:
- not a delivery failure;
- first scheduled run has not happened yet.

Timezone pitfall:
- assistant wording may claim UTC while DB stores `Europe/Moscow` and `next_run_at` matches Moscow time.
- Diagnose this as a wording / product bug, not a scheduler outage.

Suggested user-facing wording:
- "Задача создана. Первый выпуск запланирован на ..."
- "Завершение в UI относится к обработке запроса, а не к фактической доставке рассылки."