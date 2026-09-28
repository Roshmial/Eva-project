# Recurring render branch vs display_text

Use this pattern when a live chat UI still shows reasoning/planning text after backend sanitization appears correct.

## Failure shape

A message may have several parallel text surfaces:
- `content`
- `display_text`
- `meta.display_text`
- `meta.recurring_summary.summary`
- `meta.recurring_summary.status_detail`

The frontend may not use the normal assistant bubble for all message kinds. For recurring/job deliveries it can suppress `messageDisplayText(...)` entirely and render a dedicated recurring card instead.

## Diagnostic sequence

1. Inspect the persisted live message row.
2. Inspect the final API payload for the exact message (`serialize_message(...)` or equivalent).
3. Compare these fields separately:
   - `payload.display_text`
   - `payload.meta.display_text`
   - `payload.meta.recurring_summary.summary`
   - `payload.meta.recurring_summary.status_detail`
4. Read the frontend render path for that message class.
   - Confirm whether the normal bubble is skipped.
   - Confirm source priority inside the specialized card.
5. Fix both layers when needed:
   - frontend should prefer cleaned `display_text` over stale nested summaries;
   - backend recurring envelope should normalize nested `summary/status_detail` too, otherwise the same stale text can leak into another surface later.

## Concrete lesson from this session

A live Telegram digest message had:
- cleaned `display_text`
- stale `meta.recurring_summary.summary`
- stale `meta.recurring_summary.status_detail`

The recurring card preferred stale nested fields ahead of `display_text`, so the UI still showed reasoning/planning text even though the normal assistant payload looked fixed.

The durable fix was:
- frontend: reorder recurring-card source priority to `display_text -> meta.display_text -> recurring.summary/status_detail -> content`
- backend: build recurring envelope `summary/status_detail` from normalized content first, then only fallback to older nested fields.
