---
name: financial-model-workbook-delivery
description: Use when building formula-driven financial Excel models.
version: 1.0.0
---

# Financial Model Workbook Delivery

## Purpose

Build decision-ready Excel models from partial source workbooks: preserve the source calculation engine, extend it across the complete business perimeter, add plan/fact/forecast, and deliver a formula-driven file that survives input changes.

## Procedure

1. Inventory the source workbook before designing anything.
   - Read every sheet’s dimensions, formulas, named ranges, tables, and charts.
   - Map the economic chain explicitly: source expenses → allocation drivers → business directions/products → units → prices → revenue → P&L/cash flow.
   - Treat a distribution matrix as calculation logic, not as background data.

2. Separate facts, source formulas, and new assumptions.
   - Keep the original sheets under their original names unless every dependent formula is rewritten and verified; renaming can strand formulas on nonexistent sheet names.
   - Preserve source cells and formulas byte-for-meaning where practical, and place extensions on new sheets.
   - Mark unsupported values as editable assumptions. Do not silently promote technical defaults into business facts.

3. Cover the full business perimeter before deepening one direction.
   - Build the common model for every direction present in the allocation or revenue source.
   - Add direction-specific detail, such as consulting project packages, as a drill-down beneath the common model.
   - Never mistake the most detailed source sheet for the complete business scope.

4. Build plan/fact/forecast as distinct contours.
   - Plan: monthly units, prices, revenue, fixed cost, variable cost, profit.
   - Fact: separate monthly inputs for actual units, revenue, and costs.
   - Forecast: fact through a configurable closed-month boundary plus an explicit estimate for future months.
   - Add monthly and annual P&L, cash flow, variance to plan, and a unit-economics view by direction.

5. Keep prices and costs dynamic.
   - Link project price to its driver chain, for example `project hours × current average sales rate`; do not paste the current calculated value.
   - Link project cost to `project hours × current full-cost rate` and calculate target-margin price separately.
   - Distinguish markup from gross margin: `price = cost × (1 + markup)` while `price = cost / (1 - gross margin)`.
   - If a source formula already defines the rate, reference that live formula so team mix, utilization, overhead allocation, and hours flow through automatically.

6. Preserve and expose allocation logic.
   - Carry each cost line through its marker and driver weights to every business direction.
   - Separate fixed and variable cost only through an explicit, editable classification when the source does not define it.
   - Reconcile total source costs, allocated costs, fixed-plus-variable costs, and direction totals.

7. Verify before delivery.
   - Scan formulas for `#REF!`, nonexistent sheets, external workbook references, and parser errors.
   - Distinguish a dangling reference from an intentional blank allocation weight; document blank weights as zero drivers rather than claiming every blank reference is broken.
   - Confirm original sheets still match the source after the extension.
   - Confirm every detailed product uses formulas for hours, rates, cost, and price rather than cached values.
   - Add a visible control sheet and force full recalculation on open.
   - Report formula count and reconciliation results only after reading the generated workbook back.

## User-facing quality rules

- Deliver the working `.xlsx` file directly.
- Explain assumptions that still require business input, especially unit definitions, baseline volumes, fixed/variable split, and forecast factors.
- When corrected, rebuild from the source if the model architecture is wrong; avoid layering patches over a narrowed or reference-broken workbook.
- Keep formula cells visually distinct from inputs and make monthly inputs easy to overwrite.

## Reference

For a reusable model structure, reconciliation equations, and audit checklist, read `references/unit-economics-models.md`.
