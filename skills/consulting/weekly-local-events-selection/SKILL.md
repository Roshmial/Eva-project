---
name: weekly-local-events-selection
description: Use when picking weekly local events. Prioritize now.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Weekly Local Events Selection

## When to use

Use this skill when preparing:
- weekly city event digests;
- shortlist-style local activity picks;
- recurring Telegram/event recommendations for one city;
- "what should I do this week in <city>" подборки.

Especially use it when the user is unhappy that the selection:
- collapses into one venue;
- overuses one domain/source;
- fills space with long-running exhibitions;
- misses the obvious citywide event of the week.

## Core rule

The job is not to maximize count. The job is to surface what is worth catching now.

Default ranking order:
1. local events with a short availability window;
2. events that start this week or are in their last days;
3. major citywide/weekend programs that matter specifically this week;
4. only then durable exhibitions or evergreen items as backfill.

If the strong verified list is only 6-7 items, return 6-7. Do not pad with weak museum tails.

## Selection logic

### 1. Establish the week boundary first
- Define explicit `week_start` and `week_end`.
- Every candidate must be checked against that boundary before final delivery.
- If an event starts after `week_end`, it is out.
- Keep a final pre-send pass whose only job is date validation.

### 2. Check the major city trigger of the week
Before ordinary venue hunting, ask whether the week has a strong city-level reason people would care now:
- Day/Weekend of the city;
- season opening/closing;
- major festival;
- special city program.

If such a trigger exists, it must be checked and usually appear at least once in the final list.

### 3. Control source concentration
Track both:
- venue/place concentration;
- source-domain concentration.

Default guardrails:
- max 2 picks from one venue;
- max 2 picks from one source domain.

3+ from one venue or domain is allowed only when it is a true week-defining cluster such as a citywide holiday block or a festival, and the reason should be obvious from the week.

### 4. Penalize easy-but-weak backfill
Late-list candidates need a stricter bar.

For the last 1-2 slots, reject items that are merely:
- still running;
- generic museum fillers;
- weakly dated "still relevant" picks;
- duplicates in tone/source when better week-specific options exist.

### 5. Prefer exact timing for ordinary events
For non-citywide events, prefer:
- exact date;
- exact time;
- or a short explicit range inside the week.

Avoid vague wording like:
- "ещё идёт";
- "ещё актуально";
- "всю неделю";
unless the page truly gives nothing more precise and the item is ending soon or clearly belongs to the week.

## Recommended workflow

1. Gather week boundary.
2. Identify citywide/seasonal trigger of the week.
3. Start from primary/official sources.
4. Use rescue search only when the official page is insufficient.
5. Build a candidate pool with explicit fields:
   - title
   - venue
   - source_domain
   - date/time
   - why_now
   - link
6. Apply bias checks:
   - place bias from recent outputs
   - domain bias from recent outputs
7. Apply final date-boundary pass.
8. Only then write the user-facing digest.

## Output guidance

Good weekly event picks should feel like:
- "это стоит ловить сейчас";
not like:
- "вот чем можно добить список".

For this user, the digest improves when it clearly favors:
- short-lived;
- newly starting;
- city-relevant this week;
- locally grounded events.

## Pitfalls

### Pitfall: one-venue collapse
Symptom:
- many picks come from one institution because its site is easy to parse.

Fix:
- enforce venue cap;
- require a stronger reason for the 3rd item from the same place.

### Pitfall: one-domain collapse without one-venue collapse
Symptom:
- items come from different subprograms but the same domain keeps dominating.

Fix:
- treat domain concentration separately from venue concentration.

### Pitfall: long-running exhibition padding
Symptom:
- the list reaches 8-10 items only because durable exhibitions were used as filler.

Fix:
- shorten the list instead of padding it.
- raise the bar for the last 1-2 slots.

### Pitfall: missing the obvious weekly city trigger
Symptom:
- the digest ignores a citywide event like Day of the City while focusing on niche venues.

Fix:
- inspect citywide/official programs first.

### Pitfall: date leakage past the requested week
Symptom:
- a strong event just beyond `week_end` sneaks into the list.

Fix:
- explicit final date audit against `week_end` before delivery.

## Support files

- `references/moscow-weekly-events-logic-2026-08.md` — concrete lessons from a real Moscow weekly-events correction pass: source bias, date leakage, and selection guardrails.
