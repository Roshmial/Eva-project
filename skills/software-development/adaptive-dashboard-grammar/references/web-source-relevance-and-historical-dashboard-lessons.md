# Web source relevance and historical dashboard lessons

## Trigger

Use this note when a dashboard looks structurally valid but the underlying open-web evidence may be wrong, thin, or polluted.

## What happened

A historical BI dashboard request produced a formally valid `dashboard_result`, but the source set included irrelevant pages such as Google Translate help and unrelated support/product docs. The result looked like a dashboard yet was analytically false because the evidence base was off-topic.

## Durable lessons

1. Separate payload-shape bugs from evidence-selection bugs.
   - A dashboard can have the right envelope and still be wrong because the collected sources are unrelated to the subject.

2. Validate source relevance explicitly.
   - Check candidate URLs before fetch.
   - Check fetched documents after fetch.
   - If no subject-relevant documents remain, reject the run instead of manufacturing a dashboard.

3. Historical domain requests need focused search queries.
   - Raw user prose is often a weak search query.
   - For acronym-heavy IT topics, derive focused English domain queries, e.g.:
     - `"business intelligence" history evolution OLAP DSS data warehousing`
   - Preserve acronym expansions:
     - `BI -> business intelligence`
     - `OLAP -> online analytical processing`
     - `DSS -> decision support system`

4. Do not accept the first non-empty query result set by default.
   - Compare candidate sets across multiple queries.
   - Prefer the set with the best subject relevance, not the earliest non-empty response.

5. Honest failure is better than a false dashboard.
   - If the pipeline cannot assemble a relevant evidence set, fail with an explicit irrelevance / insufficient-evidence condition.
   - Do not replace that gap with synthetic charts or polished but irrelevant sections.

## Good verification pattern

For live incidents, inspect the full chain:
- original user request
- generated search queries
- selected candidate URLs
- fetched documents
- filtered relevant documents
- final dashboard sections

If the chain fails before the final dashboard build, fix source acquisition first. Do not spend the whole session polishing section grammar on top of bad evidence.
