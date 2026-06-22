# Universal collection and composition contour

## When this reference matters

Use for local-first backend/chat delivery where the user asks for:
- source -> processing -> resulting file
- collection from one file / many files / API / web / Telegram / tenders
- proposal-like outputs such as commercial proposal drafts, cost estimates, or resource estimates
- stricter routing so the agent does not choose several top-level paths at once

## Core contour

1. Intake / contract
- Build one `collection_contract` with:
  - `source_kind`
  - `source_items`
  - `subject`
  - `task_goal`
  - `output_format`
  - `fields`
  - `since_date`
  - constraints such as `must_use_analogs`

2. Selected route
- Data-driven requests must stay on one top-level route.
- Preferred priority:
  - `collection_execution`
  - `collection_contract`
  - `message_export`
  - `dashboard`
  - `recurring_job`
  - `generic_chat`

3. Task-specific source manifest
- Do not let collection requests live only in chat text.
- Materialize a per-task source artifact:
  - URL/source manifest for generic web search
  - channel list for Telegram
  - source-list JSON for tenders
  - attachment bundle manifest for one/many files
  - API config manifest for API tasks

4. Raw ingest
- Fetch or load raw source data.
- Keep enough provenance to trace each normalized row/entity back to its source.

5. Normalize
- Convert sources into shared structures such as:
  - rows
  - requirements
  - roles
  - cost_items
  - evidence
  - analogs

6. Analog stage
- For proposal/cost/resource tasks, analogs are not optional.
- If direct matches do not exist, use partial/component analogs and mark them honestly.
- Separate:
  - confirmed fact
  - analog-based estimate
  - hypothesis

7. Composition layer
- Dataset outputs: csv/json/xlsx
- Human outputs: md/docx/pdf proposal draft or estimate summary
- For proposal work, prefer dual outputs:
  - machine-readable table/model
  - human-readable narrative / project-of-proposal

## Important parsing lessons

### Generic web collection
If the user says things like:
- `собери информацию из источников в интернете`
- `собери с открытых источников`
- `собери с сайтов`

then do not force `missing_fields = список URL / сайтов` at contract stage.
Treat this as generic `web` collection and continue through:
- query/search manifest
- top results
- fetch
- normalize
- artifact

### Subject extraction
Natural phrasing often looks like:
- `в csv по теме LegalAI с полями ...`
- `собери по теме X с полями ...`

So subject parsers must not only look for a format marker immediately after `по теме`. They should also stop correctly before `с полями`, `колонки`, `и поставь`, similar continuations.

## Regression targets worth keeping

Minimum regression coverage for this contour:
1. Explicit web URLs -> real artifact file
2. Generic web request without explicit URLs -> valid `web` contract, no fake URL blocker
3. Collection route preempts dashboard/recurring job/generic path
4. Telegram request -> task-specific channel list + API call
5. Tender request -> task-specific source list + honest active/placeholder status

## Still-open implementation gaps

These are design-complete but not necessarily fully delivered in every runtime:
- first-class execution path for `attachment/attachments` collection
- arbitrary API collection executor with task-specific config manifest
- analog corpus + end-to-end cost/resource estimation layer for proposal drafting
