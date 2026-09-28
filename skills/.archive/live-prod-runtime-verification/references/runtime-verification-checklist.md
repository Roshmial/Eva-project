# Live runtime verification checklist

## 1. Contour mapping
- Record frontend host:port.
- Record backend host:port.
- Confirm expected upstream direction explicitly.
- Verify `/api/service-info` or equivalent on both direct backend and frontend-proxied path.

## 2. Admin/UI failure triage
- Confirm role and viewport gating first.
- Reproduce in browser.
- Inspect console/runtime errors.
- If navigation exists but screen fails, inspect handler/prop mismatches before redesigning access rules.

## 3. Attachment ingestion review
Check both parser coverage and truncation:
- max upload size
- max files per request
- extracted text cap
- preview cap
- per-format structure support

Minimum format checklist:
- DOCX: body, tables, header, footer
- XLSX: workbook sheets and row text
- PPTX: slide text, tables, notes
- PDF: text extraction path and fallback note when parser/OCR support is unavailable

## 4. Session continuity
- Verify TTL default.
- Verify expiry is based on last activity, not login time.
- Verify session-touch path updates last activity in real requests.

## 5. Long-chat continuity after model reset
- Confirm full message history is persisted by thread.
- Add/history-summary compaction when message count or char budget is exceeded.
- Pass summary + recent tail to the model.
- Surface metadata that compaction occurred for debugging.

## 6. LLM output publication guard
Block or fail closed on:
- tool transcript leakage
- raw technical dumps
- repetitive garbage
- false artifact/file claims

## 7. Reporting discipline
Split final status into:
- confirmed live
- fixed in code
- tested locally
- still not deployed/proven on prod
