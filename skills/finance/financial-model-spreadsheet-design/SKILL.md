---
name: financial-model-spreadsheet-design
description: Use when building Excel financial models. Keep drivers.
version: 1.0.0
metadata:
  hermes:
    tags: [finance, excel, unit-economics, planning, allocation, forecast]
    category: finance
---

# Financial Model Spreadsheet Design

## Purpose

Build user-operable Excel models whose commercial grain, cost allocation, plan/fact/forecast logic, and formulas remain understandable to both an analyst and a manager.

Use the bundled `xlsx` skill for file mechanics. This skill governs model architecture, sequencing, and quality gates.

## Procedure

1. **Audit the exact workbook supplied for the current iteration before designing.** Treat the user's deletions, renamed sheets, and revised allocation as the new source of truth; do not regenerate an older model and overwrite those decisions. Inventory sheets, formulas, named ranges, links, input cells, output cells, and the dependency graph. Identify every business direction, saleable item, cost marker, allocation driver, and unit of measure. Scan by sheet for `#REF!` and external-book tokens before extending the model, because deleted sheets often leave apparently intact but unusable formulas. Treat cached results as outputs, not reusable inputs.
2. **Lock the model grain.** Put sales planning and actuals at the lowest commercially meaningful grain: product/project, purpose or focus, scale, unit, month, quantity sold, and price of that month’s sale. Keep direction-level sheets as summaries derived from those rows; never ask for the same volume again at direction level.
3. **Separate catalog, plan, fact, and forecast.** The catalog defines what can be sold and supplies a calculated price benchmark. Plan and fact use identical product/project rows with separate monthly quantity and monthly unit-price inputs, because the same S/M/L/XL offer may close at materially different prices in different months. Calculate monthly revenue as quantity × that month’s price. Forecast uses fact for closed months and a separately visible future estimate for open months.
4. **Preserve allocation semantics.** Carry source markers and driver logic forward before changing layout. For a user-facing monthly allocation journal, show only the useful fields: month, marker, driver, amount, driver value, total driver, destination, and allocated amount. Add a plan/fact/forecast selector only when needed. Represent absent weights as explicit zeroes so they are auditable rather than blank references.
5. **Keep pricing dynamic but overridable.** For every product, calculate cost from live cost/resource drivers and calculate a benchmark price as `cost / (1 - target gross margin)`. Keep a separate established-price override; the applied catalog price uses the override when present. Treat the catalog price as guidance: Plan and Fact must still allow month-specific sale prices. For consulting, derive cost from project hours × current full cost rate; never paste cached source prices.
6. **Build an RSM resource layer for the whole portfolio.** Model costs and resources together for every saleable service, not only the direction with the richest source detail. Maintain a common resource catalog, monthly available capacity and rates, and a normalized product × resource requirement table. Calculate Plan from sales quantities × resource norms × monthly planned resource rates. Calculate Fact from actual sales and the resources/capacity actually available in that month; do not substitute planned demand for observed capacity. Derive normative monthly direct cost, resource balance, and utilization by product and resource. Put zero/unknown capacities, rates, and unsupported norms in visible editable assumptions; do not invent them as facts. The manager dashboard must surface overloaded resource-months and maximum utilization.
7. **Adapt source sheets safely.** If operational source sheets remain in use, retain their names or rewrite every dependent formula after redesign. Restyle them as first-class working sheets. Never rename a formula-bearing source sheet and assume references will follow automatically. After moving columns, rewrite dependent `SUMIF`/lookup ranges and verify the full chain from practice resources through costs and allocation.
8. **Design the interface in user order.** Default order: manager dashboard → short “how to work” → catalog → plan → fact → direction summary → resources → product-resource norms → costs → allocation → forecast → resource sufficiency → practice → drivers → controls. Use yellow for editable inputs and green for formulas; hide technical helper columns while keeping their purpose documented.
9. **Make dependencies structural before optimizing formula length.** Use native Excel tables, stable IDs, structured references, and named interfaces for retained matrices. Avoid formulas coupled to row numbers or positional inter-sheet links when the user requires systematic formulas; expose a matrix such as allocation through a small set of named arrays instead of repeating `Sheet!A1` addresses downstream. Split monthly quantity, unit price, revenue, resource demand, direct cost, indirect allocation, and profit into separate stages. Long formulas are acceptable when they express one key-driven rule; readability and resilience to inserted rows outrank an arbitrary character limit.
10. **Verify before delivery.** Run `scripts/audit_xlsx_model.py`, then supplement it with a structured-reference-aware scan: a generic regex may misclassify `tblName[Column]` as an external workbook reference. Require zero literal `#REF!` tokens and obsolete external-book tokens such as `[1]`; verify all required table and defined-name interfaces exist. Reconcile total source costs to allocated totals, check every direction, verify plan volumes roll into summaries, confirm monthly revenue equals monthly quantity × monthly price, and spot-test sensitivity: changing a norm, monthly resource rate, sales quantity, margin, or manual price must change the expected outputs. Verify every active product has a resource-norm row and every direction has at least one resource; test that increasing volume increases demand and can produce a visible capacity deficit. Confirm plan profit follows the agreed identity: revenue minus normative direct resource cost minus allocated out-of-norm indirect expenses. Read the generated workbook back, test its ZIP integrity, keep formulas intact, and force full recalculation on load.

## Standing quality gates

- Plan owns planned quantities and month-specific prices; direction summaries only aggregate them.
- Fact uses the same commercial grain and monthly price structure as plan.
- Allocation is monthly when plan/fact/forecast is monthly.
- Driver names, values, totals, destinations, and allocated sums stay visible.
- Every saleable service maps to one or more resources; sales volumes drive monthly resource demand and a visible sufficiency check.
- Source logic is preserved by meaning even when layout changes.
- No `#REF!`, missing-sheet references, external workbook links, formula parse failures, or unexplained references to blank cells.
- A dashboard must answer: expected revenue, costs, profit, margin, variance to plan, contribution by direction, resource deficits, and peak utilization.
- The final delivery states which values are source facts, formulas, and technical assumptions.

For a reusable workbook layout and allocation design, read `references/model-architecture.md`.