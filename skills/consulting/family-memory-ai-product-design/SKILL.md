---
name: family-memory-ai-product-design
description: Use when designing AI family-memory/archive products.
version: 1
---

# Family Memory AI Product Design

## When to use

Use this skill when the user wants to design or evaluate a product in one of these spaces:
- family archive with AI assistance;
- living photo / living portrait;
- memory playback or re-experiencing moments;
- memorial or intergenerational story products;
- conversational archives built from photos, videos, audio, and captions.

This skill is especially useful when the user is exploring a product concept and needs a realistic MVP framed around current open-source and local-first capabilities rather than broad speculative AI promises.

## Core product framing

Default to this framing first:
- the product is a family memory archive;
- the core value is re-experiencing moments with important people;
- the system should preserve and surface real materials;
- the conversational layer is supportive and bounded, not the main value proposition.

Do not default to "digital human", "digital twin", or "AI resurrection" framing unless the user explicitly insists on that direction.

## Primary design choice: episode-first vs person-first

For family-memory products, consider episode-first as the default MVP shape.

Why episode-first often wins:
1. emotionally it matches how people remember — not a person in the abstract, but a scene, trip, holiday, dinner, summer, room, laugh, or period;
2. technically it is easier to ground in real media and metadata;
3. it reduces pressure to simulate a whole personality;
4. it lowers hallucination and ethical risk;
5. it fits archival structure better than a pure person-card model.

Recommended default entities:
- episode / memory unit;
- participants;
- photos / video / audio;
- time / place / captions;
- reconstructed memory scene;
- supported prompts / questions;
- provenance links back to real source material.

Use person-first only when the user explicitly wants the product center to be a persistent character/avatar rather than moments.

## Product layers

Separate the system into layers:
1. source archive layer — raw photos, videos, voice, text, dates, places;
2. organization layer — people, episodes, periods, tags, validation;
3. reconstruction layer — keyframes, face clusters, transcripts, embeddings, candidate memory scenes;
4. presentation layer — living portrait, living scene, timeline, gallery, "revisit this moment" screen;
5. bounded conversation layer — answers only from grounded material;
6. permissions/privacy layer — who can see, edit, approve, and share.

Do not design the product as "just an LLM chat with media attached".

## What belongs to the user vs the AI

Default split:

### User responsibilities
- choose which memories matter;
- define episode boundaries;
- upload media;
- label people, dates, places, and context;
- confirm resemblance and emotional accuracy;
- approve whether a generated scene or voice feels acceptable;
- decide privacy and family-sharing rules.

### AI responsibilities
- extract frames/audio/transcripts;
- cluster faces and suggest matches;
- propose which media belong to one episode;
- generate candidate living portraits or living scenes;
- surface related episodes and searchable context;
- answer short grounded questions from preserved material;
- say clearly when data is missing.

Hard rule:
- user owns meaning;
- AI assists with extraction, reconstruction, search, and presentation.

## MVP default

Recommended MVP for this class:
- one local archive;
- one family or one small household;
- episode-first structure;
- 1-3 participants per episode is enough;
- ingest photos, video, optional voice;
- manual confirmation everywhere meaning matters;
- living scene generation from the best grounded materials;
- limited chat only about that episode or directly linked episodes.

### MVP outputs
- timeline of episodes;
- one living-memory scene per episode or selected episodes;
- one or more living portraits tied to real source sets;
- short grounded answers like "who is here", "what was happening", "when was this", "show related moments";
- explicit fallback: "данных недостаточно" when unsupported.

## Local-first and open-source default

Prefer the current local stack and open-source components before suggesting outside services.

Typical building blocks:
- Python backend;
- local file storage for originals and derived assets;
- SQLite or DuckDB for metadata;
- ffmpeg for frame/audio extraction;
- faster-whisper for transcription;
- local embeddings + FAISS/SQLite/other local index for retrieval;
- open-source face clustering / verification tools;
- open-source portrait animation / lip-sync models for short clips.

Do not promise polished real-time avatars unless the user explicitly accepts the heavier runtime and quality risk.

## What not to put into MVP by default

Avoid these as core v1 requirements:
- unrestricted free-form chat in the voice of the person;
- whole-person simulation across all topics;
- confident answers about motives, beliefs, or advice the person never expressed;
- full-body avatar systems;
- heavy 3D presence;
- social feed / network mechanics;
- cloud-first architecture when a local archive is viable.

## Evaluation criteria

Judge the MVP by these questions:
- does it feel recognizably tied to real memories;
- does it preserve provenance back to the actual media;
- does it help the family find and revisit moments faster;
- do generated scenes feel like memory support rather than deepfake spectacle;
- does the system avoid speaking beyond what the archive justifies;
- can users correct and curate the result without fighting the product.

## Scenario framing

When the user asks for a product concept, separate three scenarios:

### 1. Living photo / living portrait
Best for fast demo value.
Pros:
- visually immediate;
- emotionally legible;
- easier MVP.
Risks:
- can stay shallow;
- can look gimmicky without archive depth.

### 2. Re-experience a memory
Best default family-archive scenario.
Pros:
- stronger archival meaning;
- better grounded in episodes;
- easier to bound ethically.
Risks:
- requires more metadata and curation;
- heavier ingest pipeline.

### 3. Conversational avatar of a loved one
High-risk advanced scenario.
Pros:
- strong wow effect;
- richer interaction.
Risks:
- largest hallucination and expectation gap;
- easiest to slip into "this is pretending to be the person".

Default recommendation:
- build scenario 2 first;
- use scenario 1 as an entry feature;
- delay scenario 3 until grounding, provenance, and permission logic are strong.

## Pitfalls

### Pitfall: person-first framing creates the wrong expectation
If the design starts from "recreate the person", users expect whole-person simulation. That expands scope, raises ethical stakes, and makes every error feel uncanny.

Fix:
- start from moments, episodes, and preserved materials.

### Pitfall: letting the chat layer become the product
If the archive becomes only a prompt source for an LLM, the real asset — family memory structure — gets flattened into generic conversation.

Fix:
- keep episodes, participants, media, and provenance as first-class entities.

### Pitfall: AI decides emotional truth
The system may confidently infer relationships, motives, or emotional meaning from sparse media.

Fix:
- user confirms meaning;
- AI only proposes candidates and grounded summaries.

### Pitfall: one blended face across years and contexts
Mixing all photos of a person into one canonical output often erases period-specific recognizability.

Fix:
- support period-specific or episode-specific variants;
- ask the user which version feels right.

### Pitfall: unrestricted dialogue breaks trust
Free-form roleplay answers quickly cross the boundary from memory support into fabrication.

Fix:
- retrieval first;
- short bounded answers;
- explicit "нет данных" fallback.

## Output pattern for advisory replies

When helping the user on this topic, prefer this structure:
1. the core product framing;
2. recommended MVP boundary;
3. what AI does vs what users do;
4. required components;
5. main risks and why they matter;
6. one concrete next build step.

## References

Add session-specific notes under `references/` when a concrete market scan, architecture option set, or media-pipeline comparison is produced.
