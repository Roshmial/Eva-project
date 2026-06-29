---
name: hermes-web-jobs-runtime-delivery
description: "Live delivery and verification of Hermes Web job/task flows: chat-to-job creation, recipient visibility, stale UI state, and Moscow-time schedule rendering."
---

# When to use

Use this skill when Hermes Web tasks/jobs must be fixed or verified in a real runtime, especially if the user reports any of these symptoms:
- the assistant said a recurring task was created, but no job appeared;
- `+ Новая задача` or job settings blank the screen / reset the page;
- the job creator or assigned user cannot see the created job;
- schedule time in chat text and job UI differ (for this user, Moscow time is the business truth);
- backend health is green, but the actual chat -> task/job contour is suspect.

This skill is for live local-first delivery, not paper analysis. Finish with a real runtime state and real verification evidence.

# Core rules

1. Verify the actual contour in use first.
- Identify which frontend is serving the user-facing UI and which backend/API it calls.
- If the user points to a specific server, verify that exact contour directly. Do not drift into generic architecture discussion.
- Confirm whether the local UI proxies to a remote backend or is fully local before drawing conclusions.

2. Separate three failure classes.
- Chat -> job persistence failure: assistant text claims scheduling happened, but no persisted job exists.
- Visibility/access failure: job exists, but intended user cannot see it in `/api/jobs` or open `/api/jobs/{id}`.
- UI state/runtime failure: list renders, but `activeJobId`, modal handlers, or detail fetches still blank the screen.

3. Treat health checks as necessary but insufficient.
- A green `/api/service-info` or healthy process does not prove job creation, access control, or UI correctness.
- Always verify the business flow, not only service liveness.

4. Moscow time is the business truth for this contour.
- New/default job creation and UI rendering must use `Europe/Moscow`.
- Distinguish current regressions from legacy data already stored in UTC.
- Do not claim the timezone problem is fully gone if only rendering changed but old jobs still show UTC-derived times.

# Delivery workflow

## 1. Reconstruct the exact symptom from data

For a reported missing recurring task:
- inspect the user's thread/messages around the request;
- verify whether the assistant replied as if the task had already been created;
- check whether a real job row exists for that user;
- check chat-task/task-run records separately from jobs.

For a reported false-positive recurring task:
- inspect the exact user message that triggered chat-task completion;
- distinguish a real scheduling intent ("поставь", "на регулярной основе", "ежедневно", "еженедельно") from an ordinary research/search request ("подбери", "найди", "собери перечень");
- verify whether the backend classified the request from the current user message or from broad recent context that may include assistant text.

Important: chat success text is not evidence of persistence.

## 2. Verify job existence and access separately

For each suspected job:
- confirm persisted job record;
- confirm recipients / ACL / owner semantics;
- verify `/api/jobs` for the intended user;
- verify `/api/jobs/{id}` for the intended user;
- treat `403/404` on detail fetch as a separate access/state problem even if list loading looks fine.

## 3. Reproduce the UI crash paths explicitly

After any fix, exercise all of these:
- `+ Новая задача`;
- open settings on an existing job;
- stale saved UI state with an invalid `activeJobId`.

Do not stop at "the list page opened".

If the user described a blank screen:
- use browser console after each action;
- treat live JS exceptions as blockers, even if some DOM still rendered.

## 3a. When the complaint is about bad text shown in the UI, verify the frontend contour before chasing cron/backend outputs

Use this branch when the user reports that the web screen showed internal reasoning, duplicated blocks, raw prep text, or a mixed `analysis + final` reply.

1. Verify the exact user-facing frontend contour first.
- Confirm the real frontend port/service the user is looking at.
- Confirm which backend/API that frontend proxies to.
- Do not inspect unrelated local ports or a different backend contour just because they are familiar.

2. Distinguish three artifacts that may disagree.
- preserved cron/job output files;
- backend message payload returned by `/api/threads` or equivalent;
- frontend-rendered text after `messageDisplayText` / markdown rendering / UI post-processing.

3. If preserved cron output is clean but the UI showed leaked internal text, do not conclude the user was mistaken.
- The bad text may live in persisted message `content` for the chat/thread even when cron output files look normal.
- The frontend may also be rendering raw assistant `content` instead of a safe display field.

4. Read the frontend renderer path directly.
- Inspect the function that maps a message object to visible text (`messageDisplayText`, `renderMarkdownContent`, equivalent).
- Check whether the UI renders `message.content` as-is with only cosmetic cleanup.
- Treat that as a real product bug if assistant/internal prep text can reach the database or API.

5. Prefer a contract fix over regex-only cleanup.
- Best fix: backend exposes a dedicated safe field such as `display_text` / `final_text` for user-facing rendering.
- Frontend should prefer that safe field over raw `content`.
- A frontend regex that strips obvious prep markers is only a fallback guard, not the main contract.
- If you implement this fix, carry it through the whole delivery path: assistant meta enrichment, message serialization/backfill for legacy rows, cron/job output extraction, and the frontend renderer. See `references/safe-display-contract.md`.

6. Lock the fix with a narrow regression trio.
- Add one serializer test proving raw `content` may still contain leaked prep text while `display_text` is safe.
- Add one delivery extraction test proving cron/job output cleanup uses the same safe display path.
- Add one compatibility test proving threads/jobs endpoints still serialize the affected message family without 500s.

## 4. Fix backend truth before frontend cosmetics

Priority order:
1. real job persistence / routing;
2. access rules / recipient visibility;
3. frontend fallback/state guards;
4. formatting and display.

If the backend says the job does not exist, do not spend the bulk of effort polishing the UI.

## 5. Re-verify with a fresh test object

After fixes:
- create a fresh verification job or recurring request;
- validate that the assigned user can see it and open details;
- validate next-run time is shown in Moscow time;
- keep legacy jobs separate in the analysis so they do not mask whether new behavior is fixed.

# Recurring-core implementation pattern

When the task is not just a one-off UI bug but a broader recurring/jobs core pass, use this sequence instead of jumping straight into screen polish:

1. Backend contract first.
- Normalize job run states before touching the UI.
- At minimum separate:
  - `running`
  - `completed`
  - `completed_with_limitations`
  - `empty_result`
  - `failed`
- Add user-facing fields in serialized runs/jobs so the frontend does not infer meaning from raw status alone.

2. Jobs surface second.
- Wire the jobs list/detail/history to the normalized backend contract.
- Show last-run reason, delivery summary, result kind, and timestamps explicitly.
- Separate delivery route (`recipients`) from personal subscription state (`job_subscriptions`) in the UI.

3. Recurring message family third.
- For job/monitoring outputs in chat threads, attach a normalized recurring summary envelope in message metadata rather than relying on free-form text.
- Prefer a stable family like `job_delivery` / `processing_status` plus a compact `recurring_summary` block containing status, reason, result kind, delivery summary, and whether result/limitations exist.
- Then render that envelope as a dedicated recurring summary block in chat UI.

4. Stuck/recovery policy fourth.
- Do not leave old `running` / `pending` states ambiguous forever.
- Add a time-based threshold for stale `chat_tasks` / `job_runs`.
- Reuse the current backend lifecycle: recover stuck `chat_tasks` inside the existing claim/processor path rather than introducing a separate daemon.
- In serializers, convert stale `running` into a user-visible stuck/failed state with an explicit reason and detail.

5. Verify by narrow subsets, not by hoping the whole suite explains itself.
- Add targeted smoke tests for:
  - run-state serialization,
  - recurring summary envelope,
  - stuck recovery.
- Use `py_compile` and frontend build as the regression bar even when a wider backend suite still contains unrelated red tests.

## Additional pitfall: recurring/job messages need real time context for stale-state classification

If you implement stuck detection for `processing_status` or other recurring message families, do not rely only on message `meta`.

Typical trap:
- the stale-state classifier looks for `created_at` / `started_at`,
- but `serialize_message()` passes only parsed `meta_json`,
- so old pending messages still render as `running` forever even though the logic appears present.

Correct pattern:
- pass the persisted row timestamp (`row.created_at`, or equivalent real message timestamp) into the recurring-summary / surface helper explicitly;
- then verify with a targeted smoke test that an old `processing_status` serializes as stuck/failed, not still `running`.

# Pitfalls

- `references/recurring-core-contract-and-stuck-control.md` — concrete recurring-core implementation pattern: backend run contract, chat recurring summary envelope, subscriptions-vs-recipients split, and stuck recovery wired into existing chat-task lifecycle.

- "Assistant said done" is not proof. The model may promise scheduling while no job was persisted.
- A list that loads can hide broken detail fetches.
- Stale `activeJobId` in saved UI state can recreate a blank screen even after backend fixes.
- Fixing `toLocaleString()` alone is not enough if defaults/fallbacks still create jobs in UTC.
- Historical UTC jobs can remain in the UI after the fix; classify them as legacy data unless new jobs reproduce the drift.
- False-positive recurring creation can come from classifying against `recent_context` that includes assistant replies. For chat-to-job creation, the create/don't-create decision must be driven by the current user message's explicit scheduling intent; prior context is safe only for subject extraction after intent is already established.
- A useful regression pair is: (1) explicit scheduling request still creates a job; (2) ordinary research/search phrasing about monitoring sources does not.

# Definition of done

Only call it done when all are true:
- the live contour is updated/restarted on the real target runtime;
- a fresh recurring job path persists an actual job;
- the intended user can see and open that job;
- `+ Новая задача` and existing job settings no longer blank the screen;
- new job times render in Moscow time;
- any remaining wrong times are explicitly identified as legacy job data, not current code behavior.

# References

- `references/chat-recurring-job-gap.md` — concise reproduction pattern for the failure mode where chat claimed a recurring task was scheduled but no persisted job existed, plus the paired visibility/UI pitfalls discovered during live verification.
- `references/chat-recurring-job-false-positive.md` — prod pattern where ordinary research requests were wrongly converted into recurring monitoring because classification used recent context instead of explicit scheduling intent in the current user message.
- `references/safe-display-contract.md` — safe user-facing rendering contract for leaked assistant/job delivery text: backend `display_text`, frontend preference order, and the minimal regression trio.

# What to record in decision-log

For major task/job incidents, record:
- whether the root cause was persistence, visibility, or UI state;
- whether the fix changed backend truth, frontend fallback, or both;
- whether any remaining timezone anomalies are legacy-data cleanup rather than active regressions.
