# Unit-economics workbook pattern

## Recommended sheet structure

1. `00_Инструкция`: model purpose, color legend, missing inputs, update sequence.
2. `01_Параметры`: year, closed month, payment delays, opening cash, pricing mode, target margin.
3. `02_Направления`: unit definition, baseline volume, source allocated cost, fixed/variable split, plan price, forecast factors.
4. `03_Аллокация`: source cost lines, marker, variable share, driver-based allocation by direction, reconciliation totals.
5. `04_План`: monthly units, revenue, cost, and profit by direction.
6. `05_Факт`: separate monthly input blocks for units, revenue, and cost.
7. `06_Прогноз`: fact for closed months and forecast formulas for future months.
8. `07_P&L`: monthly and annual plan/fact/forecast with variance.
9. `08_Денежный поток`: collections and payments shifted by their delays.
10. `09_Юнит-экономика`: full cost per unit, variable cost, contribution, gross margin, break-even volume.
11. Direction drill-down sheets, such as consulting project packages.
12. `Контроль`: visible reconciliation checks.
13. Original source sheets, unchanged and under their original names.

## Core formulas

- Allocated line cost to direction: `line cost × direction driver / total driver`.
- Variable allocated cost: `allocated cost × variable share`.
- Fixed allocated cost: `allocated cost × (1 - variable share)`.
- Variable cost per unit: `annual variable allocated cost / baseline units`.
- Plan monthly cost: `annual fixed allocated cost / 12 + monthly units × variable cost per unit`.
- Target-margin price: `full unit cost / (1 - target gross margin)`.
- Project calculated price: `project hours × average sales rate`.
- Project full cost: `project hours × average full-cost rate`.
- Break-even units: `fixed cost / (unit price - variable cost per unit)`.
- Forecast month: `actual` when month ≤ closed month; otherwise `planned value × forecast factor` or a dedicated future estimate.

## Minimum controls

- Source expense total = allocated line total.
- Sum across directions = allocated line total.
- Fixed + variable = allocated total.
- Direction allocation total = source direction total.
- Baseline-volume plan cost = source allocated cost.
- Revenue − cost = profit.
- Opening cash + collections − payments = ending cash.
- Every formula-referenced sheet exists.
- No external workbook links unless explicitly intended.
- No `#REF!` tokens or formula parse errors.
- Original source sheet values and formulas match the input workbook.
- Detailed product prices reference live hours and live rates.

## Blank-driver interpretation

A blank weight inside a sparse allocation matrix usually means zero participation, not a missing destination. Keep this distinction in the audit report. If blanks are intentional, either retain the source matrix unchanged or normalize them to zero only in a derived calculation layer; do not mutate the protected source solely to silence an audit count.
