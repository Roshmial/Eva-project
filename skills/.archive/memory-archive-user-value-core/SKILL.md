---
name: memory-archive-user-value-core
description: Use when a memory archive MVP feels like smart storage.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Memory Archive User-Value Core

## When to use

Use this skill when building, reviewing, or redirecting a family archive, memory archive, or memory-AI MVP and the current result is technically functional but feels like:
- smart storage;
- better tagging/search;
- nicely grouped media;
- an Apple Memories imitation without equivalent polish or emotional payoff.

Typical trigger phrases:
- "Нужен рабочий core, с доставкой ценности"
- "Это просто архив"
- "Похоже на плохую версию подборок Apple"
- "Нужен образ человека"
- "Хочу не файлы, а воспоминание / событие / обсуждение"

## Core rule

If the product currently delivers mainly ingest, storage, search, clustering, or media grouping, do not present that as the product core.

For this class of product, infrastructure is necessary but not sufficient. User value appears only when the system outputs a human-meaningful object, not a storage object.

## Product test

Ask:
1. What does the user get back immediately after import?
2. Is that object something a person actually wants to revisit?
3. Does it answer "why should I come back here"?

If the answer is mostly:
- folders;
- files;
- grouped photos;
- media cards;
- generic highlights;
then the value core is still missing.

## Preferred value objects

Prioritize one of these as the first-class output:

### 1. Person-first portrait
Best when the user wants an "образ" человека.

Output should include:
- who this person appears to be in the archive;
- confirmed episodes involving them;
- recurring themes around them;
- 1-3 quotes from chats/messages;
- the best supporting media;
- a concise portrait text grounded in evidence.

### 2. Episode-with-meaning card
Best when the user wants memories as scenes/events.

Output should include:
- episode title;
- why it matters;
- who is involved;
- what evidence supports it;
- a short preview/narrative;
- key quotes/messages;
- best media from the episode.

### 3. Guided revisit
Best when the user wants immediate action.

Output should include prompts like:
- 5 important moments with this person;
- what to revisit first;
- scenes related to a recurring topic;
- what the archive repeatedly remembers about the person/event.

## Decision rule

If forced to choose between:
- improving ingest/metadata quality, or
- surfacing a stronger user-facing memory object,
prefer the user-facing object once the basic pipeline already works.

## Anti-patterns

### Anti-pattern: smart archive presented as product
Symptoms:
- strong CRUD and import pipeline;
- weak first screen;
- user reaction: "это просто архив".

Correction:
- stop adding backend-only value as if it were product value;
- implement a first-class person or episode surface.

### Anti-pattern: bad Apple Memories clone
Symptoms:
- multimedia highlights are polished but generic;
- grouped media is the main output;
- the system offers less emotional payoff than consumer photo apps.

Correction:
- do not compete on montage/gallery alone;
- compete on meaning: person, relationship, event, discussion, recurring themes.

### Anti-pattern: media-first highlights
Symptoms:
- cards are essentially files with nicer labels;
- the user still has to infer the memory.

Correction:
- replace media cards with memory cards or person cards;
- media becomes evidence, not the product object itself.

## Recommended implementation order

1. Keep the existing local-first ingest/retrieval core.
2. Add person story endpoint/surface.
3. Add episode cards with meaning and quotes.
4. Add "what to revisit first" ranking.
5. Only after that invest further in OCR, face clustering, or richer semantics unless those are blocking the surfaced value object.

## User-specific lesson embedded

For this user, a family-memory product should not stop at:
- "умно разложил по папкам";
- media highlights;
- generic gallery curation.

A more correct direction is:
- person-first;
- event discussion as evidence;
- an "образ" человека through episodes and conversations.

## Deliverable standard

A good intermediate delivery should let the user say:
- "Теперь я вижу, как в архиве проявляется человек"
not merely:
- "Теперь архив лучше организован".

## References

Add session-specific examples, prompts, and real output patterns under `references/` when you discover useful shapes for person portraits, episode cards, or revisit ranking.
