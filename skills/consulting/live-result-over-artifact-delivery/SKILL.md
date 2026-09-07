---
name: live-result-over-artifact-delivery
description: Use when live product value should replace repeated deck.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Live Result Over Artifact Delivery

## When to use
Use this skill when:
- a presentation, deck, document, or other artifact exists, but the user's current focus has moved back to the working product;
- the user reacts negatively to repeated mention of a deck, export, or presentation artifact;
- the task is implementation-heavy and the user wants proof of value in the live runtime rather than another delivery wrapper.

Typical signals:
- "хватит тащить презу"
- "мне нужна пользовательская ценность"
- "покажи результат в самом продукте"
- frustration that outputs look like packaging around weak substance.

## Core rule
Once the user shifts from artifact delivery to runtime value, stop surfacing the artifact by default.

Lead with:
1. live URL;
2. actual system behavior;
3. factual outputs and user-facing examples;
4. what changed in the product itself.

Treat slides, docs, and presentation files as secondary evidence only.

## Preferred delivery pattern
For product/runtime turns after artifact fatigue appears:
- first show the working URL or runtime entrypoint;
- then show one real user-facing output;
- then summarize what is better now;
- only mention supporting artifacts if the user explicitly asks for them again.

## What counts as success
The user should be able to understand the improvement from the product behavior itself, not from a deck describing it.

Good examples:
- the actual reply produced by the system;
- the actual contents of a user-facing screen;
- a live acceptance result;
- counts, statuses, and concrete runtime state tied to the experience.

Bad examples:
- repeatedly attaching the same presentation after the user has already seen enough;
- using a deck as a substitute for proving user value;
- describing the product better than the product currently behaves.

## Pitfalls
- Do not keep re-announcing an artifact just because it exists.
- Do not confuse packaging quality with product value.
- Do not answer a value complaint by polishing the explanation alone.
- Do not use presentation delivery as a fallback when the user actually wants the live product experience.

## Decision rule
If forced to choose between:
- one more presentation/document mention, or
- one more live demonstration of product behavior,
choose the live demonstration unless the user explicitly asks for the artifact.
