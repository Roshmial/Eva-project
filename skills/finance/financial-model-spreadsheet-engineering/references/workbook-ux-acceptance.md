# Workbook UX acceptance

Use this after calculations reconcile and before final spreadsheet-engine save.

## First-time-user walkthrough

Test the workbook without relying on model architecture knowledge. Use three distinct artifacts: the clean template, a minimal first-user smoke copy, and the fully filled stress copy; never treat the filled copy as evidence that blank rows are safe.

1. Start from the first sheet and answer in under a minute:
   - What do I fill once?
   - What do I fill for the monthly plan?
   - What do I fill for fact and rolling forecast?
   - Where is the close-month driver?
   - Where are results and errors?
2. Confirm every input sheet states:
   - what the row grain is;
   - which cells are editable;
   - required fields;
   - units;
   - whether zero means no activity or missing data.
3. Confirm recurring shared inputs are visible near the top. Keep technical mirrors hidden and formula-driven.
4. Open the result sheet. Direction/company summaries must appear before project helpers. Collapse technical rows with outline levels rather than deleting traceability.
5. Open controls. Show an overall verdict, failed count and passed count outside the table. The table must explain where to fix a failure.
6. Verify tab classification by ownership: any catalog, normative or master-data sheet that a user must maintain belongs to the input group even if it feeds technical formulas.
7. Confirm every seeded business value is labelled as an assumption to confirm or replace.

## Minimal first-user smoke

1. Copy the clean template; do not use the fully filled fixture.
2. Follow only the navigation and sheet instructions. Change the year, one plan quantity, one calendar month, one rate/headcount and one overhead; add one project and one project-resource row.
3. Leave all other preallocated rows blank. Recalculate in LibreOffice or Excel and scan cached error cells on every sheet, not only visible rows.
4. Verify the entered project reaches an explicit valid status and produces a plausible recognized-revenue, direct-cost and margin result.
5. If blank rows produce `#N/A`, guard dependent formulas with the complete row key before lookup or aggregation. Preserve the original formula unchanged inside the nonblank branch.
6. Keep a small starter block visible and the remaining blank rows outlined; in the synthetic filled copy, unhide rows that the fixture populated.

## Visual rendering pass

Render the recalculated workbook to PDF with LibreOffice and inspect the first page of:

- start/navigation;
- plan input;
- project input;
- resources and calendar;
- management economics;
- controls.

Review:

- cropped instructions and headers;
- text overlap;
- unreadable navigation labels;
- empty technical header rows before results;
- summary cards covering table columns;
- months or totals that appear inconsistent only because later columns are off-screen;
- excessive print pages caused by technical ranges.

A render is evidence of layout, not of calculation correctness. Reconcile suspicious values against cached workbook values before changing formulas.

## Interface rules

- Group tabs visually into input, results, and calculations/checks; keep navigation first.
- Keep the number of operational input tabs small and publish workflow-specific paths instead of asking the user to visit every sheet.
- Use explicit labels in addition to color. Protect formulas and unlock only intended inputs.
- Use full-width instructions with wrapping and adequate row height.
- Separate plan, fact and forecast visibly; show the current close-month context on the start sheet.
- Clarify that annual totals include all 12 months when only part of the horizon is visible in the viewport.
- Use filters, frozen panes, stable ID columns and readable widths on long registries.
- Preserve management-level readability: round displayed values and keep technical precision in formulas.

## Engine-save metadata gate

After LibreOffice or Excel recalculation, recheck:

- tab order and colors;
- hidden/outlined rows and columns;
- hyperlinks;
- charts;
- print areas;
- formula caches and errors.

LibreOffice may strip tab colors and coalesce adjacent hidden columns into one range. Restore presentation-only metadata directly in XLSX XML when needed, then do not resave with openpyxl because that clears fresh cached values.