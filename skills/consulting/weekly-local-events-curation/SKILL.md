---
name: weekly-local-events-curation
description: Use when weekly city picks miss short-window events.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Weekly local events curation

Use when preparing a weekly подборка городских событий для этого пользователя or repairing a recurring city-events digest that has become repetitive, overly venue-biased, or padded with long-running filler.

## What this skill is for

This skill governs weekly event picks where the output should feel like a practical human shortlist, not a generic afisha dump.

Typical triggers:
- the user complains that the digest keeps collapsing into one venue or one source;
- a city-scale occasion such as Day of the City, a seasonal closing weekend, or a short festival block was missed;
- the list is padded with easy long-running exhibitions because they are convenient to verify;
- the output feels technically correct but strategically weak.

## Core selection order

Prioritize in this order:
1. local events available only for a short window;
2. events that start this week or end this week;
3. citywide programs with a real reason this week;
4. only then long-running exhibitions, and only as careful backfill.

A weekly list should answer: what in the city is worth catching now, before the window closes?

## Hard constraints

### 1. No single-source drift
- Default maximum: 2 items from one venue.
- Default maximum: 2 items from one domain/source.
- More than 2 is allowed only for a real citywide cluster such as Day of the City, a major festival, or a tightly bounded special program.
- If such an exception is used, the reason must be visible from the week itself, not from source convenience.

### 2. Respect the week boundary literally
- Never include events outside `week_start..week_end`.
- Re-check every chosen date before finalizing.
- A strong event that starts after `week_end` is still disallowed.

### 3. Prefer precise timing
- For normal venue events, require an exact date/time or a short explicit within-week range.
- Phrases like 'ещё идёт', 'ещё актуально', or other vague availability wording are weak evidence and should usually be rejected.
- Citywide programs are the main exception if the official page clearly shows the within-week block.

### 4. No weak tail padding
- The last 1–2 items should survive a stricter filter.
- If a candidate is only a generic long-running museum fallback and not a short-window item, a start/end-of-week event, or a strong citywide hook, drop it and return a shorter list.

## Source strategy

1. Start from official and primary sources.
2. Put citywide official pages first when the week has an obvious city-scale hook.
3. Use direct extraction first.
4. Use web search only as a rescue path.
5. Stop once enough verified items exist.

## Bias control from recent outputs

When this is a recurring digest, inspect recent outputs and track:
- repeated venue dominance;
- repeated domain dominance;
- repeated recommendation titles.

Treat these as penalties, not as anchors.
A venue or domain that dominated recent weeks should face a higher inclusion bar in the current week.

## Quality gates for this user

Reject or rewrite a candidate set if:
- one institution dominates because it was easiest to verify;
- a major citywide occasion this week is absent;
- most items could have been recommended on many neighbouring weeks unchanged;
- the output contains a strong first half and a weak museum-filler tail;
- the selection explains the city poorly for this specific week.

## Verification pattern

Before finalizing, check explicitly:
- all items are inside the requested week;
- there is no hidden venue/domain collapse;
- at least one major weekly city hook was considered when relevant;
- the bottom of the list is not weaker than the user's tolerance for filler;
- fewer verified items are allowed if that avoids low-quality padding.

## Good final framing

Lead with:
- the week range;
- that the shortlist prioritizes short-window / starting / citywide events;
- the major weekly hook if there is one.

Keep the tone concise, practical, and human.
Do not sound like an afisha bot.

## Pitfalls

- Do not treat long-running exhibitions as the default path to fill quota.
- Do not confuse multiple venue names with true source diversity when the links still come from one dominant domain.
- Do not let an apparently 'successful' cron run mask a bad editorial result; inspect the actual delivered output.
- Do not allow a post-week event to slip in just because the title looked strong.

## References

- Add recurring examples, source quirks, and scoring heuristics under `references/` when a real weekly digest failure reveals a reusable pattern.
