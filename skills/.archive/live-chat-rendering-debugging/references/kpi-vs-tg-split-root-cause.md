# KPI vs TG split root cause — session note

Use this as a concrete example of why live chat rendering incidents must be split by layer and by message class.

## Symptoms
- User reported two seemingly related problems:
  - `KPI`: markdown formatting looked wrong; user explicitly asked to fix this case separately and not change global rendering.
  - `ТГ Дайджест`: messages for 24–25.06 looked missing or malformed.

## What live checks established
- `KPI` problem message: `thread 224`, assistant `message 903`.
- `ТГ Дайджест` latest messages: `thread 74`, messages `871` (24.06) and `914` (25.06).
- For TG, raw stored `content` was polluted with planning/reasoning text.
- But live API already returned clean user-facing `display_text` beginning with `Дайджест ИТ-консалтинга...`.

## Durable lesson
- Do not collapse these into one generic "markdown bug".
- `KPI` was a narrow frontend rendering/legibility issue for wide markdown tables.
- `TG` was a legacy data-shape issue in stored message body; the serializer contract was already the user-facing source of truth.

## Good fix shape
- For `KPI`, prefer a thread-scoped or message-class-scoped render branch (for example by `meta.thread_title == 'KPI'`) rather than a global markdown/table renderer switch.
- For old digest/job-delivery messages, confirm whether `display_text` is already clean before attempting DB surgery.

## Verification pattern
1. Compare `content`, `meta.display_text`, and live API `display_text` for the same message id.
2. If API is already clean but DB raw body is not, describe it as a serializer-vs-storage split, not message loss.
3. If the user explicitly asked for a local fix, keep the renderer change scoped and document that scope explicitly.
