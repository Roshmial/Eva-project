# Intent-aware contentful fallbacks

Session lesson: a dashboard can be structurally valid and still be product-wrong if fallback sections expose backend mechanics instead of analytical content.

## Problem signature

Typical bad fallback patterns:
- `Минимальная визуализация` with only source label / route / policy token;
- summary cards dominated by `source_mode`, `global_only`, connector names, or routing metadata;
- `market_overview` rendered with history-style blocks like `Смена практик и подходов`;
- `history_evolution` duplicating the same content in both timeline and matrix;
- `comparison` falling back to generic text when the real missing piece is a criteria matrix;
- `evidence_board` showing generic visualization instead of confirmed evidence and gaps.

## Durable fix pattern

1. Keep the outer dashboard envelope stable.
2. Move fallback intelligence into an intent-aware normalization layer.
3. Make fallback cards/sections describe the analytical question, not the transport/runtime internals.
4. Prefer honest weak-content boards over fake quantitative visuals.

## Minimal fallback targets by intent

### market_overview
Use:
- summary cards about market focus, source family, and analytical constraints;
- first meaningful section about players / brands / market signals / positioning;
- supporting conclusions and caveats.

Avoid:
- history scaffolding unless the query explicitly asks for evolution/history.

### comparison
Use:
- `matrix_list` for criteria and differences;
- text only as summary/support;
- explicit trade-offs or incompleteness when evidence is partial.

Avoid:
- burying the comparison matrix below generic text blocks.

### trend
Use:
- chronology / turning points / drivers;
- timeline before generic filler;
- quantitative visuals only when backed by real slices.

### segmentation
Use:
- segment definitions, distinguishing criteria, and caveats about uncertain boundaries.

### history_evolution
Use:
- `timeline_list` for stages;
- `matrix_list` for a different lens such as role, architecture, operating model, or adoption pattern.

Avoid:
- duplicating stage text nearly verbatim across both sections.

### evidence_board
Use:
- `post_list` or evidence-style cards for confirmed items;
- separate gap section for what is still missing;
- explicit honesty about coverage.

Avoid:
- generic placeholder charts whose only purpose is to look visual.

## Verification hints

Check not only that sections exist, but that they are semantically right for the intent:
- market asks should mention players/signals, not practices;
- comparison should surface criteria;
- evidence should surface confirmations and gaps;
- history should not say the same thing twice in timeline and matrix.

When testing, add regressions that fail on semantic anti-patterns (`Минимальная визуализация`, routing-token cards, duplicated timeline/matrix payload), not only on missing JSON fields.
