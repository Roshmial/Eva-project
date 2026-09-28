# Session note — recurring digest duplication and KPI markdown verification

## What mattered

### 1. Recurring/job-delivery duplicate render can come from one message, not two

Observed class of bug:
- user sees one digest twice;
- first as plain assistant text;
- second as recurring/digest card.

Important finding:
- the affected digest was a single `job_delivery` message in DB;
- `recurring_summary` was derived in `serialize_message(...)`, not stored in raw `meta_json`;
- duplicate UI came from dual render channels for one message, not from two thread rows.

## Durable fix pattern

Apply both layers:

### Frontend
Suppress plain assistant text for any message with `meta.recurring_summary`, not only when attachments exist.

### Backend serializer
If `recurring_summary` exists for an assistant message:
- set top-level `display_text` to empty;
- clear `meta.display_text` too.

Rationale:
old fallback paths may still read `meta.display_text` even after top-level cleanup.

## 2. Missing markdown requires parser-check on exact live text

In this session the KPI message looked like plain text in the screenshot, but the durable investigation pattern was:
- fetch exact live `display_text` for the affected message;
- run that exact string through the same markdown parser/tokenizer used by the frontend;
- inspect whether tokens include `table`, `heading`, `hr`.

Meaning of the result:
- if parser already recognizes tables/headings/hr on exact live text, root cause is no longer markdown syntax itself;
- then inspect runtime render-path, bundle freshness, or state/fallback selection.

## Suggested evidence to capture next time

For each affected message, keep a compact before/after snapshot:
- raw `content` prefix;
- `meta.display_text` prefix/length;
- serialized `display_text` prefix/length;
- whether `meta.recurring_summary` exists;
- which frontend card path should be the only remaining one.
