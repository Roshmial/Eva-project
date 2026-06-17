---
name: persona-portrait-iteration
description: Iterate portrait/avatar concepts from user references while preserving subject fidelity and adjusting energy, styling, and environment with minimal drift.
version: 1.0.0
user_locked: false
tags: [creative, portraits, avatars, image-generation, iteration]
---

# Persona Portrait Iteration

## When to use
Use this skill when the user wants to:
- develop a recurring assistant/persona/avatar image;
- iterate portraits from a reference photo;
- preserve the person while changing only styling, age impression, smile, wardrobe, or background;
- compare named archetypes or energy variants such as warmer vs sharper, approachable vs status-heavy.

## Core rule
Treat portrait iteration as two separate layers:
1. subject fidelity;
2. environment and energy tuning.

If the user says the girl/person is already right, stop redesigning the face and body. Keep the subject close to the reference and move the iteration pressure onto background, expression, wardrobe details, and realism.

## Procedure
1. Identify what is locked:
   - face / hair / apparent age;
   - outfit direction;
   - pose;
   - smile;
   - level of formality;
   - background.
2. Explicitly separate:
   - what must stay 1:1 or near-1:1;
   - what may change.
3. If a user provides a photo reference, extract practical descriptors:
   - age impression;
   - face shape;
   - hair color / texture / parting;
   - eye contact;
   - smile type;
   - blazer/top palette;
   - pose and hand placement.
4. Build prompts that preserve the subject first, then tune only one or two variables at a time:
   - younger/fresher;
   - warmer smile;
   - darker/lighter blazer;
   - more formal background;
   - more lived-in / less luxury-staged background;
   - more or less femme-fatale energy.
5. When the user dislikes a result, classify the miss precisely:
   - too simple;
   - too luxury-glossy;
   - too artificial;
   - still the wrong archetype;
   - failed to reproduce the smile/reference.
6. Iterate narrowly. Do not change five things when only one thing was rejected.
7. Once the user declares a version final, stop generating and treat it as canon.

## Prompting rules
- Prefer phrases like "keep the woman almost 1:1" or "keep the subject nearly unchanged" when the reference face is approved.
- Use direct smile language: "soft closed-mouth warm smile", "subtle asymmetry", "calm direct eye contact".
- Distinguish formal from luxury-staged:
  - formal = businesslike, clean, structured;
  - luxury-staged = expensive-looking, glossy, overdesigned.
- If the user wants realism, ask for:
  - natural human photography;
  - believable skin texture;
  - candid-professional tone;
  - premium but real.
- If the user wants status plus warmth, explicitly combine:
  - warm;
  - intelligent;
  - approachable;
  - slightly magnetic;
  - not cold.

## Named-archetype handling
When the user maps portraits to names or character energy:
- treat names as energy labels, not literal identities;
- explain the trade-off in plain language;
- be ready to conclude that one name fits the interaction style better than another.

Common mapping pattern:
- "Liza" = warmer, simpler, more approachable;
- "Eva" = warmer than cold-femme-fatale, but more status, magnetism, and character;
- "Nika" = sharper, more controlled, more severe.

Do not force the user into the original naming if the visual evolution clearly moved elsewhere.

## Pitfalls
- Do not keep reinterpreting the face after the user says the face is right.
- Do not accidentally reintroduce rejected background motifs such as stickers, toys, cars, clutter, or hobby objects.
- Do not confuse "formal" with "expensive luxury set".
- Do not turn "warm" into "simple" if the user actually wants warmth plus status.
- Do not promise a final pass and then keep proposing more generations after the user says the image is final.

## Output style
For each round, report briefly:
- what was preserved;
- what changed;
- why the new result should be closer.
Keep the explanation compact; the image is the main artifact.

## References
- See `references/eva-avatar-case.md` for a worked example of assistant-persona portrait iteration with a near-1:1 subject transfer from a user-provided office photo.

## Verification
Before presenting a new portrait, check:
- subject still resembles the approved reference;
- requested wardrobe change is visible;
- background removed previously rejected objects;
- realism improved if requested;
- the iteration changed only the intended variables.