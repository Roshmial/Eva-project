# August 2026 daily structure and stability pass

Use this note when Misha says the daily is still weak even after many prompt bans.

## Session lesson

The real fix was not another wording ban. The contour had to move from prompt-healing to structure:
- preflight script emits day anchors;
- preflight emits task families;
- preflight emits suggested raw tasks;
- renderer mainly turns those tasks into live Telegram lines;
- same-date rerun stability is enforced by baseline reuse, not by hoping the model stays consistent.

## Durable corrections

### 1. Do not keep re-deciding the day in the agent layer
If preflight already knows:
- today_event;
- tomorrow_event;
- whether a near personal anchor exists;
- the allowed task families;
- the suggested raw tasks;

then the agent should mostly render and reject.

If the renderer starts inventing new storylines, the contour is still too prompt-heavy.

### 2. Personal self-reference must stay in the user's point of view
When the nearby anchor is the user's own birthday, lines like `день рождения Михаила` sound alien.

Normalize this before rendering:
- good: `как отметить завтра день рождения`;
- bad: `как отметить день рождения Михаила`.

This belongs in preflight normalization and reject-list, not only in style commentary.

### 3. Same-date rerun stability needs its own structure
A good one-off run is not enough.

During manual tuning on the same morning, check repeated outputs for drift:
- weather line;
- extra filler words like `быстро`, `просто`, `короткий рабочий`;
- accidental synonym churn with no user value.

If drift appears, emit a `SAME_DATE_STABILITY_BASELINE` block from preflight and instruct the renderer to reuse clean wording by default.

### 4. Stability beats fake freshness
For same-date reruns, wording novelty is not a goal.

If task families did not change, keep the stable line unless there is a real reason to rewrite it.

## Practical preflight fields that helped
- `STRUCTURED_DAY_ANCHORS`
- `TASK_FAMILIES`
- `SUGGESTED_RAW_TASKS`
- `SAME_DATE_STABILITY_BASELINE`
- `STABILITY_RULES`

## Why this mattered
Before the structural stability pass, same-date reruns drifted between versions even when the day itself had not changed.
After the preflight baseline was added, repeated live runs produced identical final lines, which is the useful test for cron stability in this workflow.
