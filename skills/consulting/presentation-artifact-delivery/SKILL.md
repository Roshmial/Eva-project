---
name: presentation-artifact-delivery
description: Use when delivering presentation artifacts. Prefer normal client-readable outputs over internal editor-native formats.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Presentation Artifact Delivery

## When to use
Use for requests to create, export, or hand off presentations, decks, or slide-like artifacts.

## Core rule
The primary deliverable should be a normal client-readable presentation artifact, not the internal working format of the rendering engine.

Examples of acceptable primary delivery formats:
- standalone HTML presentation;
- PDF deck;
- other directly readable presentation outputs.

Examples of secondary / optional source artifacts:
- `.bento.html`;
- editor-native project files;
- intermediate JSON / markdown / outline files.

## Delivery order
1. Build the presentation itself.
2. Export or package it into a normal viewing format.
3. Verify the exported artifact exists and contains the slide content.
4. Deliver the viewable artifact first.
5. Only then, if useful, include the editable source artifact as an optional companion file.

## User-specific lessons embedded
For this user, a request for a presentation means an actual presentation-looking artifact, not an outline, markdown summary, or internal engine file.

If Bento or another slide engine is used under the hood:
- treat it as production machinery, not as the user-facing default;
- HTML/PDF-style outputs should be the primary handoff whenever feasible;
- engine-native files may still be saved for later editing, but should not be the only meaningful result.

## Pitfalls
- Do not hand off only the engine-native file when a normal presentation format is feasible.
- Do not silently downgrade a presentation request into a text outline.
- Do not present markdown as the main deliverable unless the user explicitly asked for text rather than slides.
- Do not stop at a technically valid artifact if it is not legible or presentation-like.
- Do not end with a list of optional next steps when the user asked for turnkey delivery; finish the presentation artifact itself first.

## Verification
Before finishing, confirm:
- the presentation artifact exists;
- it opens in a normal viewer class for its format;
- the slide count or section count is plausible;
- the main text and visual blocks are actually present;
- the user-facing file is the primary delivery.
