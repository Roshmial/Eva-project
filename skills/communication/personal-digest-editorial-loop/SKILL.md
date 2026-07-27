---
name: personal-digest-editorial-loop
description: How to produce short personal digest messages for this user with iterative editorial QA so the final text sounds like a real Telegram message rather than generated prose.
---

# Purpose

Use this skill when generating short personal digests, daily briefs, check-ins, reminder-style messages, or similar compact personal guidance for this user.

The main lesson from repeated corrections: content quality was often acceptable, but the delivery felt generated, over-explained, symmetric, or mechanically polished. The fix is not just better wording. The fix is an explicit editorial loop.

# When to use

Use for:
- daily brief / morning digest generation
- short Telegram-style planning notes
- personal recommendation lists for the day
- recurring cron-generated brief messages
- any compact message where the user wants something that reads like a familiar human wrote it quickly

# Core principles

1. Optimize for how the text lands, not just for whether it is technically correct.
2. Prefer short, direct, human phrasing.
3. A plain useful sentence is better than a clever sentence.
4. If a concrete link makes the sentence clunky, drop the link instead of forcing it.
5. Recommendations should be dynamic to the day, not a fixed checklist disguised with synonyms.
6. Do not inspect or rewrite the user’s actual task content unless asked. Focus first on format, liveliness, and legibility.

# Required generation workflow

Follow this loop every time:

1. Generate several draft candidates, not just one. Minimum: 3 candidates with different rhythm or recommendation mix.
2. Make at least one candidate that tries a live content recommendation when appropriate: video, music, article, event, or route.
3. Review each candidate as a strict editor for user-facing Telegram text.
4. If a candidate does not pass, rewrite it and review again.
5. Continue the rewrite -> review loop until the text passes or you hit 10 iterations per candidate.
6. Keep track of the best-scoring candidate across the whole cycle. Do not default to the last version just because it is last.
7. Compare the best candidate against yesterday's final digest. If it is too similar in structure, meaning, or recommendation shape, rewrite again.
8. If several versions remain imperfect, choose the shortest, simplest, liveliest option with the least similarity to yesterday.

This is a true cycle, not a single cleanup pass. After every rewrite there must be a fresh review.

# Review checklist

A draft fails review if any of these are true:
- it feels generated
- it feels too smooth, too balanced, or too symmetric
- it sounds like a polished note instead of a quick human message
- it includes bureaucratic wording or abstract framing
- it explains a recommendation instead of simply giving it
- it contains decorative filler
- it uses a raw URL that breaks the flow
- it includes over-precise mechanics that make the sentence feel synthetic
- it uses explicit contrast constructions like «..., а не ...»
- it uses qualifier tails like «..., без ...» when a shorter sentence would do
- it repeats yesterday's digest too closely in structure, meaning, or recommendation type
- it can be shortened further without losing meaning
- it chooses a dry generic sentence over a natural sentence with a good link

# Language rules for this user

## Required defaults

- Start the daily brief with: «Доброе утро, Миша!» when that format is expected.
- Keep the message compact.
- One thought per line is usually better than long combined sentences.
- Prefer simple verbs and everyday nouns.
- Allow slight conversational unevenness.

## Avoid

Avoid words and patterns that repeatedly triggered user pushback:
- «поддерживающая вещь»
- «бытовой сброс»
- «конкурентный рабочий результат»
- «рабочий блок»
- «собрать базу»
- «переключить голову»
- «держать в голове»
- «подтянуть всё»
- «что поедет с тобой»
- «вязкая задача»
- «тот кусок работы, который...»
- «хвост» / «хвосты» in digest prose
- «подойдёт» when it acts as bland filler
- «выдели 20–30 минут» unless timing is genuinely essential

Also avoid:
- generated optimization phrasing
- explanatory tails after an already complete recommendation
- raw pasted links in the body when a normal sentence would be cleaner

# Recommendation selection rules

The user wants a dynamic mix, not a nailed-down recurring checklist. Depending on the day, recommendations may include:
- work
- trip prep
- a walk
- music
- a film / series / video
- an event
- a small practical household action
- a short admin step
- rest

Do not force pre-trip advice every time a trip exists in the background.
Do not force content suggestions if they sound bolted on.
Prefer omission over a weak filler recommendation.

Do not default to a rigid micro-template like:
- `Фокус дня: ...`
- recommendation 1
- recommendation 2

That shape often creates symmetry, duplicate meaning, and generated tone even when each line is individually acceptable.
Prefer a short Telegram note with one live main thought and 1–2 genuinely different supporting lines.
If the explicit `Фокус дня:` label makes the text worse, drop it.

A draft also fails if:
- the supposed main thought could be pasted into almost any weekday unchanged;
- the main thought and a trip/admin recommendation collapse into the same storyline;
- two recommendations both orbit the same trip/logistics plot in softer words;
- the text sounds like a mini-plan or checklist instead of a normal human morning message.

# Link handling

- If a link fits naturally, integrate it into a human sentence.
- Good links can make the digest feel more alive: video, music, article, route, or event.
- If a link would appear as a naked URL or make the sentence clunky, omit it.
- Better no link than a bad link insertion.
- If two variants are equally alive, prefer the one with the well-integrated useful link.

# Final test

Before sending, ask internally:

«Я правда могла бы так написать человеку в Telegram с телефона?»

If the answer is no, rewrite again.

# Pitfalls

## Pitfall: fixing words but not the process

Symptom:
- the same generated feeling returns with new vocabulary

Fix:
- switch from one-off prompt patching to a rewrite/review loop with explicit pass-fail criteria

## Pitfall: over-optimizing usefulness

Symptom:
- every line becomes technically useful but text stops sounding human

Fix:
- keep the recommendation, remove the explanation
- choose simpler wording even if it sounds less “smart”

## Pitfall: forcing links

Symptom:
- a recommendation reads fine until a raw URL is appended

Fix:
- either embed the link naturally or drop it

# References

- references/digest-style-signals.md — concrete user corrections and failure patterns that shaped this skill
