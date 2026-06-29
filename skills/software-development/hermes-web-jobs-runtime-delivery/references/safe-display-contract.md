# Safe display contract for leaked assistant/job delivery text

Use this pattern when Hermes Web chat/job UI shows internal reasoning, prep text, or mixed `analysis + final` content.

## Symptom shape
- User-facing message shows lines like `We have the payload data ...`, `Let's parse them`, internal extraction notes, or a duplicated `analysis -> final` sequence.
- Cron/job output files may look clean while the persisted chat message is not.

## Root-cause split
1. Backend persistence/serialization issue:
- raw `messages.content` contains both prep text and final text;
- serializer exposes raw `content` without a dedicated safe user-facing field.

2. Frontend rendering issue:
- renderer (`messageDisplayText` or equivalent) uses `message.content` as source of truth with only cosmetic cleanup.

## Preferred fix
1. Backend computes a dedicated safe field such as `display_text`.
- Strip media tokens separately from semantic cleanup.
- Remove known prep/reasoning prelude before user-facing serialization.
- Store/backfill `display_text` in message metadata and expose it as a top-level serialized field.

2. Frontend prefers `display_text` over raw `content`.
- Read order should be:
  - `message.display_text`
  - `message.meta.display_text`
  - fallback to `message.content` only if no safe field exists.

3. Delivery extractors should also use the safe path.
- Hermes cron delivery extraction should return safe display text, not raw `## Response` tail blindly.
- Job-result footer cleanup should finish by returning the same safe display text helper, not raw trimmed text.

## Minimal backend helper pattern
- `strip_media_tokens(text)`
- `strip_internal_reasoning_prelude(text)`
- `build_message_display_text(text)`

Then wire:
- `enrich_assistant_meta(...)` -> `meta.display_text`
- `serialize_message(...)` -> top-level `display_text` + backfill for legacy rows
- delivery/result extractors -> `build_message_display_text(...)`

## Good regression set
1. Serializer regression:
- raw `content` still contains leaked prep text;
- serialized `display_text` contains only the final user-facing block.

2. Delivery extraction regression:
- `extract_hermes_output_for_delivery(...)` removes prep/reasoning prelude from `## Response` payloads.

3. Thread/jobs compatibility regression:
- existing jobs/threads endpoints still serialize and sort messages without 500s after the new contract is introduced.

## Important rule
Treat regex-only frontend stripping as a fallback guard, not the primary solution. The real contract is: backend owns safe display text, frontend renders that field.