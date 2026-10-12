---
name: local-first-archive-ingest-hardening
description: Use when a local-first archive adds a new ingest type.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Local-First Archive Ingest Hardening

Use this skill when a local-first archive or knowledge-base product adds a new source type such as chats, notes, call logs, scans, or media sidecars, and the user expects more than a one-off demo.

Typical triggers:
- "доделай под ключ"
- "нужно в итоге хорошо"
- "подключи ещё один тип данных"
- "полный цикл должен отработать"
- the new source already imports once, but replay safety and product-level quality are not yet closed.

## Goal

Land the new ingest contour so it is:
- safe to rerun;
- integrated into the same review/retrieval/answering surface as existing data;
- proven by one real end-to-end scenario.

## Core rule

A new ingest modality is not really done when it only imports successfully once. For archive products, minimum acceptable quality is:
1. import works;
2. repeated import is idempotent or explicitly deduplicated;
3. existing duplicates are reconciled when feasible;
4. the new evidence participates in search;
5. the new evidence can be linked to the main domain entities such as episodes/people/cases;
6. evidence-backed answers can cite it;
7. one real scenario proves the full contour.

## Preferred implementation order

1. Add storage tables for the new source.
- Keep raw payload available enough for later reprocessing.
- Also store normalized fields needed for search and UI.

2. Add deterministic import identity.
- Prefer source hash, external message IDs, or another stable source identity.
- Return whether the import was deduplicated.

3. Make replay safe.
- Re-importing the same file should not create duplicate top-level entities.
- If older rows predate the fix, add a lightweight reconciliation step on startup or migration.

4. Wire the new source into the same working surface.
- list endpoint
- search endpoint
- review/suggestion flow
- attach/link flow to the primary entity
- final answer path

5. Verify with one live scenario.
- Import the new source.
- Attach it to a real primary entity.
- Query through the user-facing path.
- Confirm that the answer cites both old and new evidence types when relevant.

## Concrete pattern for chat/message JSON

For chat JSON imports, a practical baseline is:
- `conversations` table for top-level imports;
- `conversation_messages` table for normalized messages;
- bridge table from domain entity to messages, for example `episode_messages`;
- `source_sha256` or equivalent stable import identity on the conversation;
- import response field like `deduplicated: true|false`;
- reconciliation that merges old duplicate conversations into one canonical row when possible.

## Verification checklist

Do not report completion until all of these are checked:
- import endpoint works on a real file;
- repeated import does not multiply rows;
- existing duplicates are either cleaned or clearly blocked by risk;
- search returns the new source;
- the primary entity details page includes the new linked records;
- evidence-backed ask/QA includes the new source in the answer;
- automated test covers the new source end to end.

## Pitfalls

### Pitfall: stopping at first successful import
Symptom:
- the JSON file imported once, so the feature is declared done.

Why this fails:
- archives are replay-heavy systems; duplicate imports silently degrade trust and usability.

Correction:
- add deterministic dedupe and prove it with repeated import.

### Pitfall: adding a source as storage only
Symptom:
- new rows land in the DB, but the user cannot find or use them in the same product flow.

Correction:
- wire the source into search, detail view, linking, review, and final answer paths in the same pass.

### Pitfall: fixing future imports but leaving old duplicates behind
Symptom:
- new imports dedupe correctly, but the archive already contains duplicate rows from earlier runs.

Correction:
- add a small reconciliation step or migration that consolidates old duplicates into one canonical entity and rewires links.

## Output style

Report briefly:
- what was hardened;
- what replay-safety rule was added;
- what full-cycle scenario was proven;
- what remains open, if anything.
