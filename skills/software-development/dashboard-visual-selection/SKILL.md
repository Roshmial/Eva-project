---
name: dashboard-visual-selection
description: Choose and enrich Hermes-style dashboard sections so outputs stay visual-first, especially for market-share and factor-analysis requests.
---

# Dashboard visual selection

Use this skill when a Hermes or local-first dashboard pipeline already supports multiple section kinds, but the actual outputs are too text-heavy, repetitive, or choose the wrong chart type for the analytical question.

## When to use

- Users complain that dashboards look like text piles instead of visual dashboards.
- The backend already supports several section kinds (`pie_list`, `bar_list`, `bubble_list`, `timeline_list`, `matrix_list`, `text_list`) but selection quality is weak.
- Market-share / composition prompts keep producing bars or text when a pie/donut view is more natural.
- Factor analysis is returned as prose or bullets even though the factors have weights, priorities, or relative influence.
- You need a backend-side normalization/enrichment layer that improves model output without inventing facts.

## Core rules

1. Prefer visual-first composition.
   - When quantitative structure exists, visual sections should appear before long text sections.
   - Text should explain, qualify, or add evidence — not dominate the dashboard.

2. Match the chart to the question.
   - Share/composition/distribution across a small set of players: prefer `pie_list` or donut-style composition near the top.
   - Exact ranking/comparison: use `bar_list`.
   - Change over time: use `timeline_list` and optionally `bar_list`.
   - Segment × criterion comparisons: use `matrix_list`.
   - Factors with weights/influence: add a visual factor block (`bar_list`, `bubble_list`, or `pie_list`) instead of only text.

3. Enrich from existing structured data, never from imagination.
   - If a section already has labels plus ratios/percentages, backend normalization may synthesize an additional visual section.
   - Do not invent new numbers; only transform existing structured values into a better view.

4. Reorder after normalization.
   - First normalize payloads.
   - Then add any safe derived visuals.
   - Then reorder sections by analytical priority so the most meaningful visuals are seen first.

## Practical heuristics

### Market-share / composition heuristic

If all of the following are true:
- there are about 3–8 categories,
- each item has a usable ratio/percentage/value,
- totals are reasonably close to a whole,

then:
- add or prioritize a `pie_list` section,
- keep `bar_list` as a secondary precision view if useful,
- place the composition chart before text-heavy explanation blocks.

### Market-overview anti-bias heuristic

If the analytical intent is `market_overview`, do not reuse history-style fallback sections by default.

Prefer sections about:
- players / brands / vendors,
- market signals,
- positioning,
- pricing/product accents,
- constraints or caveats.

Avoid generic history scaffolding like:
- `Ключевые этапы и поворотные точки`
- `Смена практик и подходов`

unless the request truly contains history/evolution markers.

A practical fallback pattern for market-overview is:
- first visual section: `bar_list` with market signals or players,
- supporting section: `text_list` with concise conclusions,
- optional comparison/matrix only when the source content actually compares segments or criteria.

### Factor-analysis heuristic

If a factor section has:
- explicit weights,
- relative importance,
- influence scores,
- approximate percentages or ratios,

then:
- create a dedicated visual factor section,
- keep the original explanatory text only as supporting context,
- ensure the factor visual appears above or alongside the text explanation.

## Recommended implementation pattern

1. Write a failing test first.
2. Update dashboard blueprint priorities so visual blocks outrank `text_list` where appropriate.
3. Add a post-normalization pass that detects:
   - share-like sections,
   - factor sections with weights.
4. Auto-insert derived visual sections from the already-structured items.
5. Reorder sections with a weighted priority function.
6. Run the focused test, then the full smoke suite.
7. Restart the affected backend/runtime and verify health.

## Verification checklist

- A market-share request with top-N players yields a composition visual near the top.
- Factor analysis with numeric weights yields both explanation and a visual factor block.
- Visual blocks appear before verbose text blocks when quantitative structure exists.
- No derived visual introduces numbers absent from the original structured data.
- Existing smoke tests still pass.

## Reference

See `references/visual-priority-and-factor-rules.md` for the concrete lessons and implementation pattern captured from a live Hermes Web dashboard-fix session.
