---
name: excel-business-model-delivery
description: Use when delivering complex Excel business models.
version: 1.0.0
metadata:
  hermes:
    tags: [excel, financial-model, ux, validation, libreoffice, acceptance]
    related_skills: [xlsx, execution-finalization-discipline, decision-logging]
---

# Excel Business Model Delivery

## Purpose

Use this skill for multi-sheet planning, unit-economics, project, resource, budget, and plan–fact Excel models where formulas, user-owned facts, role-based input, usability, and Microsoft Excel compatibility all matter.

## Standing rules for this user

- Preserve user facts, roles, constraints, and result status exactly. Never replace factual rows with synthetic data or silently delete completed history to make a workbook look cleaner.
- Treat the workbook as a product: calculations, data ownership, user paths, controls, visual legibility, and delivery compatibility are all acceptance criteria.
- Keep one shared calculation model, but separate input surfaces by data owner. Hide technical cores from ordinary users; do not duplicate business logic across role sheets.
- Prefer reversible UX compression over destructive reduction. Show active records by default and retain completed records behind a clear status filter or archive view.
- Use systematic references, named ranges, and formulas. Do not introduce scattered hardcoded cell lists or per-cell duplicated dropdown values.
- Keep the final delivery set small. Work through temporary copies outside the delivery folder and replace the single working artifact only after acceptance checks pass.

## Procedure

1. Establish the source of truth.
   - Identify the user-supplied workbook that owns facts and formulas.
   - Inventory sheets, formulas, array formulas, defined names, validations, hidden rows/columns, protection, filters, external links, charts, and cached values.
   - Record baseline business totals before editing so later UX changes can be proven calculation-neutral.

2. Separate input, calculation, and output layers.
   - Keep role-facing sheets limited to fields each owner supplies.
   - Keep calculation cores hidden and locked.
   - Link façade fields to the calculation layer instead of copying logic into multiple sheets.
   - Unlock only genuine input cells; scan all role sheets for unlocked formulas before delivery.

3. Build user paths before cosmetic styling.
   - Give every role sheet: owner, task, required fields, meaning of colours/asterisks, and next step.
   - Put a numbered end-to-end route on the start sheet.
   - Use internal `HYPERLINK` formulas such as `=HYPERLINK("#'Sheet'!A1","Label")`; verify that saved links contain no local filesystem target.
   - Keep instructions short enough for their merged area. Render and inspect them; row height alone does not prove text is visible.

4. Add controlled input.
   - Use named ranges for products, resources, projects, statuses, periods, and other reference values.
   - Add numeric validation for quantities, months, rates, percentages, calendar hours, and costs.
   - Build active-record dropdowns through a hidden helper list when the full registry is too noisy.
   - For LibreOffice-compatible active lists, assign each active record an ordinal with `COUNTIF`, then populate the helper with ordinary `INDEX/MATCH`. Avoid array-dependent ranking formulas unless they have been recalculated successfully in both target engines.

5. Compact large factual registries without data loss.
   - Derive an explicit calculated status such as `Активный` / `Завершён` from an agreed business field.
   - Apply a default filter to active records and explain how to clear it.
   - Apply the same status to dependent execution rows so role sheets stay consistent.
   - Keep completed rows and their financial contribution intact. Prove this by comparing baseline and final totals.

6. Recalculate with a real spreadsheet engine.
   - Set full recalculation flags before saving.
   - Recalculate through LibreOffice or Microsoft Excel; openpyxl does not evaluate formulas.
   - Treat the recalculated spreadsheet-engine output as the delivery candidate.
   - Do not reserialize worksheet XML after the final spreadsheet-engine save. Generic XML writers can remove Excel extension namespaces and trigger Microsoft Excel Recovery.

7. Run formula and business acceptance checks.
   - Scan cached results for `#VALUE!`, `#N/A`, `#REF!`, `#DIV/0!`, and other formula errors.
   - Verify all workbook control rows are green/`OK`.
   - Verify key reconciliation identities and the exact business totals captured at baseline.
   - Verify active counts, archived counts, visible row counts, and dropdown counts agree.
   - Verify defined names, validations, filters, protection, hidden technical sheets, and absence of external links.
   - ZIP-test the XLSX package and compare the checksum of the spreadsheet-engine candidate with the delivered copy.

8. Run UX acceptance separately from calculation acceptance.
   - Render key sheets to PDF or images and inspect the start page and every role-facing path.
   - Check instruction truncation, header overlap, scale, colour meaning, visible filter state, and whether the next action is obvious.
   - Inspect charts in the actual renderer. A chart object existing in the package does not prove its series render; remove a broken chart rather than ship an empty visual.
   - Remember that print/PDF scaling can make an interactive wide sheet look compressed. Combine rendering with structural checks for zoom, freeze panes, filters, and column widths.

9. Deliver honestly.
   - Copy the direct spreadsheet-engine result into the delivery path without a later XML or openpyxl save.
   - Report verified counts and unchanged totals, not assumed success.
   - If Microsoft Excel is unavailable, state that absence as the single external compatibility check still open; do not claim Recovery-free opening from LibreOffice evidence alone.

## Pitfalls

- Never save a workbook loaded with `data_only=True`; cached values replace formulas.
- Do not use arbitrary first-N-row hiding as a compact view. Filter by a meaningful calculated status so visible rows match the business state.
- Do not delete completed projects to reduce clutter; this corrupts historical fact and dependent PMO/resource totals.
- Do not trust a successful file write as model acceptance. Recalculate, inspect cached errors, compare business totals, and render the user paths.
- Do not equate a Data Validation object with a usable dropdown. Verify its named range, recalculated helper values, visible prompt, and saved formula after LibreOffice.
- Do not leave blank charts because their source table is populated. Verify rendered series; rebuild from direct ranges or remove the chart.
- Do not use a generic XML parser to make final cosmetic edits to XLSX worksheet parts. Namespace loss can make LibreOffice accept a file that Microsoft Excel repairs.

## Verification output

Report at minimum:
- formula-error count;
- non-OK control count;
- unlocked-formula count on input sheets;
- active/archived/visible record counts;
- validation and named-range status;
- external-link count;
- baseline-to-final business-total deltas;
- ZIP test result;
- delivery checksum;
- any remaining Microsoft Excel-only check.

For the detailed reusable acceptance matrix, see `references/acceptance-checklist.md`.
