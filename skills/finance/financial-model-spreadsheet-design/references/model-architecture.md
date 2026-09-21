# Reusable financial-model architecture

## Recommended workbook flow

1. Dashboard: plan, fact YTD, forecast, variance, direction contribution.
2. How to work: four short steps and global forecast parameters.
3. Catalog: product/project ID, direction, focus, scale, unit, pricing model, hours or driver quantity, cost, margin, calculated price, manual override.
4. Plan: catalog dimensions plus monthly volume inputs and calculated annual volume/revenue.
5. Fact: same dimensions and monthly volume inputs; allow actual price override.
6. Directions: source allocated cost, plan volume from Plan, fact volume from Fact, forecast volume, revenue, cost, profit, margin.
7. Costs: source metadata, marker, driver, annual base, monthly plan, monthly fact; retain dynamic links to practice/resource calculations.
8. Allocation: flat monthly journal with scenario selector and eight business columns.
9. Forecast: separate blocks for plan/fact/forecast volume, revenue, cost, and profit.
10. Practice/resources: roles, FTE, utilisation, direct cost, full cost, average rates, and project packages.
11. Driver matrix: explicit zeroes for absent weights; editable driver values highlighted.
12. Controls: source-to-allocation reconciliation, plan-to-summary reconciliation, profit identity, and cash identity when cash flow exists.

## Monthly allocation recipe

For each cost line and month:

1. Read the cost marker.
2. Map the marker to one named driver.
3. Read the cost amount for the selected contour.
4. Read each destination’s driver value and total driver.
5. Calculate allocated amount = amount × driver value / total driver.
6. Suppress rows only when the driver value is explicitly zero; never suppress because a referenced cell is blank.
7. Reconcile monthly and annual allocated totals to the cost inputs.

Direct markers can use a one-to-one driver. Shared management and presale costs should use the source model’s stated cost-base or percentage driver. Hardware or platform pools can use quantities such as demo stands when that is the approved source driver.

## Plan/fact/forecast rule

- Plan: monthly volume × current calculated unit price.
- Fact: actual monthly volume × actual or overridden price.
- Future estimate: plan volume × volume coefficient; plan price × price coefficient; plan cost × cost coefficient.
- Forecast: fact for months up to the close month, future estimate afterwards.

Keep the future estimate separate from the forecast selector. This avoids formulas that both choose the scenario and perform the business calculation.

## Dynamic consulting price

- Full project cost = project hours × average full cost rate.
- Source-style calculated sale price = project hours × average sale rate.
- Target-margin price = full project cost / (1 − target gross margin).
- Manual override, when allowed, must be a separate input and visibly override the calculated price.

Always distinguish markup from gross margin: a 50% markup on cost produces a 33.3% gross margin.