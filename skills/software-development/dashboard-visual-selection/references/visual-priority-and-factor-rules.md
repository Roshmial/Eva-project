# Visual priority and factor rules

Captured from a live Hermes Web dashboard-fix session.

Durable lessons:

- Prefer visual-first dashboards over text-heavy section stacks.
- For market-share / composition requests, when there are roughly 3–8 categories and ratios sum close to a whole, prioritize `pie_list`/donut-style composition near the top.
- Keep `bar_list` as a secondary precision view rather than the only chart for share splits.
- If the user asks for factor analysis and the data includes weights, influence, priority, or approximate ratios, produce a dedicated visual section for factors (`bar_list`, `bubble_list`, or `pie_list`) instead of only a text list.
- Backend normalization may safely enrich a sparse model payload by synthesizing share/factor visuals from structured numeric items, as long as it does not invent numbers.
- Selection policy should rank visual sections ahead of `text_list` for market/comparison/trend dashboards when quantitative structure is available.

Implementation pattern that worked:

1. Tighten blueprint priorities so visual blocks come before text blocks.
2. Add post-normalization heuristics that detect share-like sections and factor-weight sections.
3. Auto-insert missing visual sections from existing structured data.
4. Reorder sections by weighted priority so the most meaningful visuals surface first.
5. Lock behavior with a smoke test that asserts pie priority for market-share dashboards and a factor visual when weights exist.
