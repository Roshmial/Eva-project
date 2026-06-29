# Business-function metrics layer

Session lesson:
- A dashboard architecture that starts from `file dashboard` or another source-specific mode becomes too narrow once users ask for comparable analytics across files, web research, exports, and future connectors.
- The better stable model is three-axis:
  1. business function;
  2. analytic intent;
  3. source shape.

## Durable design rule

Use:
- `business function` to choose metric families and likely visuals;
- `analytic intent` to choose the analytical question (overview, trend, comparison, segmentation, evidence);
- `source shape` only to describe freshness, confidence, and field availability.

Do **not** let source identity dominate the dashboard title or conceptual mode when the user is clearly asking about an operating domain.

## Why this matters

A file-centric implementation initially solved local analytics, but it created the wrong product boundary:
- `dashboard by file` sounds like transport-level functionality;
- users actually mean `dashboard of sales`, `dashboard of marketing`, `dashboard of finance`, etc.

If the skill is followed, file uploads become just one ingestion path into a shared business-metrics dashboard layer.

## Function inference pitfall

A naive first-match marker approach is unsafe.

Observed failure:
- marketing request + columns containing `leads` was classified as sales.

Safer pattern:
- score functions instead of returning the first marker hit;
- weight explicit request words more strongly than column hints;
- use columns as supporting evidence, not the primary truth.

Recommended weighting baseline:
- request-text match: strong weight;
- column-name match: weaker weight.

## Practical function grammar starter

### Sales
- revenue
- deals
- average deal size
- funnel / stages
- manager contribution
- channel contribution
- period trend

### Marketing
- leads
- campaign/channel mix
- cost
- conversion
- contribution by campaign/channel
- period trend

### Finance
- income
- expenses
- margin
- budget vs actual
- category deviations
- period trend

### Operations
- throughput
- SLA attainment
- cycle time
- backlog/load
- bottlenecks

### Support
- tickets
- first response
- resolution time
- backlog
- category mix
- SLA breaches

### HR
- headcount
- hires
- attrition
- retention
- funnel/time-to-hire
- team/location breakdown

### Product
- activation
- adoption
- usage
- retention
- feature contribution

### Procurement
- spend
- supplier concentration
- lead times
- deviations
- vendor breakdown

## Implementation implication

When evolving a dashboard backend:
- avoid creating separate long-lived product modes like `file_dashboard`, `crm_dashboard`, `spreadsheet_dashboard`;
- prefer a shared `business_function_analytics` envelope with source-specific adapters;
- keep intent-aware fallback rules compatible with function-aware routing.

## Verification ideas

- Same function should survive across different source shapes.
- Same source shape should be able to route to different functions.
- Marketing requests with `leads` should not automatically collapse into sales.
- Titles/cards should prefer function labels (`Продажи`, `Маркетинг`) over transport labels (`CSV`, `файл`) when the function is clear.
