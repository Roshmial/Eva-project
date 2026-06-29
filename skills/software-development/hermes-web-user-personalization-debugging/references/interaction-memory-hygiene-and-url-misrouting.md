# Interaction memory hygiene and URL misrouting

## Why this note exists

Live Hermes Web incident pattern: a user asks a simple source-first question such as `Опиши, что по ссылке ...`, but the answer drifts into unrelated domain content because per-user personalization is overloaded with subject-matter notes from older tasks.

## Confirmed symptoms from the incident

- User-facing memory contained domain-heavy business content instead of only interaction rules.
- A Google Maps shortlink request was answered with BI / TCO / CSV-oriented content.
- The model later self-corrected, revealing it had followed profile noise rather than the source.
- Historical wrong assistant messages then had to be cleaned from chat history because the live product surface looked broken even after the routing logic was improved.

## What to inspect

1. `app.users.interaction_memory_json`
2. `app.users.pinned_json`
3. `build_personalization_block(...)`
4. `build_hermes_system_prompt(...)`
5. recent assistant messages for the user, especially whether the bad answer aligns with noisy profile content rather than the actual request

## Red flags in interaction memory

Treat these as likely contamination, not valuable personalization:
- KPI trees
- metric taxonomies
- CSV-derived phrases
- long domain summaries
- evaluation criteria copied from one project
- broad work-context statements that do not change how the assistant should interact

## Remediation pattern

1. Reduce `interaction_memory_json` to concise interaction rules only.
2. Keep only stable communication preferences in `pinned_json` / profile memory.
3. Tighten auto-writeback heuristics so generic words do not create memories.
4. Add a source-first rule for URL requests in the system prompt.
5. If the live thread now contains obviously wrong assistant messages, consider cleaning those messages so the UI reflects the corrected product behavior.

## Good target shape for cleaned memory

Examples of good items:
- `Предпочитает краткий деловой стиль без воды.`
- `Ожидает рекомендации с чёткими действиями и приоритетами.`
- `Если просит итоговый материал, предпочитает готовый к презентации результат.`

Examples of bad items:
- domain metric frameworks
- KPI decomposition text
- vendor-comparison criteria from a single task
- copied problem statements from past chats

## Durable lesson

When a bad answer appears to come from the model "being weird," verify personalization hygiene before blaming the browser tool, upstream source, or generic model quality. In Hermes Web, noisy per-user memory can be the real root cause of source-irrelevant completions.
