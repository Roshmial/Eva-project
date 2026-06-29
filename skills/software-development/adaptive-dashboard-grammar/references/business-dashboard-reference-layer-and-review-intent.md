# Business dashboard reference layer and `review` intent

## When this matters

Use this note when evolving Hermes-style dashboards from backend-only prompt rules toward a reusable grammar layer.

## Key lesson

Do not keep adding narrow backend branches like "file dashboard", "CRM dashboard", "web dashboard" as separate product identities.

Prefer three axes:
- `business function` — sales, marketing, finance, operations, support, HR, product, procurement;
- `analytic intent` — review, market overview, trend, comparison, segmentation, evidence, history/evolution;
- `source shape` — file, web, collected dataset, integration export, connector.

`source` should explain evidence quality and constraints, not define the semantic type of the dashboard.

## `review` as a first-class intent

Add `review` when the user is asking for an overview/explanation/synthesis rather than only chronology or market mapping.

Typical request signals:
- `обзор`
- `review`
- `что это такое`
- `как устроено`
- `как развивалось`
- `общая картина`
- `разбор темы`

Typical `review` output shape:
- summary cards for scope and framing;
- `timeline_list` when there is an evolution/history component;
- `matrix_list` for structure, shifts, or grouped distinctions;
- `text_list` for practical meaning and limitations.

Do not force these requests into `history_evolution` only. History may be one component of review, but not always the full user ask.

## Reusable grammar layer

A good intermediate architecture is:
- backend = routing/orchestration/envelope;
- policy JSON = function detection, metric groups, preferred sections;
- reference dataset / skill-like layer = reusable intent/function guidance for prompt building.

This keeps business logic out of backend-only strings while avoiding a heavy new runtime.

## Practical prompt-building pattern

Compose the prompt from:
1. detected analytic intent;
2. detected business function;
3. blueprint for the intent;
4. reusable reference guidance for intent + function.

Example guidance sources:
- `dashboard_review`
- `dashboard_sales`
- `dashboard_marketing`
- `dashboard_finance`

## Pitfall

If a dataset contains ambiguous column names like `leads`, do not let that alone move the dashboard into `sales` when the request is explicitly about `marketing`, campaigns, or channels. Request wording should outweigh weak column hints.

## Verification

Useful checks after introducing this layer:
- prompt for finance includes finance-specific reference guidance, not just a generic label;
- overview request like BI review resolves to `review` intent;
- the reusable dashboard grammar dataset is exposed in bootstrap/runtime references;
- tests may pass while the test runner process still crashes on teardown — separate logical pass/fail from environment-level shutdown bugs when verifying.