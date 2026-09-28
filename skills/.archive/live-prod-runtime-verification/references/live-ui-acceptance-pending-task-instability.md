# Live UI acceptance: pending-task instability and scenario grading

Date: 2026-06-20
Skill: `software-development/live-prod-runtime-verification`

## Why this reference exists

This session established a durable verification rule for Hermes-style web runtimes: when the user asks for final testing through the user interface, the verdict must be based on the raw UI path first, not on whether an engineer can later coerce the backend into producing a result.

## Verified contour

- Frontend UI: `95.182.85.233:8803`
- Backend API/runtime: `178.104.207.89:8791`
- Test user: dedicated prod-like demo user

## Durable lessons

### 1. Health is not enough

Observed pattern:
- `/api/health` stayed green;
- `chat_processor.enabled=true` and `running` could be non-zero;
- but fresh `chat_tasks` still remained in `pending` and did not start automatically.

Lesson:
- acceptance must inspect actual task progression, not just service health;
- a green runtime can still fail the product-level contract if user chat tasks are not being consumed.

### 2. Manual task draining is diagnosis, not acceptance

During UI testing, several scenarios produced valid results only after an off-process call to:
- `process_pending_chat_tasks_once(max_tasks=...)`

This is acceptable as a diagnostic aid, but not as proof that the user-path works.

Classification rule captured from this session:
- raw UI completion without intervention -> pass
- result only after manual processing -> unstable / partial pass
- runtime error / timeout / wrong route -> fail for the requested scenario

### 3. Mixed scenario grading must be route-specific

A single broad request can hide several distinct layers:
- acquisition from source
- analysis/classification
- dashboard generation
- artifact delivery

A scenario must not be marked "working" just because one layer works.

Examples from the session:
- `web -> classify -> csv file` produced a real artifact and downloadable attachment: this confirmed the collection/file contour.
- `collect from internet and build dashboard` returned a processing error (`'NoneType' object is not subscriptable`): this is a dashboard/runtime defect, not a generic LLM weakness.
- Telegram export could reach clarification and then fail with upstream timeout: this confirms the route exists but the end-to-end contour is not stable.

### 4. Follow-up over prior file/data is a different acceptance class

Requests like:
- analyze the previous file
- build a proposal based on previous data
- give a preliminary estimate based on previous data

may succeed as generic chat responses while still bypassing a stricter specialized execution path.

Acceptance note:
- distinguish `generic chat answer over prior thread context` from `specialized controlled proposal/estimate pipeline`.
- If the user asked for the latter, a plain assistant answer is only a partial success.

## Scenario grading snapshot from this session

### Clear passes
- plain `расскажи про ...`
- code review for pasted snippet
- file download from generated collection artifact

### Partial / unstable
- internet research request that required manual backend rescue before completion
- file-based analysis / proposal / estimate answers that completed but used generic assistant reply rather than a stricter controlled pipeline
- web collection to CSV that produced the right artifact but required manual backend processing during acceptance

### Fails or not-pass-as-requested
- dashboard request that returned processing error
- Telegram export request that ended in timeout/error after clarification
- prompts that expected a specific execution contour but were answered via generic fallback/clarification inconsistent with the requested end state

## Recommended verification sequence for future sessions

1. Run each target scenario from the UI only.
2. Record whether the assistant placeholder completes by itself.
3. If not, inspect:
   - `chat_tasks.status`
   - `started_at/finished_at`
   - thread messages and `message_kind`
   - live logs
4. Only then use manual processing/restart as diagnostic escalation.
5. Keep the user-facing verdict tied to step 2, not step 4.
