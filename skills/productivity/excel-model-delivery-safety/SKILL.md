---
name: excel-model-delivery-safety
description: Use when delivering complex Excel models to Misha.
---

# Excel model delivery safety

## Delivery rules

- Treat Microsoft Excel compatibility as the acceptance target when the user will open the workbook in Excel. A successful LibreOffice recalculation and ZIP integrity check are necessary but insufficient.
- Never reserialize complete worksheet XML with generic XML libraries for cosmetic edits. This can remove Excel namespaces such as `x14`, `xr2`, `mc`, and `xdr`, causing Excel to replace worksheet components even though LibreOffice still opens the file.
- After the final tabular-engine save, do not apply direct worksheet XML rewrites. Prefer losing cosmetic tab colors over risking workbook repair.
- Preserve a clean pre-cosmetic engine-saved artifact and compare hashes before delivery.
- Validate formulas after a real recalculation, verify no `#REF!`, `#N/A`, or `#VALUE!`, and confirm user-input data against the authoritative source workbook.
- For role-based multi-user models, separate visible input surfaces by data owner and keep complex calculation sheets hidden. Use numeric zero for blank numeric links and empty text only for identifiers/text fields; empty strings in arithmetic may create `#VALUE!`.
- When repairing a user-provided reference workbook, treat it as authoritative for user data. Restore formulas from a compatible donor only after proving sheet/row alignment and preserving every non-formula input value.
- If desktop Microsoft Excel is unavailable, state that limitation explicitly and ask for the Excel repair report after the user's first open. Do not claim Excel compatibility solely from LibreOffice tests.
