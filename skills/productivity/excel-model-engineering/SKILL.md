---
name: excel-model-engineering
description: Use when complex Excel models need safe repair or redesign.
---

# Excel Model Engineering

Use this for formula-heavy planning, resource, and financial models where correctness, user-entered facts, role-based input, and Microsoft Excel compatibility matter more than cosmetic polish. Use the general `xlsx` skill for basic mechanics; this skill governs the end-to-end engineering workflow.

## Non-negotiable gates

- Treat the user's supplied workbook as the source of truth for all inputs and facts. Never replace it with synthetic data or an earlier generated workbook.
- Preserve user values exactly. Formula restoration may replace calculation cells, but it must not alter contracts, project facts, resource usage, rates, headcount, calendars, sales, or overhead inputs.
- Keep demonstration values only in a separately and unmistakably labelled test artifact. Remove stale synthetic deliverables when they can be mistaken for facts.
- Never claim Microsoft Excel repair errors are resolved from ZIP validity or LibreOffice alone. Deliver a direct spreadsheet-engine output and ask for an actual Excel open test when Excel is unavailable.
- After a workbook has produced an Excel repair report, do not use native Excel Tables or full XML reserialization unless desktop Excel validates the result.

## Procedure

### 1. Freeze the authoritative input

1. Copy the supplied workbook to a temporary working path; leave the original unchanged.
2. Run ZIP integrity, workbook inventory, external-link inventory, formula count, and literal error scans.
3. Recalculate an untouched copy with a real spreadsheet engine and scan cached values for `#REF!`, `#N/A`, `#VALUE!`, and other formula errors.
4. Inventory user-input ranges separately from calculated ranges. Use protection, formula presence, headers, and business semantics together; do not infer inputs from cell color alone.

### 2. Diagnose lost formulas before editing

1. Count formulas by sheet, range, and column. A column with hundreds of values but one remaining formula is usually a damaged calculated column.
2. If a known-good donor exists with the same layout, build a formula mask from the donor and copy only donor formula cells into the authoritative workbook.
3. Compare every donor non-formula position before and after restoration; the mismatch count must be zero.
4. Handle array formulas by semantic content (`text` and `ref`), not object identity.
5. Verify technical lookup layers as well as headline formulas. If restored formulas point to missing or shifted technical rows, copy the complete technical block only after proving it contains no user inputs.
6. Recalculate immediately. Do not accept a large formula transplant merely because formula count increased; cached errors must be zero.

### 3. Separate role inputs without rewriting the calculation model

Prefer input façades linked to a hidden calculation core when existing sheets mix owners or contain fragile formulas.

1. Identify owners by source: product configuration, sales plan, contracts, PMO execution, resource capacity, finance rates, overheads, results, checks.
2. Create one clear input surface per owner. A user should normally edit one or two sheets only.
3. Preserve the original complex sheets as hidden calculation cores.
4. Link core input cells to façade cells. Return `0` for blank numeric fields and `""` for blank identifiers/text; text empties in arithmetic cause `#VALUE!` cascades.
5. Lock linked core cells and all formulas. Unlock and visually mark only user-input cells.
6. Keep traceability: each façade instruction names its owner, update frequency, required fields, and downstream check sheet.
7. For simultaneous users, require SharePoint/OneDrive or another coauthoring platform; an ordinary network-file XLSX is not a safe concurrency mechanism.

### 4. Make first-time filling safe

1. Walk the workbook as a new user from the start sheet. Do not rely on knowledge gained while building it.
2. Run a minimal smoke scenario that changes one value in every input class: period, plan, contract, project resource, monthly fact, calendar, rate/headcount, and overhead.
3. Recalculate the smoke copy and inspect the resulting project status, revenue, direct cost, margin, and controls.
4. Guard all preallocated blank detail rows by their key IDs. Empty project-resource rows must return zero/blank instead of lookup errors.
5. Collapse unused preallocated rows in the template; expand populated rows in the labelled test version.
6. State clearly whether prefilled values are confirmed data or working assumptions.

### 5. Add robust reference choices

1. Use standard Data Validation and workbook defined names for cross-sheet lists; e.g. product, resource, and project IDs.
2. Do not use direct cross-sheet Data Validation ranges when Excel compatibility matters; named ranges are more reliable.
3. Add static lists for stable categories such as month, size, type, scenario, and yes/no.
4. Add numeric validation for nonnegative values, integers, percentages, durations, and closed periods.
5. Protect formula cells and assert there are zero unlocked formula cells across user sheets.
6. Explain that Excel displays the dropdown arrow only when the cell is selected.

### 6. Derive resource capacity from demand

- Default planned capacity from sales-driven demand and product norms, rather than independent manual entry.
- For people, use `CEILING(required hours / production-calendar hours)` per month.
- For licenses/equipment, round required units upward to whole units.
- Document this rule on the detailed resource-plan sheet and the resource input sheet.
- Compare every visible planned-capacity value to its detailed required value; maximum delta must be zero and fractional plan counts must be zero.
- Make inclusion in direct costs an explicit resource attribute instead of hardcoding a product/resource ID. This keeps zero-direct-cost licenses configurable while preserving entered rates.

### 7. Verify three separate states

Before delivery, independently prove:

1. **Calculation state:** zero cached formula errors after spreadsheet-engine recalculation; all control rows are `OK` or an explicitly documented expected warning.
2. **Data state:** all authoritative input ranges match the source; key financial totals before and after restructuring have zero delta unless the requested rule intentionally changes them.
3. **UX state:** role sheets have readable instructions, filters/freeze panes, protected formulas, unlocked inputs, and preserved validations/defined names after recalculation.

Use direct XLSX XML reads for large cached-result comparisons when loading multiple large workbooks with openpyxl is too slow.

### 8. Deliver without re-corrupting the workbook

1. Save through LibreOffice or Excel and treat that engine-produced file as the delivery candidate.
2. Do not subsequently parse and serialize whole worksheet XML files with generic XML libraries for cosmetic changes. Spreadsheet namespaces and compatibility metadata such as `mc`, `x14`, `xr2`, or drawing namespaces can be dropped even though LibreOffice still opens the file; Microsoft Excel may then replace entire sheet parts.
3. If cosmetic tab colors are lost during recalculation, accept the cosmetic loss rather than postprocess worksheet XML.
4. Copy the engine-produced file byte-for-byte to the delivery path, run ZIP and cached-error checks, and compare hashes of source candidate and delivered file.
5. Report the exact validation boundary: LibreOffice verified, Microsoft Excel verified, or Microsoft Excel verification still required.

## Durable pitfalls

- Never save a workbook loaded with `data_only=True`; formulas are discarded.
- Do not equate `restart`, `ZIP OK`, or `LibreOffice opens` with completed Excel compatibility verification.
- Do not copy all donor cells during formula repair; donor inputs overwrite authoritative facts.
- Do not treat `0`, blank, and missing lookup keys as interchangeable. Numeric links should default to zero; IDs and labels should remain blank.
- Do not keep an input sheet unprotected simply because its source workbook had no protection. Explicitly lock formulas and unlock the intended input ranges.
- Do not infer a resource's cost treatment from a special ID when it can be a configurable yes/no attribute.
- Do not accept a control sheet with one unexplained warning. Trace the balance by month and resource until the unmatched component is identified.

## Delivery format for this user

Lead with what was found and fixed. Then report concrete verification: formula-error count, control status, data mismatch count, key financial deltas, plan-capacity delta, defined names/validation coverage, external links, and the spreadsheet engine used. Keep caveats explicit and attach the working file directly.

See `references/verification-checklist.md` for the final delivery gate.
