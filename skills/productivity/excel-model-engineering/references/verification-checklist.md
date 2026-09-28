# Verification checklist for complex XLSX models

Use this after the final spreadsheet-engine save, on the exact file to be delivered.

## Package and compatibility

- ZIP test passes.
- Workbook opens and saves through a real spreadsheet engine.
- No external-link parts unless explicitly required.
- No worksheet XML is rewritten after the engine save.
- Delivery-file hash equals the engine-candidate hash.
- Record whether desktop Microsoft Excel was actually tested.

## Formula and control checks

- Cached formula errors: 0 across every sheet, including hidden cores.
- `#REF!` literals: 0.
- Control rows: all `OK`, or every non-OK row is explicitly expected and explained.
- Formula count and maximum formula length are plausible after restructuring.
- Empty preallocated rows do not produce lookup errors.

## Data preservation

Compare authoritative source inputs with final role surfaces:

- product catalog and norms;
- sales plan;
- contracts;
- project-resource facts and forecasts;
- resource directory and calendar;
- plan/fact rates and headcount;
- overheads.

Mismatch count must be zero unless a requested migration intentionally transforms a field. Compare formulas separately from user data.

## Resource planning

- Visible planned capacity equals calculated required capacity in every month/resource cell.
- People and discrete-resource counts are whole numbers.
- Full pool = allocated direct cost + unallocated pool within tolerance.
- Zero-direct-cost resources are excluded through an explicit configurable attribute.

## UX and role surfaces

- Every input sheet states owner and update cadence.
- Formula cells unlocked for editing: 0.
- Intended input cells are unlocked and visually marked.
- Defined names and Data Validation rules survive the engine save.
- Product/resource/project dropdown sources resolve to nonempty ranges.
- Filters, freeze panes, instructions, and required-field markers are readable.
- Run a minimal first-user scenario through all input classes.

## Financial invariants

Compare before/after totals at minimum:

- contract value;
- recognized revenue to date;
- direct cost;
- current margin;
- remaining revenue forecast;
- fact plus forecast versus contract.

Unless business logic intentionally changed, deltas must be zero.
