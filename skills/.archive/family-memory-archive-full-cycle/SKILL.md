---
name: family-memory-archive-full-cycle
description: Use when building local-first family memory archive MVPs.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Family Memory Archive Full Cycle

## When to use
- Local-first family archive MVPs.
- Episode-first memory systems built around media, people, переписки, and evidence-backed retrieval.
- Tasks where the user asks for "под ключ" and expects a real end-to-end run through the shipped product, not just code and tests.

## Core approach
1. Build around `episode` as the main retrieval unit.
2. Keep ingest broad: media files, folder import, and conversation JSON import should all land in the same archive contour.
3. Preserve provenance: answers should cite attached media and attached messages, not free-generate memory claims.
4. Keep the pipeline resilient: prefer real processing when available, but keep explicit fallback behavior so the full cycle still completes.
5. Acceptance bar is a real full-cycle run through the developed functionality on one named character/persona.

## Minimum feature contour
- Media upload/import.
- People CRUD.
- Episode CRUD.
- Review queue for candidate matching.
- Person→media suggestion.
- Person→messages suggestion.
- Conversation/message import from JSON.
- Episode attachment for media, people, and messages.
- Evidence-backed episode Q&A.
- Jobs visibility for processing steps.
- Simple but working UI that exposes the whole chain.

## Full-cycle acceptance recipe
Use one concrete character and push them through the entire chain:
1. Import media folder.
2. Import conversation JSON.
3. Create person.
4. Run transcription/normalization on imported media.
5. Generate and accept person-media candidates.
6. Generate and accept person-message candidates.
7. Generate and accept episode candidates.
8. Attach person to episode.
9. Attach representative messages to episode.
10. Ask the episode a grounded question and verify that both media and message evidence appear in the answer.

If the user says "используя исключительно разработанный функционал", this full cycle must go through the app's own API/UI flow rather than ad hoc side scripts that bypass product logic.

## Stability rules
- Prefer user-space dependencies over root-only setup when the host lacks passwordless sudo.
- For media preprocessing, use a local packaged `ffmpeg` path when system `ffmpeg` is absent.
- Use real transcription when runtime dependencies are present, but preserve a visible fallback path so processing degrades gracefully instead of breaking the chain.
- Health output should expose runtime capability flags for critical processing dependencies.

## Conversation JSON guidance
Support at least a pragmatic normalized shape:
- top-level `conversation` metadata;
- top-level `messages` list;
- each message with sender, timestamp, and text.

Normalize permissively:
- sender from `sender_name` / `from` / `author` / `sender`;
- text from `text_content` / `text` / `message` / `body`;
- timestamp from `sent_at` / `date` / `timestamp` / `created_at`.

The point is not perfect schema purity; the point is robust import of common exported chat JSON shapes.

## Pitfalls
### Pitfall: declaring success after backend CRUD only
If the user asked for turnkey delivery, CRUD and tests are not enough. Run a real persona through ingest → review → episode → ask.

### Pitfall: building media-only memory retrieval
For family archive use cases, переписки are part of the memory substrate. Add at least JSON ingest and message attachment early.

### Pitfall: brittle processing dependencies
Do not make the full product chain depend on system-wide packages when a user-space packaged alternative exists.

### Pitfall: answers without provenance
Do not present reconstructed memory text without attached evidence from media/messages.

## References
- `references/conversation-json-and-evidence-patterns.md` — compact implementation notes for importing chat JSON and folding message evidence into episode Q&A.
