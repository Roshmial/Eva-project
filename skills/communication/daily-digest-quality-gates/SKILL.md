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
- it is useful only in the weak sense of being unobjectionable.

## Pipeline guidance

When improving the workflow, prefer staged contours:
- context gathering;
- candidate generation;
- critique/selection;
- fallback only when necessary.

Do not let fallback become a convenient escape hatch for weak generation.
Fallback is acceptable only as an honest minimum, not as a preferred winner over better contextual candidates.

## User-specific operating notes

For this user:
- analysis must be concrete and evidence-led, not hypothesis-led;
- 'not artificial' is not enough — the digest must also be genuinely useful;
- safe generic weather text should be treated as a failure mode;
- if there is already a concrete same-day hook, it usually deserves to appear in at least one strong candidate and often in the final text.
