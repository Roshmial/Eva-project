---
name: episode-first-memory-archive-mvp
description: Use when building a local-first family memory archive MVP.
created_by: agent
version: 1
---

# Episode-first memory archive MVP

## When to use

Use this when the user wants to build a family-memory or recollection product from photos, videos, audio, and notes, especially when:
- the product value is `relive memories` rather than `talk to a digital person`;
- the available infra is modest;
- the user prefers local-first / open-source / minimal extra infrastructure;
- the task is to ship an MVP now, not speculate about a full avatar stack.

## Core product rule

Default to an episode-first architecture, not a person-first digital twin.

Why:
- users often remember moments and periods more vividly than an abstract person profile;
- episode-first framing avoids premature expectations of a full simulated personality;
- it lowers ethical risk and hallucination risk;
- it fits a modest-server MVP much better.

Primary entity order:
1. episode / moment / period;
2. media attached to the episode;
3. participants in the episode;
4. evidence-backed search and Q&A;
5. only later: visual relive / portrait animation.

## MVP boundary

For a base-layer MVP, include:
- media ingest;
- local storage for originals and derived assets;
- metadata DB;
- people CRUD;
- episodes CRUD;
- attach media to episodes;
- search across archive materials;
- constrained Q&A inside an episode;
- simple review UI;
- provenance / evidence discipline.

Do not include by default in v1:
- free-form persona chat;
- digital-twin claims;
- voice cloning as a core feature;
- heavy video generation;
- always-on talking portrait;
- complex social/family sharing layers.

## Architecture pattern

### Control plane
Use a small Python web stack for:
- FastAPI backend;
- SQLite or DuckDB metadata DB;
- local file storage;
- simple web UI;
- background jobs for ingest and indexing.

### Data layout
Recommended top-level dirs:
- `data/originals/`
- `data/derived/`
- `data/transcripts/`
- `data/embeddings/`
- `data/db/`
- `logs/`

Recommended tables/entities:
- `people`
- `episodes`
- `media_items`
- `episode_media`
- `episode_people`
- `transcript_segments`
- `jobs`
- optional later: `face_clusters`, `memory_scenes`

### Retrieval rule
Use retrieval-first, generation-second.

Q&A flow:
1. identify the episode scope;
2. retrieve matching media / notes / transcript segments;
3. answer briefly from evidence;
4. if evidence is weak, say so directly.

Never let the model invent biographical facts or speak freely `for the person` in the base layer.

## Resource-sizing rule

If the target host is modest and GPU-free, treat it as a base-layer MVP host, not as a full media-generation host.

A host in the rough class of:
- 8 vCPU
- ~16 GiB RAM
- no GPU
is usually enough for:
- backend/API;
- metadata DB;
- media catalog;
- light preprocessing;
- search/retrieval;
- simple review UI.

It is usually not enough for:
- strong talking-portrait generation;
- scalable lip-sync/video generation;
- large-archive heavy video processing.

Default conclusion on such hardware:
- ship MVP light on the host now;
- defer heavy visual generation to a later GPU worker contour.

## User-workflow split

### User does
- choose meaningful episodes;
- confirm people;
- add dates/places/notes;
- approve or reject AI suggestions;
- decide what counts as `similar enough` and `important enough`.

### AI does
- ingest and indexing help;
- suggest episode groupings;
- extract thumbnails/keyframes/transcripts when available;
- assist with search;
- produce evidence-backed short answers.

## Delivery discipline

When the user says `сделай под ключ` and the target host is explicitly named:
- do not stop at architecture talk;
- deploy a working base contour on that host;
- run tests there;
- run at least one live API probe there;
- report only what is actually running.

## Pitfalls

### Pitfall: starting from the digital-person fantasy
Symptom:
- the design drifts into personality simulation, long dialogues, or `what would he say` features too early.

Correction:
- re-anchor on episode, archive, evidence, and review.

### Pitfall: over-investing in visual magic before archive structure exists
Symptom:
- animation, portrait, and voice layers are discussed as core while ingest, episode assembly, and provenance are still weak.

Correction:
- base-layer usefulness first;
- visual relive later.

### Pitfall: treating a modest host like a media-generation workstation
Symptom:
- the plan assumes heavy video generation on a no-GPU server.

Correction:
- scope the host to MVP light and postpone the heavy worker contour.

### Pitfall: answering archive questions without evidence discipline
Symptom:
- the assistant gives a smooth memory answer not clearly grounded in the stored materials.

Correction:
- retrieval-first answer shape with explicit evidence or an explicit `данных недостаточно`.

## References

Add session-specific implementation examples, API shapes, and deployment contours under `references/` when a concrete delivery path is proven on a real target host.
