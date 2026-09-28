# Semantic baseline sprint verification

Use this pattern when the user asks for a sprint/phase to be done "под ключ" and the work is not just feature coding but product-semantic hardening: statuses, entity boundaries, result semantics, fallback behavior, or backend/frontend contract cleanup.

## Goal

Convert a draft/product-definition sprint into an implemented baseline, not just a document bundle.

## Minimum closure pattern

1. Product docs:
- acceptance/contract draft;
- entity glossary or equivalent;
- status/fallback rules;
- one implementation-baseline document that says what was really wired into code.

2. Backend:
- expose user-visible semantics from serializers/API payloads instead of leaving raw internal states only;
- prefer explicit fields like `public_status`, `result_kind`, `entity_kind`, `surface`, `delivered_count`, `has_error` when they remove frontend guessing.

3. Frontend:
- consume the new semantics in the actual screens the user sees;
- replace raw/internal status display with normalized user-facing values;
- show the distinction between response/file/artifact/clarification/job-result when the payload now supports it.

4. Regression:
- add at least one focused test for the exact new semantic layer;
- do not rely only on broad existing smoke suites if they already contain unrelated red tests.

5. Live verification:
- run syntax/build checks;
- run the focused semantic tests;
- verify at least one real API/runtime path using the new fields.

## Clean-runtime fallback for honest verification

If the existing local operational DB fails startup because of old demo/seed collisions or other legacy contamination:
- do not present the feature as unverified;
- do not rewrite the task into a DB-cleanup task unless that was actually requested;
- start an isolated temporary runtime with a temp data dir / temp DB;
- verify the new contract on that clean runtime;
- report the legacy DB contamination separately as a pre-existing runtime hygiene issue.

This keeps the reporting honest:
- new semantic baseline verified;
- legacy local DB still needs cleanup.

## Reporting boundary

Good final framing:
- what is now implemented in backend/frontend/docs;
- what was verified by real commands/runtime;
- what remains red but is outside the sprint scope;
- which browser/runtime/tooling issues are separate infrastructure layers rather than proof that the product change failed.
