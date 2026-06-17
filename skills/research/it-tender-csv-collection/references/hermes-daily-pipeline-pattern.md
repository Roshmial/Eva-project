# Hermes Daily IT Tender Pipeline Pattern

Session-derived production pattern for turning the tender collection workflow into a recurring Hermes-managed pipeline.

## Goal

Build a fully local recurring pipeline that:
- collects IT tenders from `zakupki.gov.ru` and `B2B-Center`;
- writes a flat business CSV;
- writes a separate per-source status CSV;
- runs on Hermes cron without external SaaS.

## Recommended execution shape

- Use a local Python script under `~/.hermes/scripts/`.
- Use a Hermes `cronjob` with `no_agent=true` when the script itself can produce the final user-facing message.
- Keep the working directory on a stable writable workspace, e.g. `/home/hermes/workspace`.
- Keep output files in a dedicated subdirectory such as `/home/hermes/workspace/tenders/`.

## Proven file set

Recommended outputs per run:
- `it_tenders_<YYYY-MM-DD>.csv` — dated business CSV
- `it_tenders_latest.csv` — stable latest pointer
- `tender_sources_status_<YYYY-MM-DD>.csv` — dated diagnostics by source
- `tender_sources_status_latest.csv` — stable latest diagnostics pointer
- `last_run_summary.json` — machine-readable run summary

## Delivery pattern

For a script-only cron job, print a short final message plus `MEDIA:<absolute_path_to_csv>`.
This makes Hermes deliver the CSV directly to Telegram without an extra agent summarization layer.

## Source handling rule

Do not fabricate rows for a source just because it is part of the configured source set.

Correct behavior:
- include real rows only when a source produced verified public tenders;
- if a source produced zero qualifying rows for the target date, keep the business CSV clean;
- record the zero-row outcome in the status CSV instead.

This is especially important for `B2B-Center`, where the source may be publicly reachable but still yield zero relevant rows for the date/query pack.

## Scheduling note

If the user wants 10:00 Moscow time and the server runs in UTC, the cron expression is `0 7 * * *`.
Always record both the business-facing time and the server cron expression when handing over the pipeline.

## Practical limitation notes

- `zakupki.gov.ru` may return imperfect buyer fields; if buyer extraction is unreliable, keep `не указано`.
- `B2B-Center` often exposes public tenders but does not show public price; keep an explicit missing-price marker instead of inventing a value.
- A clean diagnostics CSV is more useful than polluting the main CSV with blocker rows.
