# Acceptance checklist for complex Excel business models

## Data preservation

- Identify the source-of-truth workbook.
- Capture key totals before editing.
- Confirm that factual row identifiers are preserved.
- Confirm that completed/archived records remain in the workbook.
- Compare key totals before and after UX-only changes; expected delta is zero.

## Calculation integrity

- Recalculate in LibreOffice or Microsoft Excel.
- Scan cached cell values for Excel error tokens.
- Confirm all control rows are `OK`.
- Confirm important reconciliation formulas independently from cached values.
- Confirm plan-capacity or allocation identities at row/month level, not only as a grand total.

## Input safety

- List every role-facing input sheet.
- Confirm sheet protection is enabled.
- Confirm intended input cells are unlocked.
- Confirm no formulas are unlocked.
- Confirm numeric limits and list validations cover the intended ranges.
- Confirm named-range dropdowns still exist after spreadsheet-engine recalculation.

## Compact registry UX

- Count all, active, completed, and dependent detail rows.
- Confirm the default filter exposes only active records.
- Confirm clearing the status filter reveals archived records.
- Confirm dependent sheets use the same status semantics.
- Confirm the active-record dropdown contains exactly the active identifiers.

## Navigation and clarity

- Verify every start-page destination exists.
- Verify links are internal and do not include a local file path.
- Verify each input sheet states owner, action, required fields, and next step.
- Render key sheets and inspect text clipping, merged-area overflow, header overlap, and visible filter cues.
- Treat print/PDF review and interactive worksheet review as complementary checks.

## Package and delivery

- Confirm there are no external workbook links.
- Test the XLSX as a ZIP package.
- Avoid any XML rewrite after the final LibreOffice/Excel save.
- Copy the spreadsheet-engine result directly to the delivery path.
- Confirm source and delivery checksums match.
- If Microsoft Excel was not available, explicitly leave Recovery-free opening as an external verification item.
