# Document generation: preserve user structure, strip technical metadata

Use this note when a live Hermes-style web runtime generates or exports `docx` / `pptx`, but the user-visible file looks like a technical dump instead of a real document.

## Failure pattern

Typical symptoms:
- the app correctly routes to file generation, but the resulting `docx` contains service text such as `Чат: ...`, `Сообщение #...`, `Дата: ...`, ids, timestamps, or status phrasing;
- a `pptx` title slide/subtitle leaks message ids or backend timestamps;
- structured answer content is flattened into plain paragraphs, losing headings, lists, and tables;
- continuity/file-routing fixes appear correct, but the final file still looks wrong because packaging reuses an older export builder.

## Root cause class

The same builder is often reused for two different jobs:
1. explicit message export;
2. generated-file delivery.

If that builder takes its source from line-flattened export helpers instead of cleaned display content, the system will package service metadata and lose structure even when chat routing is correct.

## Preferred fix shape

1. Use cleaned user-facing content as source-of-truth.
   - Prefer a canonical helper such as `build_message_export_body(...)` or equivalent cleaned display-text source.
   - Do not build user documents from helpers that prepend thread title, message id, created_at, status labels, or other service metadata.

2. Parse baseline structure before packaging.
   - Preserve at least:
     - headings;
     - paragraphs;
     - bullet / numbered lists;
     - markdown-style tables.

3. Keep technical metadata out of the user document.
   - `docx` should not auto-insert `Чат`, `Сообщение`, `Дата`, ids, or timestamps unless the user explicitly asked for an audit/export transcript.
   - `pptx` title/subtitle should prefer meaningful content headings, not backend metadata.

4. Test both dimensions together.
   - Positive checks: expected headings/lists/tables survive.
   - Negative checks: `Чат:`, `Сообщение #`, `Дата:`, ids, timestamps do not appear in the user-facing file.

## Minimal regression strategy

Add targeted tests that verify:
- generated-file `docx` keeps structure and omits technical metadata;
- direct message-export `docx` also omits technical metadata;
- neighboring generated-file routing/continuity tests still pass, so document-builder fixes do not regress file delivery semantics.

## Reporting discipline

When the live rollout is done, report separately:
- code fix applied;
- local targeted tests passed;
- live backend restarted/health-checked;
- whether a real user-path download/open of the resulting document was also verified.
