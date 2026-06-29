# Semantic metric mapping v1 for dataset dashboards

## When to use

Use when a business-function dashboard is built from a dataset and the raw columns do not already expose every KPI in final user-facing form.

Goal:
- move beyond direct column-name matching;
- derive a small set of explainable metrics from common business data structures;
- keep the logic honest and best-effort.

## Supported semantic patterns

### 1. Plan / fact

Detect pairs such as:
- `plan` / `actual`
- `budget` / `actual`
- `target` / `fact`
- `forecast` / `realized`

Preferred output:
- summary card with absolute delta;
- note with relative delta when denominator is safe;
- section showing row/group deltas, not only one global number.

Good user-facing framing:
- `Plan vs Actual`
- `отклонение факта от плана`
- `относительное отклонение`

### 2. Numerator / denominator rates

If a rate column is absent, try deriving it from paired flow columns.

Common examples:
- marketing: `won / leads`, `converted / visitors`
- support: `resolved / opened`
- operations: `completed / incoming`
- product: `activated / signups`
- procurement: `savings / spend`

Rules:
- derive only when numerator and denominator are distinct and denominator is non-zero;
- label derived metrics explicitly as computed/derived in the note when useful;
- prefer understandable names like `Resolution rate`, `Flow efficiency`, `Savings rate` over raw column names.

### 3. Ageing buckets

Detect backlog/overdue ageing structures such as:
- `0-30`, `31-60`, `61-90`, `90+`
- `ageing`, `aging`, `bucket`
- `overdue_*`
- `*_days`

Preferred output:
- one section that shows where volume is stuck by age bucket;
- notes should explain that this is about work or obligations getting old, not just a categorical split.

Typical section titles:
- `Ageing backlog`
- `Ageing обращений`
- `Ageing закупок / просрочек`

### 4. Cohort / retention

Detect retention-like structures from:
- retention columns;
- cohort/period/month/week dimensions.

Preferred output:
- retention summary card;
- timeline-style section by cohort/period when labels exist.

Rule:
- if retention is weakly inferred, keep the wording conservative and avoid pretending this is a full cohort model.

## Function-specific reminders

### Finance
- Plan/fact should usually surface as both a card and a grouped section.
- A single total delta is not enough when row/category-level drift is visible.

### Support
- If no explicit SLA compliance field exists, resolution/opened is a valid fallback proxy for operational closure rate.
- Ageing is often as important as average response time.

### Operations
- When SLA is absent, flow efficiency from completed/incoming can still explain whether the system keeps up.
- Ageing backlog should be preferred over another generic bar chart when bucketed delay data exists.

### Product / HR
- Retention should be treated as a first-class semantic pattern, not just another percent column.
- If cohort labels exist, show them explicitly.

### Procurement
- Savings without spend leaves the user blind to scale; when both exist, derive `Savings rate`.
- Overdue buckets are stronger than a generic vendor split when the real issue is delayed cycle execution.

## Honesty constraints

- Do not derive rates from mismatched columns just because the names look vaguely related.
- Do not turn a proxy into a claimed canonical KPI.
- Do not stack too many semantic cards into one dashboard; prefer a few interpretable ones.
- If unit systems differ across rows or columns, downgrade confidence and keep the note explicit.
