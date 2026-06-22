# Collection request execution downstreams

Use this pattern when chat requests ask to collect or configure collection of data from explicit sources and output formats.

## Why this matters

A `collection_contract` alone is not a finished delivery. If the user asked to collect, configure collection, or set up export, the runtime must continue into an executable downstream or an explicit execution-plan artifact.

## Required split

1. Contract stage
- Extract `source_kind`, `source_items`, `subject`, `output_format`, required `fields`, and `since_date` when present.
- If critical fields are missing, return `clarification_request`.

2. Execution stage
- Do not stop at `chat:data_collection_contract` for complete requests.
- Route to a real downstream based on `source_kind`.

## Telegram pattern

For `source_kind=telegram`:
- create a task-specific channel list file instead of reusing a global list;
- keep it in the existing `TG-API` contour next to `app.py` as `channels_task_<...>.yml`;
- call the existing `TG-API /export` endpoint with `profile` + `config`;
- return execution metadata with:
  - `message_kind=collection_execution_result`
  - `downstream=chat:telegram_collection_result`
  - `task_source_list.kind=telegram_channels`
  - API result count/profile/config.

Important runtime detail:
- quote `date_from` in YAML task configs. Unquoted ISO dates may be loaded as YAML date objects and break APIs that later expect strings for `fromisoformat()`.

## Tender pattern

For `source_kind=tenders` in the current local-first contour:
- create a task-specific source-list artifact under the local tenders workspace;
- match requested domains against the existing source registry using both domain aliases and registry keys/names;
- return honest source status, separating active sources from placeholders that still need collectors.

Recommended metadata:
- `message_kind=collection_execution_plan`
- `downstream=chat:tender_collection_plan`
- `task_source_list.kind=tender_sources`
- `source_status.active_sources`
- `source_status.placeholder_sources`

## Verification

Minimum acceptance is not just parsing.

Verify all of the following:
- the request becomes a contract with no fake file export;
- a task-specific source list is physically created;
- the real downstream API or runner is invoked;
- the result exposes whether execution really happened or only a plan was possible;
- placeholder/unimplemented sources are shown explicitly instead of being silently treated as covered.

## Common pitfalls

- Treating a parsed contract as equivalent to execution.
- Reusing a global Telegram channel config instead of creating a task-specific list.
- Hiding partial source coverage in tender flows.
- Assuming a source registry file exists on prod when it was only present locally.
- Emitting fake CSV/XLSX/export replies from normal assistant text instead of producing a real artifact or an explicit execution-plan result.
