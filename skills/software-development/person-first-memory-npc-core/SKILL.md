---
name: person-first-memory-npc-core
description: Use when archive value must come from a person-first NPC.
created_by: agent
version: 1
---

# Person-first memory NPC core

## When to use

Use this when:
- a family-memory or recollection product already has the base archive contour;
- the user says the current result feels like `just organized folders`, `a weak Apple Memories clone`, or `not enough user value`;
- the next step should be a person-centered experience rather than more ingest plumbing;
- the user wants a `живой образ` or limited `npc` grounded in photos, notes, and conversations.

## Core product rule

Keep `episode` as the storage/retrieval unit, but move `person` to the main user-facing entry point.

The product should answer questions like:
- how this person shows up in the archive;
- which episodes best express their image;
- what themes recur around them;
- what quotes and discussion traces support that image;
- what the user should open first to reconnect with the memory.

## What the core should feel like

Good:
- a constrained memory guide;
- a warm but bounded image of the person;
- replies that sound like `memory through evidence`, not like a general chatbot;
- suggestions for the next memory or scene to open.

Bad:
- a generic gallery of media cards;
- `smart archive` UX that mainly proves indexing happened;
- free persona chat that invents traits or memories beyond the stored material;
- a presentation deck substituting for live product value.

## Preferred runtime contour

1. Person page / person selector.
2. Short portrait assembled from confirmed episodes and discussion traces.
3. Episode cards with:
   - title;
   - why the moment matters;
   - who appears;
   - supporting media count;
   - message quotes.
4. Limited NPC-style chat endpoint.
5. Evidence block in every reply.
6. Suggested next memories to open.

## Reply discipline for the NPC

The NPC is not a digital twin.

It should:
- stay inside confirmed archive evidence;
- reuse wording from discussions and notes where possible;
- explicitly ground the reply in episodes, quotes, and media;
- refuse to invent character traits not supported by the archive.

Useful reply frame:
1. `If we stay only with confirmed materials...`
2. short image of the person;
3. 1–2 matching episodes;
4. 1–2 supporting quotes;
5. one sentence about the limit: this is memory by traces, not fantasy.

## User-specific delivery lesson

For this user, a memory product is not accepted as `core` when it only gives:
- better ingestion;
- folder-like archive structure;
- multimedia highlights without meaning;
- presentation artifacts instead of live UI and actual system replies.

When showing progress, prefer:
- the working UI link;
- factual example replies from the running system;
- a short judgment of how much the result feels like a living image of the person.

Do not keep dragging a separate presentation/deck artifact unless explicitly asked again.

## Pitfalls

### Pitfall: stopping at archive competence
A system that can import, group, and search materials is still only archive infrastructure unless it produces a person-centered memory experience.

### Pitfall: copying Apple Memories without Apple's payoff
If the output is mainly multimedia picks, it will feel like a worse Apple-style recap unless you replace visual payoff with stronger meaning, quotes, and person-centered interpretation.

### Pitfall: voice without grounding
A vivid-sounding NPC that is not clearly tied to episodes, quotes, and media becomes fake quickly.

### Pitfall: backend pride instead of user value
Do not report CRUD, imports, and schemas as if they were the user-facing result. Show what the user can now ask, read, or revisit.

## References

Add session-specific examples of grounded person portraits, good/bad NPC replies, and ranking heuristics for `what to open first` under `references/`.
