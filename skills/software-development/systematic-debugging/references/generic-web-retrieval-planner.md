# Generic web retrieval planner: lessons from live debugging

Use this note when debugging or redesigning topic-agnostic web collection / research retrieval.

## Core decisions

- Do not add subject-specific branches like `if BI ...`.
- Keep planner topic-agnostic and intent-aware.
- Prefer broad subject-first queries for ordinary internet research.
- Keep quoted / exact-like queries as later fallback, not first pass.
- Score candidate sets, not just the best single URL.
- Validate breadth as well as relevance; a small top-N cap can hide quality problems.

## Durable implementation patterns

1. Split the retrieval path into layers:
   - subject extraction / normalization
   - intent detection
   - query-family generation
   - candidate-set scoring
   - post-fetch document filtering

2. Test genericity on unrelated topic classes:
   - enterprise / BI history
   - consumer / automobiles history
   - market-overview / LegalAI

3. For camelCase or compressed product names, prefer humanized variants early:
   - example pattern: `Legal AI` before `LegalAI`

4. For short acronym handling, use boundary-aware matching.
   - Avoid substring false positives like `ai` matching inside unrelated words.

5. For mixed-script or acronym-heavy subjects, inspect the generated query family, not just the chosen documents.
   - Check `subject_terms`, ordered `subject_phrases`, and the first several generated queries.
   - Prefer a clean broad phrase built from expanded multiword terms (for example `business intelligence`) before malformed hybrids like `BI-инструментов` or acronym+expansion duplicates like `bi business intelligence`.
   - If a condensed phrase builder and an acronym-expansion builder conflict, make the fully expanded multiword phrase the first broad query.

6. Score candidate sets with explicit weak-set penalties.
   - Penalize sets where no URL has positive topical signal, even if the set is non-empty.
   - Penalize generic/training/profile/help/support/landing pages both before fetch and after fetch.
   - Keep short but topically valid reference pages eligible; do not over-penalize paths like `/topics/` if they still carry subject hits.

7. Compare local and live candidate sets when the search backend is noisy.
   - The same planner may look healthy locally but receive radically different search results on the live host.
   - Probe server-side `build_web_search_queries()`, `search_web_source_candidates()`, and `score_web_candidate_set()` directly on the target contour before blaming post-fetch ranking.

8. Inspect selected-source count explicitly.
   - Do not trust only preview arrays capped at 5 rows.
   - Confirm the full selected-source count after ranking and dedupe.

## Pitfalls

- Early exact quoting can starve the search space and make the planner look brittle.
- A first-nonempty result policy hides better later query families.
- A 5-source cap may be too narrow for history and market-overview tasks.
- Preview-only diagnostics can make an 8-source selection look like 5 if the probe truncates output.

## Useful acceptance checks

- Broad query appears before quoted fallback.
- No topic-specific hardcode remains in planner branches.
- Expanded source limit propagates through search, ranking, fetch, and final metadata.
- At least one unrelated topic still works after the fix.
