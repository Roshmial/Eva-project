# Session note: recurring media-monitoring request from chat did not create a job

What happened:
- The user reported that Victoria asked in chat to put media collection on a weekly basis.
- The assistant replied as if the task had already been scheduled.
- No job appeared in the tasks list.

Verified failure pattern:
- The chat thread contained the user's scheduling request and the assistant's "done" response.
- `chat_tasks` showed a completed assistant run.
- No matching job existed for the user at that time.
- This proved a real chat-to-job persistence gap rather than a pure UI-visibility bug.

Additional live findings from the same incident:
- Recipient visibility was a separate backend issue: assigned users could fail to see jobs unless `job_recipients` was considered in access logic and `/api/jobs` filtering.
- Blank-screen regression on tasks was real and required browser-console checking; opening job settings surfaced a live JS exception (`handleCloseJobModal is not defined`).
- Moscow-time fixes must be validated on fresh jobs. Old jobs can still show UTC-derived times and should be classified as legacy data, not necessarily a current regression.

Useful verification sequence:
1. Confirm runtime contour actually in use.
2. Check chat messages around the scheduling request.
3. Check persisted jobs for that exact user.
4. Check `/api/jobs` and `/api/jobs/{id}` for intended recipients.
5. Reproduce `+ Новая задача`, settings open, and stale `activeJobId` UI state.
6. Create a fresh verification job and confirm `Europe/Moscow` rendering.
