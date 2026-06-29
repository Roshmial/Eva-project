# Useful web fallback: source shortlist instead of technical partial result

## When this pattern applies

Use when the web collection route selected correctly and source discovery produced plausible candidate URLs, but document extraction failed for all candidates because of timeout, blocking, 403, parser failure, or empty content.

This is not a routing failure. It is a source-stage / extraction-stage failure after successful discovery.

## Anti-pattern

Do not return a fallback file that contains only:
- `url`
- `title`
- `status`

That is a technical artifact, not a user-usable result.

## Required fallback contract

Return a `source_shortlist` artifact that lets the user continue manual review without redoing discovery.

Minimum per-row fields:
- `title`
- `domain`
- `source_url`
- `query`
- `source_rank`
- `availability_level`
- `error_reason`

Recommended metadata:
- `fallback_result_kind=source_shortlist`
- `partial_result=true`
- `status_note=sources_found_but_documents_unavailable`

## User-facing reply shape

Say explicitly that:
- full document extraction failed;
- a useful shortlist of sources was still assembled;
- the file contains URLs, domains, query context, selection order, and unavailability reason.

Avoid vague wording like "here is a file" or purely technical wording like "partial result" without explaining why the file is still useful.

## Implementation notes

- Save the winning search query in the web-source manifest.
- Normalize each discovered URL into a structured manifest item before persistence.
- If requested format is `xlsx` but xlsx runtime is unavailable, degrade to `csv` instead of failing the fallback path.

## Verification

At minimum add tests for:
1. manifest-item enrichment from raw URLs (`domain`, `query`, `source_rank`, `availability_level`);
2. partial fallback producing enriched rows and `fallback_result_kind=source_shortlist`.
