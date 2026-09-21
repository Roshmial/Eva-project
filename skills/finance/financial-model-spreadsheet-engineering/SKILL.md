---
name: financial-model-spreadsheet-engineering
description: Use when building or repairing Excel financial models.
---

# Financial-model spreadsheet engineering

## Outcome

Deliver a working, auditable Excel model whose units, calculation layers, resource economics, revenue recognition and P&L reconcile. Preserve the user's compact workbook structure and make each management calculation traceable to a visible detail layer.

## Procedure

1. Inventory the workbook before editing.
   - Record sheets, dimensions, input ranges, calculated ranges, protection, validations, charts, tables, external links and formula errors.
   - Identify the unit of every resource field: hours, people, FTE-equivalent, discrete units or money. Never compare fields until their units match.
   - Treat the measure name as part of every lookup key. Before trusting `SUMIFS`, prove that the criteria select exactly one measure; criteria such as `scenario + resource_id` are unsafe when rate, availability, effective rate and cost share the same labels.
   - Locate the formulas that feed the reported symptom and trace them back to the smallest source rows.

2. Reproduce the error with one minimal business scenario.
   - Zero unrelated inputs in a temporary copy.
   - Use one product, one resource, one start month and one contract where possible.
   - State the expected result from the normative before changing formulas; for a 33.6-hour norm and a one-third monthly profile, the expected monthly need is 11.2 hours.
   - Evaluate the actual workbook formulas in a spreadsheet engine or an independent formula evaluator. A handwritten calculation alone is not sufficient verification.

3. Replace opaque aggregate formulas with a visible calculation layer.
   - For plan resource demand, use one row per `product type × resource`, monthly project starts, monthly profiles and calendar-month demand.
   - Add monthly direct-cost columns to that same visible detail layer: human hours use the month's effective hourly cost; licenses and equipment use quantity times unit rate.
   - Aggregate demand by resource and monetary cost by direction from this prepared layer with bounded `SUMIFS`; do not reconstruct money in a summary by searching a mixed-purpose resource sheet.
   - Avoid `SUMPRODUCT` wrapped around `SUMIFS` with an array criterion; spreadsheet engines can aggregate the criteria array differently and multiply demand.
   - Keep months in columns and use ordinary formatted ranges when native Excel tables have caused repair reports.

4. Separate resource concepts explicitly.
   - Input human-resource availability in whole people when the staffing decision is headcount; do not label hours as people or FTE.
   - Store one production-calendar row of working hours per person for every month and use it across the whole team. Add role-specific effective-capacity adjustments only as separate, explicit drivers when the business has agreed them; do not duplicate the production calendar by role. Never hard-code one annual average such as 168 into monthly staffing formulas.
   - Calculate demand in hours, required people as `CEILING(hours / monthly_capacity[m], 1)`, available capacity as `people × monthly_capacity[m]`, deficit as `MAX(required people - available people, 0)`, surplus as `MAX(available people - required people, 0)`, reserve hours as `MAX(available capacity - demand hours, 0)`, and utilization as `demand hours / available capacity`.
   - Treat a whole-person surplus in plan as a planning error. Treat residual hours inside the minimum rounded headcount as normal rounding reserve.
   - Keep the full cost of available surplus capacity in the resource pool. Do not allocate idle-capacity cost to projects; carry it as an unallocated pool that reduces company P&L.
   - Never derive available headcount from demand in a way that hides shortages. Required people and available people must remain separate fields.

5. Model rates and cost allocation by economic unit.
   - For salaried people, input the monthly cost of one person, not an hourly rate. Calculate `effective_hourly_cost[m] = person_month_cost[m] / monthly_capacity[m]`.
   - Calculate project direct labor cost as consumed hours times that effective hourly cost; calculate the full staff pool as paid people times person-month cost. Changing calendar hours must change the allocation rate without multiplying the monthly salary itself.
   - For licenses and equipment, retain quantity times unit rate. Verify at least one exact case such as `37 × 0.7 = 25.9`; a materially larger result usually means availability or another measure was accidentally summed with the rate.
   - Assign every resource to a cost center when direction-level economics are required. Keep direct project cost on projects and carry idle-capacity cost as an indirect direction cost before company overhead.

6. Keep revenue, margin and hour economics separate.
   - Contract revenue is fixed: for every project, `recognized_actual_to_date + forecast_recognition = contract_amount`. Costs determine the timing weights and margin, but may be lower or higher than revenue and must never change the full contract revenue.
   - Preserve three monthly layers for sold projects: baseline, closed-period actual and open-period forecast. Use one close-month driver; allow forecast overrides without overwriting baseline.
   - Build planned recognized revenue first at product/cohort level, normalize the visible timing profile to the full sale amount, then aggregate prepared values to directions with bounded `SUMIFS`.
   - Keep actual-to-date recognition distinct from full rolling revenue. Allocate the contract across rolling monthly costs; show the unrecognized remainder as forecast recognition.
   - For costless products, use an explicit catalog rule such as recognition at sale. Match stable rule codes or a deliberate prefix, not an exact display phrase that may contain an explanation.
   - Show sold hours, actual hours, hour variance, planned revenue per sold hour, recognized revenue per actual hour, margin per actual hour and margin percentage.
   - Let overruns reduce margin and per-hour economics; never increase contract revenue merely because more hours were consumed.

7. Preserve model usability while editing.
   - Organize tabs into three visible groups: data entry, results, and calculations/checks. Use stable ordering, tab colors and a start sheet with links; keep the start/dashboard first even when results are otherwise grouped together.
   - Classify sheets by editing ownership, not by how formulas use them: catalogs, resource masters and normative profiles are input sheets whenever a user must confirm or maintain them; reserve the technical group for sheets with no routine manual entry.
   - Do not make users enter small pieces on every sheet. Publish workflow paths such as initial setup, monthly plan, and monthly fact/rolling forecast, and state which input tabs each path requires.
   - Mark every seeded plan, rate, capacity, price or overhead value as a working assumption that must be confirmed or replaced; a prefilled template must not visually imply that unverified values are actual business data.
   - Walk the workbook as a first-time user before delivery: identify where to start, which fields are mandatory, which values are automatic, how to enter a monthly cycle, where to see the result, and how to know the model passed controls. If any answer requires knowledge of hidden architecture, fix the interface rather than adding a long explanation.
   - Keep yellow cells for input, green or neutral cells for calculations and red for errors/deficits. Put concise “what to fill and when” instructions at the top of every input sheet; mark required fields and explain accepted units and zero semantics.
   - Put globally shared drivers such as the production calendar in the first visible input area, even when formulas consume a hidden technical mirror. Do not force users to scroll through hundreds of rows to reach a recurring input.
   - On mixed input/calculation sheets, collapse or hide technical rows and output columns while keeping them recoverable with outline controls. Never hide user inputs, key identifiers, or error indicators. A result sheet must open on direction/company summaries, not thousands of project-helper rows.
   - For preallocated input registries, show only a small usable starter block and outline the remaining blank rows. Guard every dependent formula with the row's required keys so blank rows return a deliberate empty/zero result instead of `#N/A`; expand all populated rows in the synthetic filled copy.
   - Give the control sheet an explicit overall verdict and counts of passed/failed checks in reserved space outside the control table. Never overlay a summary card on table columns; round numerical residue to the stated tolerance for display.
   - Add navigation entries and concise descriptions for every new calculation block. Make in-sheet navigation labels wide enough to read without truncation. Deduplicate repeated control rows after iterative repairs; keep the newest correct formula for each named check.
   - Render the workbook after interface changes and inspect at least the start sheet, one plan input, project input, resources, management results and controls. Use the render to detect cropped instructions, empty technical headers, overlays and unusable print scaling, but verify suspected numeric inconsistencies against the workbook because a first-page render may omit later months.
   - Use bounded formulas, no external links, no `#REF!`, and no hidden hard-coded business results.
   - Keep formulas locked and user inputs unlocked; validate headcount and discrete units as whole non-negative numbers.

8. Verify in layers before delivery.
   - Structural: ZIP integrity, no external links, no `#REF!`, formula-token parsing, expected sheets, validation counts, protection and chart preservation.
   - Reconciliation: full pool equals allocated plus unallocated cost; product-detail direct cost equals the resource layer and direction totals; planned sales equal planned recognized revenue; actual-to-date plus forecast recognition equals every contract; project and direction actual recognition totals match.
   - Behavioral: run isolated deficit and surplus scenarios, an isolated plan-demand convolution, a zero-cost product, a discrete-resource exact case and a revenue-per-hour overrun scenario.
   - First-user smoke: from a fresh template, change one representative value in each advertised workflow, add one project and one project-resource row, leave the rest of every preallocated registry blank, then recalculate and scan every sheet for cached formula errors. Confirm the new project's status and at least one revenue/cost/margin output. This scenario is mandatory because a fully filled fixture can mask blank-row `MATCH`/`INDEX` errors.
   - Filled-model: regenerate the synthetic test workbook from the corrected template, then rerun the independent audit. Do not reuse a filled workbook created from the old formulas.
   - Engine: recalculate the clean template, minimal first-user smoke and filled workbook in LibreOffice Calc or Excel, save to a separate output directory, inspect cached values and formula errors on every sheet, and only then replace deliverables. A parser or independent Python model validates structure and logic but does not prove spreadsheet-engine execution.
   - For large books that time out in `openpyxl(data_only=True)`, read cached `<v>` values and error cells directly from worksheet XML inside the XLSX ZIP. Resolve shared-string indices before interpreting labels.
   - Re-audit usability metadata after engine save: sheet order, tab colors, outline/hidden ranges, hyperlinks and charts. LibreOffice can strip tab colors and coalesce hidden columns into one range. Restore presentation-only XML metadata directly after recalculation when necessary; do not resave through openpyxl afterward because it clears fresh formula caches.
   - Interpret controls by their contract: numeric deviations pass within tolerance, count controls pass at zero, and status controls pass at `OK`. Do not label every non-`OK` cell as a failure.
   - Report actual scenario outputs and deliver both the clean template and explicitly marked synthetic test copy.

## Gates

- Do not call a model corrected merely because formulas parse; verify expected numeric behavior through the workbook formulas.
- Do not accept a test harness failure as a workbook failure until checking whether the harness still assumes the old sheet count, units or layout.
- When the model architecture changes, update fixture generators and audit scripts in the same change; stale tests otherwise validate the wrong unit system.
- Do not infer field semantics from a remembered column letter. Read the current headers or master-data schema before writing formulas; unit, resource type and resource name often occupy adjacent columns and a one-column drift can multiply costs or invalidate controls. Prefer generating type-specific formulas from master data over formulas that rediscover type from a display column.
- Whenever a direction summary is needed, add an explicit direction helper to project rows or aggregate from a prepared detail layer. Do not compare a direction name with a project ID column.
- Keep control ranges synchronized with all direction rows and remove or repair duplicated stale controls after repeated edits.
- Add a dimensional-collision test whenever summary formulas use shared labels: changing availability must not change a rate, and changing a rate must not change resource quantity.
- Test monthly capacity with at least two different month values so a hidden fixed-capacity reference cannot pass.
- If manual project-cost overrides can exceed the calculated pool, enlarge or explicitly override the pool before allocating; otherwise the pool reconciliation breaks.

## References

- See `references/resource-and-revenue-economics.md` for reusable equations and boundary scenarios.
- See `references/workbook-ux-acceptance.md` for the first-time-user walkthrough, visual rendering pass and interface acceptance checklist.