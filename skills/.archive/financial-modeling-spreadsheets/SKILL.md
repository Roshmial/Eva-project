---
name: financial-modeling-spreadsheets
description: Use when building or repairing Excel financial models.
version: 1.0.0
metadata:
  hermes:
    tags: [finance, excel, unit-economics, planning, forecasting]
    category: finance
    related_skills: [xlsx]
---

# Financial Modeling Spreadsheets

Build auditable Excel models whose business logic remains traceable from source inputs through allocations to outputs.

## Procedure

1. **Audit the source before designing.** Inventory sheets, formulas, names, units, drivers, allocation matrices, and existing product or revenue logic. Treat a workbook with several business lines as a portfolio model; do not optimize one line while silently omitting the others.
2. **Preserve the calculation kernel.** Keep source sheet names, formulas, and allocation drivers unchanged unless the user explicitly approves a migration. Build new model sheets around that kernel. Renaming a source sheet without rewriting every dependent formula creates live-looking links that point nowhere.
3. **Map every business line and unit.** Create a direction register with unit, baseline volume, allocated fixed cost, allocated variable cost, unit cost, price, and margin. Mark technical placeholders as assumptions; never present them as facts.
4. **Separate Plan, Fact, Future Estimate, and Forecast.** Plan is editable monthly intent. Fact is a separate monthly input. Future Estimate applies transparent volume, price, and cost drivers. Forecast only selects Fact for closed months and Future Estimate for open months. Keep the cutoff month explicit and visible.
5. **Lock price semantics before writing formulas.** Decide whether price is transaction-level, monthly, or an annual weighted average; do not mix these grains. For an annual-average model, calculate Plan from annual normative direct cost plus allocated overhead, divided by annual volume and adjusted for target margin; calculate Fact selling price as actual annual revenue divided by actual annual volume. Keep actual cost per unit separately as allocated actual cost divided by actual volume, then calculate actual margin from selling price and unit cost. A project price derived from hours must reference current hours and rates; never copy cached prices from a source workbook.
6. **Preserve allocation lineage and the user's allocation surface.** Treat the supplied allocation matrix as both calculation logic and a user-facing working register. Remove or repair a corrupt native Excel Table object without deleting, compacting, or replacing the visible allocation matrix unless the user explicitly approves a redesign. Allocate each cost row through its source marker and driver matrix, then reconcile both the grand total and every business-line total to the source. Keep fixed/variable shares editable when the source does not define cost behavior.
7. **Optimize formulas for auditability.** One formula should perform one conceptual step. Split selection logic from calculation logic; use helper blocks rather than one long formula that selects a period and computes several business stages. Prefer `SUMIFS`/`SUMIF`, structured tables, stable business keys, and short arithmetic. Avoid positional cross-sheet links when rows can move; never create a model that depends on hard-coded row numbers throughout the workbook.
8. **Use an RCM chain for service economics when resources drive cost.** Make the dependency explicit: sales volume → resource norm per service → required resources → monthly resource rate → cost register → allocation → service cost → price/revenue/profit → summary/dashboard. Plan resource cost comes from planned sales and normative demand at the rate of the corresponding month. Fact unit-resource cost comes from actual resource expense divided by actual available/used capacity in that month, then applies to actual sales. Keep a calculated annual-average rate only as a summary; never use it where monthly rates can change. Keep implementation, support, and consulting teams confined to their project services unless the catalog explicitly bundles them into a license. Model fixed platform or license-family pools as allocations independent of units sold when the business rule says they are not direct license costs.
9. **Build compact management surfaces.** Put months in columns and products/resources/metrics in rows unless a long register is specifically needed for machine processing. Do not expose tens of thousands of technical rows as the primary interface; keep calculation sheets compact enough for a manager to inspect. Split aggregate project teams into role-level resources when staffing sufficiency or role rates matter.
10. **Build outputs after the engine.** Include monthly P&L, cash flow, resource sufficiency, unit economics, break-even metrics, and a control sheet. Distinguish markup from gross margin: price at target gross margin is `cost / (1 - margin)`. Treat development capacity as overhead unless the user explicitly identifies it as a direct service resource; treat product licenses as their own resource unit.
11. **Audit the entire dependency graph before delivery.** For every sheet, identify upstream sources and downstream consumers. Input catalogs may have no incoming links; instructions need no calculation links; every calculation sheet must feed a later calculation or control. Confirm specifically that the cost sheet feeds allocation and allocation feeds service economics—an allocation sheet that is merely calculated but never consumed is disconnected.
12. **Verify structurally, economically, and as an Open XML package.** Check nonexistent sheets, external links, `#REF!`, formula parser errors, source-sheet differences, formula complexity, price chains, resource sufficiency, and allocation reconciliation. Validate at least one end-to-end example independently and run sensitivity checks in which changing one month's resource rate affects that month plus annual aggregates, not unrelated months. Inspect the `.xlsx` ZIP for `xl/tables/table*.xml`, worksheet `tableParts`, and `xl/externalLinks`: a workbook can load in `openpyxl` and still trigger Excel repair. When native tables are retained, require every table `ref` to match its `autoFilter.ref`, headers, relationships, and actual range. If Excel has already reported table/formula repair, prefer ordinary formatted ranges and convert all structured references before removing table parts; remove stale external-link components and re-read the saved package. Formula-token parsing and ZIP integrity prove structure only; they do not prove that Excel evaluated formulas. If no spreadsheet calculation engine is available, clearly separate structural verification from calculation verification.
13. **Deliver assumptions visibly.** Use a consistent convention such as yellow inputs and green formulas. Mark non-applicable resource/service pairs as “not used,” not “missing.” Explain which resource norms, role shares, capacities, rates, payment lags, and scenario factors require owner validation.

## Formula quality gates

- No references to nonexistent sheets or external workbooks unless explicitly required.
- No copied values where a source-derived dynamic formula is expected.
- No formula should mix source selection with a multi-step business calculation when a helper row or sheet makes the chain clearer.
- Treat references to intentionally blank allocation weights as zero-driver positions; distinguish them from broken addresses.
- Reconcile total costs to total allocated costs and total allocated costs to costs consumed by service economics.
- Check that every service uses only its approved direct resources; license products must not silently absorb implementation, support, consulting, or development teams.
- Compare formula length, nesting, visible row count, and sheet dimensions before and after optimization; optimize for manager readability as well as technical correctness.
- Open or recalculate the workbook with a real spreadsheet engine before claiming that output sheets are populated; `openpyxl` writes formulas but does not calculate them.
- A repair operation must preserve the visible business register: deleting native table XML is not permission to delete the allocation matrix or its filters, frozen panes, styles, driver inputs, and plan/fact output blocks.
- After removing sales-price rows from a volume sheet, rewrite every dependent range and move the surviving price/revenue input to an explicit owner sheet; physically delete obsolete rows so the interface does not retain a misleading blank tail.

For a detailed workbook architecture and verification checklist, read `references/model-architecture-and-audit.md`.
