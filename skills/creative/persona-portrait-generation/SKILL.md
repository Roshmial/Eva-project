---
name: persona-portrait-generation
description: Generate and iterate on human persona portraits or assistant avatars while preserving identity, controlling age/style, and separating subject from environment.
version: 1.0.0
user_locked: false
tags: [creative, image-generation, portrait, persona, avatar]
---

# Persona Portrait Generation

## When to Use
Use this skill when the task is to:
- create or refine an assistant avatar;
- generate a human persona portrait for ongoing interaction;
- compare several name/energy archetypes built on one common visual base;
- adjust age impression, formality, warmth, or status without losing the successful core look.

## Core Principle
Treat the portrait as three separate layers and modify them independently:
1. subject identity — face, hair color, age impression, expression, vibe;
2. clothing/styling — wardrobe, grooming, polish level;
3. environment — office, home-office, boardroom, creative space, objects, clutter level.

Do not rewrite all three layers at once if only one of them is wrong. Preserve the winning layers and only change the layer the user criticized.

## Procedure
1. Identify what already works:
   - person/face;
   - clothing;
   - expression/energy;
   - environment/background.
2. Identify what needs adjustment:
   - too old / too young;
   - too cold / too playful;
   - too corporate / too casual;
   - too generic / too stylized.
3. Lock the successful parts explicitly in the next prompt:
   - "keep the girl and outfit in the successful previous direction";
   - then describe only the required change.
4. For age corrections, use bounded phrasing:
   - "visibly younger";
   - "youthful but adult";
   - specify a believable adult range;
   - avoid sliding into teen, anime, or flirty caricature.
5. For environment corrections, specify the space as its own design task:
   - formal and clean;
   - refined office / executive meeting room / strategy room;
   - subtle work context;
   - no stickers, toys, clutter, or scattered casual objects when the user wants formality.
6. When comparing variants, hold most variables constant and vary only one axis:
   - warmth;
   - magnetism/status;
   - sharpness/discipline;
   - environment formality.
7. If names/archetypes are being compared, map them to interaction feel, not just looks:
   - comfort of long-term interaction;
   - status / brand impression;
   - sharpness / distance.
8. Present a concise recommendation and explain the trade-off between:
   - everyday relational comfort;
   - visual status;
   - stronger edge or discipline.

## Prompt Pattern
Use a prompt with these blocks:
- identity anchor;
- preserved successful elements;
- one requested adjustment;
- environment requirements;
- negative constraints.

Example structure:
- "Refined portrait based on the successful previous concept..."
- "Keep the girl and clothing in the same ideal direction..."
- "Environment should be more formal and clean..."
- "Blend formality with warmth/liveliness..."
- "No anime, no neon, no exaggerated glamour, no clutter..."

## Pitfalls
- Do not regenerate from scratch after the user already approved the face/clothing direction.
- Do not change age, styling, and environment all at once unless the user asked for a full reset.
- Do not confuse "alive" with clutter, stickers, toys, or casual noise.
- Do not confuse "younger" with immature.
- Do not make the background so formal that the portrait becomes cold or stock-like.
- Do not evaluate only aesthetics; evaluate fit for repeated interaction.

## Output Pattern
Give:
- the images;
- a short comparison;
- a recommendation;
- one clear next step.

When the user asks which persona fits them better, distinguish:
- best for comfort and trust;
- best for status/brand effect;
- best for sharper business energy.

## References
- See `references/misha-assistant-persona.md` for a concrete persona brief and naming/energy mapping example.
