# Run-now vs create/reuse recurring job, plus partial egress triage

Use this reference when a user reports a recurring-monitoring thread behaving inconsistently around phrases like `запусти сейчас`.

## Concrete prod pattern

Observed shape:
- A user had an existing recurring monitoring job in `jobs`.
- In chat, the phrase `запусти сейчас` returned `job_created` / `job_reused` style messaging instead of a run result.
- A direct `manual` execution of the same job later succeeded and wrote a digest into a dedicated job thread.
- A separate generic chat collection request sometimes answered `не смог`.

## Diagnostic split

Treat these as separate questions:
1. Did the chat request create/reuse a recurring job?
2. Did the runtime manually execute an existing job right now?
3. Where does the product expect the result to appear: original chat thread or `thread_kind='job'`?
4. Did generic web collection fail because of total egress loss, or only because some sites block automation?

## Fast checklist

1. Read the exact user wording.
   - `поставь на еженедельную основу`, `создай мониторинг` -> setup/create intent.
   - `запусти сейчас`, `выполни сейчас` -> run-now intent.
2. Inspect `jobs` for an existing active match by owner + normalized subject.
3. Inspect `job_runs` for recent `trigger_type='manual'` rows.
4. Inspect delivery target thread:
   - original request chat;
   - dedicated job thread.
5. Probe outbound access with more than one source before claiming `no internet`:
   - if one source returns `200` but others return `401/403/503`, classify as partial source reachability / anti-bot friction.

## Interpretation rule

If `run now` text gets a create/reuse answer while an existing job is already present and a direct manual run succeeds, the primary defect is chat-intent routing — not scheduler health.

If at least one outbound source works from the same runtime, do not conclude `browse is broken`. Phrase it as partial reachability and identify which sites reject automation.
