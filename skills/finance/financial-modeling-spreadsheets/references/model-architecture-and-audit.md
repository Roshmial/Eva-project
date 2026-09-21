# Model architecture and audit

## Recommended workbook layers

1. Instructions and conventions.
2. Model controls: year, closed month, payment lags, pricing mode, target margin.
3. Business-line register: units, baseline volume, allocated fixed and variable costs, prices, forecast factors.
4. Source allocation view: cost rows, markers, driver weights, allocation by business line, reconciliation.
5. Monthly Plan inputs.
6. Monthly Fact inputs.
7. Future Estimate: plan adjusted by volume, price, and cost assumptions.
8. Forecast: Fact through cutoff plus Future Estimate thereafter.
9. P&L and cash flow.
10. Unit economics and break-even.
11. Product-level detail for lines that need it.
12. Control sheet.
13. Original source sheets, unchanged and under their original names.

## Formula simplification pattern

Avoid a single forecast-cost formula that simultaneously:

- checks whether the month is closed;
- selects Fact or Plan;
- calculates fixed cost;
- calculates variable cost from volume;
- applies a cost scenario factor.

Use three steps:

1. Future volume = Plan volume × volume factor.
2. Future cost = monthly fixed cost + Future volume × variable unit cost, then apply the cost factor.
3. Forecast cost = Fact cost when the month is closed; otherwise Future cost.

Use a visible row such as `Источник месяца` with `Факт` or `Оценка` so reviewers can trace the selection without reading every formula.

For cash flow, separate accrued revenue/cost, delayed receipts/payments, opening cash, net cash flow, and closing cash. Each row should have one role.

## Dynamic project pricing

For hours-based consulting or delivery packages:

- Project hours should link to the current resource or package estimate.
- Calculated selling price = project hours × average selling rate.
- Full project cost = project hours × average full cost rate.
- Target-margin price = full project cost / (1 - target gross margin).
- Gross margin = (price - full cost) / price.

If the source uses a markup, label it as markup. A 50% markup yields a 33.3% gross margin.

## Verification checklist

- Source sheet names preserved.
- Source values and formulas compared cell-by-cell with the original.
- All referenced sheet names exist.
- No external workbook links unless approved.
- No `#REF!` tokens or formula parse failures.
- Dynamic price formulas present for every product row.
- Allocated grand total equals source cost total.
- Allocated totals by business line equal the source allocation result.
- Plan at baseline volumes reproduces baseline costs.
- Forecast equals Plan when cutoff is zero and forecast factors are 100%.
- Cash closing balance equals opening balance plus cumulative net cash flow.
- Formula length and nesting measured; long mixed-purpose formulas split into helper calculations.
- Full recalculation on open enabled when no spreadsheet engine is available during generation.
