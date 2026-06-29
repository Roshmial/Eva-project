# Hermes Web dashboard follow-up and retrieval debugging

Use this note when a live dashboard thread appears "fixed" at one layer but still produces low-quality or off-topic output.

## Two-step acceptance rule

Do not stop at `task.status = completed`.

Check both:
1. route/runtime correctness — the task completed on the intended specialized path;
2. content correctness — the saved answer and persisted sources are actually on-topic.

## Live inspection checklist

For the same thread, inspect:
- user message text for the failing turn;
- prior assistant `message_kind` and `downstream`;
- current task `status`, `last_error`, and completion time;
- saved `assistant_message.content`;
- persisted structured payload (`dashboard`, `dashboard_builder`, `dashboard_intent`, `web_sources`, `collection_rows_preview`).

A common pattern is:
- parser/runtime bug first;
- after that is fixed, a short follow-up still routes to the generic dashboard/LLM path;
- after routing is fixed, retrieval/query quality is still bad.

## Follow-up routing lesson

Short rerun prompts like:
- `Построй снова дашборд`
- `ещё раз`
- `теперь с информацией`

must inherit the previous dashboard topic when the thread context clearly establishes it.

If they do not, inspect whether routing decisions are made from raw `user_text` instead of the effective follow-up request reconstructed from thread history.

## Retrieval/planner lesson

If the query is topic-relevant but sources are nonsense, inspect the search planner before touching renderer/UI code.

In acronym-heavy subjects, verify:
- extracted `subject` is non-empty;
- acronym expansion exists (`BI` → `business intelligence`);
- `subject_phrases` prioritize the normalized broad phrase;
- the first generated queries are broad and topical, not malformed hybrids.

Red flag examples:
- `bi-инструментов инструментов bi-практик практик`
- topic acronym only appears as a weak tail query
- top selected sources are off-domain even though intent/routing is correct

## Good fix shape

Prefer generic planner fixes over topic-specific branches:
- improve subject extraction for dashboard phrasing;
- expand acronyms into broad search phrases;
- lower priority of malformed hybrid tokens;
- reorder generated queries so normalized broad phrases come first;
- then rerun the same live task and inspect the stored sources again.

## Verification standard

A fix is not done until the same live task/thread shows all of the following:
- `downstream` is the intended specialized dashboard path;
- `assistant_message.content` is on-topic;
- persisted `web_sources` are recognizably relevant;
- at least one unrelated topic class still behaves sensibly after the planner change.
