# Core PPTX upgrade sequence

Use this reference when the product already has a working-but-fragile PPTX core and the task is to strengthen it without collapsing core and designer-mode into one path.

## Decision rule

Do both:
1. fix the current core pipeline;
2. strengthen it with selected backend components / ideas from `ppt-master`.

Do **not** choose either extreme:
- `only our own current code, ignore stronger upstream components`;
- `replace core with ppt-master as-is`.

## Recommended staged sequence

### Stage 1 — clean the current core path
- remove duplicated parsing/planning branches;
- keep one canonical planning path;
- make the export flow easier to reason about before adding new capability.

### Stage 2 — add source `.pptx` intake
Goal: treat uploaded/existing decks as structured sources, not opaque binaries.

Minimal useful intake bundle:
- `slide_count`
- `aspect_ratio`
- `slides[]`
- per-slide `page_type`
- per-slide `slots[]`
- per-slot text / geometry / text metrics

Practical note: a first-pass intake can read `.pptx` as zip/XML and does not have to depend on the full `python-pptx` render stack.

### Stage 3 — derive route signals from intake
Useful first signals:
- `source_deck`
- `template_candidate`
- `dense_source_deck`
- `prefer_compact_structure`

Expected use:
- compact title/overview behavior for source decks;
- different planning defaults for template-like vs dense-text decks.

### Stage 4 — derive capacity signals
Useful first signals:
- `dense_text_detected`
- `max_slot_chars`
- `max_slot_paragraphs`
- `warning_codes` such as `slot_text_overflow`, `slot_paragraph_overflow`

Expected use:
- mark plan items that need compaction;
- avoid waiting until the final slide render to discover overflow risk.

### Stage 5 — make planning and render path react
At this point warnings must stop being metadata-only.

Minimum useful reactions:
- more aggressive chunking for dense sections;
- compaction-aware `preferred` chunk size;
- smaller minimum tail when dense overflow really warrants `3+1` instead of fake-balanced `2+2`;
- compaction-aware body font sizing in actual render functions.

### Stage 6 — only then add read-back validation and safe publish
Once the pipeline can analyze and react, verify the real output:
- inspect produced `.pptx` after render;
- confirm artifact exists and is readable;
- keep publish semantics honest.

## Where selective `ppt-master` borrowing fits

Good candidates to adapt into core:
- intake / structural analysis patterns;
- deck identity / slide inventory / slot extraction ideas;
- template-aware constraints;
- validation patterns;
- native PPT utility helpers that improve stability.

Poor candidates for the core stream:
- project/workspace orchestration;
- designer-mode user flows;
- beautify/regenerate loops as the default execution path;
- advanced capability-first features (narration, transitions, etc.).

## Testing implications

Regression coverage should span three layers, not just one:
1. helper/intake tests;
2. planning-behavior tests (route + capacity effects);
3. real export tests on generated `.pptx`.

A green helper suite is not enough if the actual render path ignores `needs_compaction` or other planning outputs.
