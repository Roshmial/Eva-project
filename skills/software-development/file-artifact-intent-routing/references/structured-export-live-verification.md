# Structured export live verification

Use when a file/export flow looks "green" at transport level but may still be wrong semantically.

## Why this matters

For export features, these signals are necessary but not sufficient:
- HTTP `200`
- non-empty file bytes
- expected MIME type
- expected extension
- even a plausible slide/sheet count

A structured export can still be wrong if:
- `CSV/XLSX` contains only fallback text instead of tabular rows;
- `DOCX/HTML` exports raw planning or service text instead of cleaned user-facing content;
- `PPTX` downloads successfully but contains only a generic slide like "table ready" while the actual table never appears.

## Recommended verification ladder

1. Verify auth and public path
   - Prefer the real user-facing contour, not only direct backend localhost.
   - In split runtime, verify both backend and public/proxy path when possible.

2. Verify transport
   - status code
   - MIME / content type
   - non-zero bytes

3. Verify semantic payload by format

### CSV / XLSX
- Check header row.
- Check at least 1–2 expected data rows.
- If the feature promises table export, reject fallback files that only contain message text.

### DOCX / HTML / Markdown
- Check that the exported body matches normalized display content.
- Reject exports that leak reasoning prefaces, planning blobs, service transcript, or internal metadata that should stay out of user-facing output.

### PPTX
- Do not stop at "file opens" or "there are N slides".
- Inspect extracted slide text or slide XML.
- Confirm expected table headers / key values are present on the table slide, not only on a title slide or a sentence like "summary table is ready".

## Routing-specific pitfall

If the user means "export the previous answer", followup phrases like:
- `да, лучше сразу в файл`
- `пришли файлом`
- `давай документ`

must stay in deterministic previous-answer export flow.
They should not silently switch to generation of a brand-new file artifact unless the user is clearly asking for new file generation.

## Good evidence examples

Strong evidence:
- public login succeeds;
- public export endpoint returns `200`;
- `CSV` body begins with the expected headers and rows;
- `PPTX` archive contains the additional slide and that slide XML includes the expected column names and values.

Weak evidence:
- unit tests only;
- backend localhost only when the public proxy may differ;
- file exists / bytes > 0 / MIME looks right.
