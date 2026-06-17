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

# Pitfalls

- "Assistant said done" is not proof. The model may promise scheduling while no job was persisted.
- A list that loads can hide broken detail fetches.
- Stale `activeJobId` in saved UI state can recreate a blank screen even after backend fixes.
- Fixing `toLocaleString()` alone is not enough if defaults/fallbacks still create jobs in UTC.
- Historical UTC jobs can remain in the UI after the fix; classify them as legacy data unless new jobs reproduce the drift.

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

# What to record in decision-log

For major task/job incidents, record:
- whether the root cause was persistence, visibility, or UI state;
- whether the fix changed backend truth, frontend fallback, or both;
- whether any remaining timezone anomalies are legacy-data cleanup rather than active regressions.
