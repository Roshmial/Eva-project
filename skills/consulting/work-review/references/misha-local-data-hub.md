# Local data hub for Misha: practical default

Use this reference when Misha asks for a concrete storage recommendation for accumulated agent/analytics data on the same server.

## Recommended default
Choose DuckDB as the first option when the need is:
- one local analytical store;
- no extra DB service to operate;
- unify Hermes interaction history with parsing outputs;
- ingest Telegram and tender CSV/JSON artifacts;
- run lightweight reporting and derived views.

## Why this default fits Misha
- local-first architecture;
- avoids unnecessary external dependencies;
- avoids introducing Postgres just to store analytical snapshots and feeds;
- good fit for append/import/query workloads from Hermes, Telegram parsing, and tender pipelines.

## Delivery rule for this class of question
If constraints are already clear, do not stay in exploratory mode. Answer in this order:
1. one recommended option;
2. one-sentence reason tied to the current stack;
3. immediate deployment/implementation.

## Implementation pattern used successfully
- keep Hermes core state as-is;
- create a separate derived analytics DB beside Hermes, not inside its core state;
- load Hermes sessions/messages plus Telegram and tender artifacts into the derived DB;
- add refresh script, query script, backup script, restore script;
- wire existing Telegram and tender scripts to trigger a refresh;
- add scheduled backups with retention and checksum manifest.

## Scope that proved useful to ingest
- Hermes sessions and messages;
- Telegram raw archive;
- Telegram summary-input payloads;
- Telegram classified digest rows including post type, score, confidence, reasons;
- Telegram collection reports;
- tender items;
- tender source statuses;
- tender run summary;
- tender source config.

## User-style pitfall
The phrase 'не занудствуй' means the answer was too exploratory or over-explained. Compress immediately to a concrete recommendation and action.