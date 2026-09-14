---
name: daily-digest-quality-gates
description: Use when personal digests need anti-banality quality gates.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Daily digest quality gates

## When to use

Use this skill when working on:
- morning daily briefs;
- short personal digests;
- Telegram-native reminder/check-in style messages;
- recurring complaints that the output feels artificial, repetitive, generic, or useless.

Especially use it when the user is unhappy with quality and asks for analysis, correction, or a pipeline rebuild.

## Core rule

Do not jump straight from a bad output to redesign ideas.

For this class of task, the correct order is:
1. assess the actual output;
2. name the defect class with evidence;
3. only then change the spec, rubric, or runtime pipeline.

If the user asked for analysis, give a real evaluation of the produced text first. Do not answer with a loose list of hypotheses about the system before evaluating the artifact itself.

## What counts as a bad digest

A digest is bad not only when it is artificial or editor-like.
It is also bad when it becomes safely generic.

Reject outputs that:
- could be sent almost unchanged on many neighbouring days with similar weather;
- contain mostly weather plus generic pacing advice;
- sound harmless but have no real day-specific value;
- drop a concrete same-day hook already present in context and replace it with vague advice;
- are formally clean yet still feel like filler.

## Defect classes to distinguish

### 1. Artificial/editorial
Symptoms:
- polished lifestyle tone;
- pseudo-human phrasing;
- decorative wording;
- overbuilt smoothness.

### 2. Safe banality
Symptoms:
- the text is no longer cringe, but still too universal;
- weather and pacing dominate the whole output;
- advice like 'go earlier', 'don't overload the evening', 'keep the day light' carries the whole message;
- the same structure would survive across many similar days.

### 3. Lost contextual hook
Symptoms:
- helper context, recent travel context, or a valid same-day suggestion exists;
- the final digest ignores it without a real conflict;
- a concrete opportunity is replaced by generic advice.

### 4. Pseudo-recommendation
Symptoms:
- the line merely checks that a basic bodily need was met, for example water;
- the suggested action is trivial household maintenance or a generic checklist item;
- the user could receive the same instruction from any task manager, with no added context, selection, or benefit.

Reject classes:
- water-control prompts;
- checking a calendar, subscription, or one small expense without a stated decision;
- tidying a bag, desk, shelf, tab, or file only to fill the message;
- vague administrative commands such as «одним взглядом проверить» or «оставить опору на завтра».

A supporting line is acceptable only when it is independently worth receiving: a current concrete event, a context-relevant route, or a named resource with a direct link and a clear reason to use it.

## Evaluation rubric

When evaluating or filtering candidates, check:
1. naturalness;
2. non-artificial tone;
3. practical value;
4. no recent-repeat masquerading as new;
5. realism of the day;
6. non-banality;
7. day-specificity;
8. use of available concrete context.

A candidate should be rejected if:
- it is artificial;
- it is generic enough to fit many similar days;
- it ignores a valid concrete same-day hook without a reason;
- it is useful only in the weak sense of being unobjectionable;
- it is a pseudo-recommendation from the reject classes above.

## Pipeline guidance

When improving the workflow, prefer staged contours:
- context gathering;
- candidate generation;
- critique/selection;
- fallback only when necessary.

Do not let fallback become a convenient escape hatch for weak generation.
Fallback is acceptable only as an honest minimum, not as a preferred winner over better contextual candidates.

### Contextual suitability gate
Before releasing a candidate, check whether its action fits the actual day conditions. A route, outdoor walk, or open-air plan must be excluded when the verified forecast materially conflicts with it, for example probable rain. Do not preserve a candidate merely because it has a link.

Make reject rules deterministic where the pipeline has a candidate registry: filter invalid classes before selection, rather than asking the final writer to notice them. If the remaining pool cannot produce a worthy supporting line, fail the selection step or omit that line when the format permits; never silently fall back to a banned pseudo-recommendation.

A candidate selector must return no candidate when fresh inventory is exhausted. Never rank a repeated item as a fallback merely to satisfy a fixed output shape; the delivery contract must permit a shorter message or `[SILENT]`.

### Renewable advice inventory
For recurring daily advice, maintain a finite, curated candidate pool rather than substituting city events or a generic web scout when advice inventory runs low. Keep the sent-item ledger separate from the candidate pool: the ledger blocks repeats, while the pool supplies the next advice.

Target a pool of 40–50 concrete cards across balanced families. Refresh a defined subset weekly, and trigger an earlier refresh when the number of eligible cards falls below the safety threshold. A refresh must replace weak, repeated, or overrepresented families before creating novelty for its own sake.

Run the daily selector over every eligible family; do not hard-code a narrow subset that silently exhausts while valid inventory exists elsewhere. Require an explicit family distribution check before enabling a new pool.

Treat supplementary recommendations as optional. Admit a linked card only when the text asks for a concrete action and the link is part of completing it; reject bare documentation, resource directories, and raw URLs because a reference alone is not daily advice.

When testing a replenishment run, inspect the produced pool and simulate consecutive selections before deployment. Verify item counts, family distribution, unique IDs, and non-repetition; report only the actual job result, never a queued run as if it had produced a pool.

Use `[SILENT]` only as the honest fail-safe while replenishment is unavailable or fails validation. It is not the normal replenishment strategy.

## User-specific operating notes

For this user:
- analysis must be concrete and evidence-led, not hypothesis-led;
- 'not artificial' is not enough — the digest must also be genuinely useful;
- safe generic weather text should be treated as a failure mode;
- if there is already a concrete same-day hook, it usually deserves to appear in at least one strong candidate and often in the final text.
