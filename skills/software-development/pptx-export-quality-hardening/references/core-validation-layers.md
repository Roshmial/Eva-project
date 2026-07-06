# Core validation layers for PPTX export hardening

## Layer sequence

1. Source intake
   - normalize slide inventory
   - extract `slide_count`, `aspect_ratio`, per-slide `slots`, `text_metrics`, `text_summary`

2. Route signals
   - `source_deck`
   - `template_candidate`
   - `dense_source_deck`
   - `prefer_compact_structure`

3. Capacity signals
   - `dense_text_detected`
   - `max_slot_chars`
   - `max_slot_paragraphs`
   - warning codes: `slot_text_overflow`, `slot_paragraph_overflow`

4. Planner integration
   - compact title/overview for source-deck/template-like flows
   - annotate slides with `capacity_warning`
   - annotate slides with `needs_compaction`
   - aggressive chunking for dense sections
   - smaller tails when overflow is real

5. Render integration
   - compaction must reach actual render call sites
   - body font size should respect `needs_compaction`

6. Read-back validation
   - re-open generated PPTX with the same intake parser
   - produce machine-readable report with `valid`, `slide_count`, `text_shape_count`, `slide_titles`, `aspect_ratio`

7. Semantic validation
   - compare actual read-back against planner-derived expectations
   - warning codes: `slide_count_mismatch`, `missing_required_titles`

8. Quality summary
   - `ok` / `degraded` / `failed`
   - `degraded` should be machine-readable, not implied only by prose

## Testing pattern

Preferred RED-GREEN order:
1. helper-level failing test
2. planner/render integration failing test
3. minimal implementation
4. targeted re-run
5. broad regression run

Useful recurring test buckets:
- real fixture intake test
- route-signal unit test
- capacity-signal unit test
- planner compaction test
- render/read-back validation test
- semantic warning test
- quality summary test

## Important test-design note

If semantic expectation is generated from the same plan that drives rendering, end-to-end generated exports may naturally pass semantic validation. In that case:
- test degraded quality directly through helper-level tests;
- test export-level behavior as presence and shape of the `quality` contract.
