# Web collection fallback: source shortlist + weak-content previews

Use when open-web collection succeeds at source discovery but fails to extract usable document text for all candidates.

## Goal

Do not return a hard error or a thin technical fallback. Return a user-usable research package that preserves discovery work.

## Baseline fallback shape

Prefer a structured `source_shortlist` artifact with at least:
- `title`
- `domain`
- `source_url`
- `query`
- `source_rank`
- `availability_level`
- `error_reason`

This is the minimum package that lets the user continue manual review without repeating source discovery.

## Second-layer enrichment

Before adding new infrastructure, reuse weak-content already available inside the current contour:

1. Search-stage previews
   - Parse HTML search results and keep:
     - `title`
     - `snippet`
     - `domain`
     - normalized `url`
   - Mark entries with `availability_level=snippet_only` when a snippet exists.

2. Partial page metadata
   - If a page fetch succeeds only partially, extract:
     - `meta description`
     - `og:description`
   - Use this as weak preview content even when full-text extraction is not good enough.

## Product contract

User-facing reply should explicitly say that:
- full document extraction failed;
- the attached file still contains a useful shortlist;
- short descriptions are included where available.

Do not describe the result as just a "list of links" once snippets/metadata are present.

## Mixed-result upgrade

If at least one source produced usable document content but some sources still failed fetch/extraction, do not drop the failed half on the floor.

Prefer a single hybrid artifact that contains both layers:
- `document_row` entries for successfully extracted/structured content;
- `source_shortlist` entries for failed/unavailable sources with preview metadata.

Recommended extra columns for structured formats (`csv/xlsx/json`):
- `record_type` (`document_row` vs `source_shortlist`)
- `source_status` (`available` vs `unavailable`)
- `title`
- `domain`
- `query`
- `source_rank`
- `availability_level`
- `snippet`
- `error_reason`

Recommended metadata contract for mixed-mode:
- `partial_result=true`
- `status_note=sources_partially_unavailable`
- `fallback_result_kind=hybrid_content_plus_shortlist`
- separate `web_source_shortlist` payload in message metadata

User-facing reply in mixed-mode should explicitly say that:
- the main file contains real extracted rows;
- skipped/unavailable sources were preserved in the same file as shortlist rows;
- the user does not need to redo source discovery to continue review.

## Verification pattern

Minimum regression coverage:
1. manifest/source helper stores `snippet`, `query`, `domain`, `source_rank`, `availability_level`;
2. search-result preview parser extracts `title + snippet + normalized URL` from HTML results;
3. fallback execution path returns `collection_execution_result` with `partial_result=true`, `fallback_result_kind=source_shortlist`, and enriched shortlist rows.

## Scope boundary

This is still weak-content fallback, not confirmed full-document extraction. Preserve that distinction in code, metadata, and user-facing text.
