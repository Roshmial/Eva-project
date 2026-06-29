# Research dashboard policy guardrails

Use this note when Hermes Web handles requests like:
- "Проанализируй рынок ... и построй дашборд"
- "Собери информацию из интернета" after a previous dashboard/research ask

## Core lesson

Do not solve this class of problem with an ad-hoc `source_kind=web` hardcode buried only in Python routing.

Preferred shape:
- declare a dedicated policy block for research dashboards;
- let backend routing consult that policy;
- keep the source default, follow-up completion markers, and field requirements in the policy layer.

Example policy responsibilities:
- implicit source for research dashboards when topic + dashboard intent are already clear;
- allowlist of dashboard intents eligible for implicit open-source research;
- whether `dashboard` requires explicit result fields;
- short follow-up markers like `из интернета`, `по открытым источникам`, `с сайта`.

## Why this matters

Without a policy guardrail, the system tends to fall into generic collection-intake behavior and asks for:
- source,
- what to collect,
- output format,
- mandatory fields.

That is wrong for many research/dashboard asks where the user is posing an analytical question, not defining a table schema.

## Routing rule

If all are true:
- explicit dashboard intent is present;
- the subject/topic is already recognizable;
- the request is research/market/history/comparison oriented;
- there are no local attachments that should dominate source selection,

then the route may proceed with policy-approved open-source research instead of blocking on a collection contract.

## Follow-up rule

If a short follow-up only completes the source dimension, do not start a fresh intake.

Examples:
- `из интернета`
- `по открытым источникам`
- `с сайта`

Instead:
- recover the previous substantive user ask in the thread;
- merge it with the short follow-up;
- re-evaluate as one research/dashboard request.

## Pitfall: false history trigger

Do not infer `history_evolution` merely because the query contains years like `2024` or `2025`.
Years alone are weak signals. Require actual history/evolution markers.

## Verification

A fixed implementation should satisfy:
- market/dashboard asks no longer fall into mandatory-field clarification by default;
- dashboard clarification, if still needed, asks for scope/focus more than schema columns;
- short source-only follow-ups inherit the previous topic;
- history dashboards still keep their dedicated route when true history markers exist.
