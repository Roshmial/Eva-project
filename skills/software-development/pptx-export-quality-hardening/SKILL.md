---
name: pptx-export-quality-hardening
description: "Hardening backend PPTX export pipelines with intake analysis, planner signals, read-back validation, semantic checks, and quality gating."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [pptx, export, backend, validation, quality, testing]
    related_skills: [artifact-delivery-contract-hardening, test-driven-development, file-artifact-intent-routing]
---

# PPTX Export Quality Hardening

## When to use

Use this skill when a backend already generates `.pptx` files, but the export path is too "fire and forget" and needs real quality controls.

Typical triggers:
- the pipeline can generate PPTX, but output quality is inconsistent;
- the system needs to understand an incoming source deck before planning a new deck;
- the planner should react to dense source material instead of treating every presentation like greenfield content;
- the export path needs machine-readable validation and degradation signals;
- you need to improve a PPTX core incrementally without replacing it with a separate designer pipeline.

## Goal

Turn a plain PPTX generator into a self-checking backend export contour:

1. inspect source deck structure;
2. derive routing/planning signals;
3. derive density/capacity signals;
4. use those signals inside planning;
5. generate the PPTX;
6. read it back and validate the produced artifact;
7. summarize quality as `ok` / `degraded` / `failed`.

## Default approach

Prefer strengthening the existing local backend core first.
Do **not** jump straight to a separate redesign pipeline or external service.

Sequence:
1. add narrow failing tests first;
2. add the smallest new signal/helper layer that makes those tests pass;
3. thread the signal into existing planning/render code with minimal blast radius;
4. re-run targeted tests;
5. re-run broader regressions around export/planning/intake.

## Recommended architecture layers

### 1) Source-deck intake

Build an intake bundle for incoming `.pptx` files with normalized slide inventory.

Minimum useful fields:
- `slide_count`
- `aspect_ratio`
- `slides[]`
- per-slide `page_type`
- `slots[]`
- `text_metrics`
- `text_summary`

The backend should not treat source PPTX as an opaque binary if later planning depends on its structure.

### 2) Route signals

Derive planner-facing route signals from the intake bundle.

Useful signals:
- `source_deck`
- `template_candidate`
- `dense_source_deck`
- `prefer_compact_structure`

Use them to change planning behavior safely, for example:
- suppress title preview for source-deck/template-like flows;
- suppress synthetic overview slides when the source deck already implies compact structure.

### 3) Capacity signals

Derive density/capacity signals from slide slots and text metrics.

Useful signals:
- `dense_text_detected`
- `max_slot_chars`
- `max_slot_paragraphs`
- `warning_codes`

Useful warning codes:
- `slot_text_overflow`
- `slot_paragraph_overflow`

At first, use these as planner annotations. Do not over-automate layout changes before the signals are validated by tests.

### 4) Capacity-aware planning

Once capacity signals are trustworthy, let them affect planning behavior.

Good first moves:
- mark slides with `capacity_warning`;
- mark slides with `needs_compaction`;
- choose more aggressive chunk sizes for dense sections;
- allow smaller tail chunks when overflow is real;
- reduce body font size in render path when compaction is explicitly requested.

Important: propagate compaction into real render call sites, not just helper-level tests.

### 5) Read-back validation

After generating `.pptx`, read the artifact back through the same intake parser.

Validation report should be machine-readable and cheap to compute.

Minimum fields:
- `valid`
- `slide_count`
- `text_shape_count`
- `slide_titles`
- `aspect_ratio`
- optional `error_code` / `error`

This separates:
- "we wrote bytes" from
- "we produced a structurally readable presentation artifact".

### 6) Semantic validation

Compare read-back output to planning expectations.

Good first checks:
- expected slide count vs actual;
- required slide titles/sections vs actual read-back titles.

Useful warning codes:
- `slide_count_mismatch`
- `missing_required_titles`

Build expectations from the backend's own `presentation_plan`, not from ad-hoc guesses.

### 7) Quality summary / gating

Summarize structural + semantic validation into a stable quality contract.

Recommended shape:
- `status`: `ok` | `degraded` | `failed`
- `degraded`: bool
- `severity`: `info` | `warning` | `error`
- `warning_codes`: list[str]

Suggested rules:
- structural invalid => `failed`
- structural valid + semantic warnings => `degraded`
- no warnings => `ok`

Return this quality block from the internal export builder even if the outward HTTP/file endpoint still only serves the file buffer.

### 8) Artifact/meta propagation

After `validation` and `quality` exist inside the PPTX builder, propagate them into the real artifact path.

Recommended shape:
- introduce a single internal export-result helper that returns at least `buffer`, and for PPTX also `validation` + `quality`;
- keep the outward stream/download contract unchanged by unwrapping `buffer` where the caller still expects a file-like object;
- attach `validation` + `quality` to the stored attachment payload for `.pptx` exports;
- copy the same fields into top-level `file_response` metadata for generated-file flows and previous-message export flows.

Why this matters:
- backend-only validation is not enough if chat/file delivery surfaces cannot see the result;
- UI/runtime logic needs a stable machine-readable signal near the artifact, not hidden inside a lower-level builder;
- both `generated_file_response` and `message_export` paths should expose the same quality contract.

## TDD workflow for this class of work

Use narrow RED-GREEN cycles.

Recommended sequence:
1. add a failing helper test;
2. add a failing planner integration test;
3. implement minimal helper;
4. thread helper into planner/render path;
5. run targeted tests;
6. run broader PPTX regressions.

Good test categories:
- intake inventory test on a real fixture;
- route-signal test;
- capacity-signal test;
- planner behavior test;
- render/output test;
- read-back validation test;
- semantic validation test;
- quality-summary test.

## Pitfalls

### Do not stop at metadata-only warnings

A common failure mode is adding `capacity_warning` or similar flags that never affect real planning or rendering. If the signal matters, thread it into:
- chunk selection;
- compaction decisions;
- font-size decisions;
- quality summary.

### Do not break outward export contracts casually

It is often useful for the *internal* PPTX builder to return a richer object such as:
- `buffer`
- `validation`
- `quality`

But if the existing export endpoint or stream builder is expected to return only a file-like buffer, preserve that outward contract and unwrap internally.

### Do not invent degraded cases in end-to-end tests that the system itself cannot produce

If semantic expectation is generated from the same `presentation_plan` used to render the deck, a normal generated export will often pass semantic validation. Test degraded quality directly at the helper level when necessary, and test export-level quality as contract presence plus stable status shape.

### Do not let quality stop at the builder boundary

A frequent failure mode is proving that `build_message_export_pptx(...)` returns `quality`, while the actual attachment payload and `file_response` metadata still drop it. Fix this by introducing a single internal export-result helper and reusing it in:
- stream/download builders;
- stored attachment builders;
- generated file reply metadata;
- previous-message export reply metadata.

Test two layers separately:
- helper-level degraded/failed quality logic;
- artifact/meta-level contract presence on real `.pptx` export paths.

### Do not rebuild the whole PPTX stack too early

If the current core is salvageable, prefer incremental hardening over immediate replacement with a separate designer pipeline. Add moving parts only when the current core cannot be made reliable enough.

## Verification checklist

Before finishing:
- targeted new tests fail first;
- targeted new tests pass after the change;
- regression set around intake/planning/export passes;
- read-back validator works on a real fixture;
- semantic validator compares output to planner expectations;
- export builder returns machine-readable quality summary;
- outward file delivery contract remains intact.

## References

- `references/core-validation-layers.md` — compact notes on the layered hardening sequence, warning codes, and testing shape.
- `references/artifact-meta-propagation.md` — how to carry PPTX `validation` / `quality` through attachment payloads and `file_response` metadata without breaking stream/download contracts.
