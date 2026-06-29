# Shared semantic core and source-shape bridging

Context from the session:
- Dataset dashboards had already grown a semantic layer (`v1`..`v3`) with grouped `plan/fact`, concentration across slices, mixed percent normalization, and source-shape labels.
- The next useful step was not another isolated dataset feature, but unifying dataset path and external dashboard path under the same semantic envelope.

What to preserve in future work:
- Treat `business_function`, `analytic intent`, and `source shape` as three separate axes.
- Keep `source shape` as context/provenance, not as dashboard identity.
- External dashboards should reuse the same user-facing cards where possible:
  - `Функция`
  - `Форма источника`
- A richer subtitle such as `source shape: web_structured` is acceptable as a context layer when it does not displace the analytical framing.

Practical implementation pattern:
1. Introduce one shared helper for structured-source classification, not one helper per route.
2. Reuse one `build_source_shape_card(...)` style helper across dataset and external flows.
3. Add a business-function context card to external dashboards instead of treating them as purely source-driven.
4. Feed a shared guidance/reference item into prompt/reference builders before intent- and function-specific guidance.

Intent-detection lesson:
- Market-overview inference needs broader markers than `рынок` alone.
- Useful additions from this session: `market`, `landscape`, `игрок`, `конкурент`, `vendor landscape`, `supplier landscape`, `рыночн`.
- Without them, real market/procurement requests can silently degrade into `evidence_board`.

Verification lesson:
- If test content passes but the process aborts on teardown, separate logical correctness from runner teardown issues.
- Record the content-level pass honestly, then confirm with an alternate minimal runner before concluding the feature is broken.
- Save the verification pattern, not the transient environment complaint.
