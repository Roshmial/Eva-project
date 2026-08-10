# Weekly event + daily brief cron redesign

Date: 2026-08-04

## Why this pattern mattered

Two user-facing cron jobs were running but were not stable enough:

- `eva-weekly-moscow-events-pick` mixed broad search, ranking, and writing in one agent pass and had already hit `loop_web_search_cap`.
- `eva-daily-self-development-brief` spent too much effort re-raising deterministic context and still drifted into soft-control and generic coaching language.

The fix was not "rewrite the whole thing". The fix was to separate deterministic preflight from the agent layer.

## Concrete redesign

### Weekly event job
Job id: `3c26e0954d43`

Preflight script:
- `~/.hermes/scripts/cron_weekly_events_prep.py`

What the script emits:
- Moscow current time
- week start and week end
- allowed source clusters
- titles from recent weekly outputs for dedup awareness

Prompt changes that mattered:
- official source URLs first
- `web_search` only as rescue path
- max 1 rescue search per source
- max 4 `web_search` calls total
- stop once 8–10 verified items exist

Verified output after redesign:
- `/home/hermes/.hermes/cron/output/3c26e0954d43/2026-08-04_05-38-42.md`

### Daily brief job
Job id: `329913efa98a`

Preflight script:
- `~/.hermes/scripts/cron_daily_brief_prep.py`

What the script emits:
- Moscow current time
- today's context from `eva-digest-context.yaml`
- latest helper output
- recent final dailies
- recent linked anchors/opory

Prompt changes that mattered:
- script output is the primary day context
- tools are reserved for selective verification only
- for an ordinary workday with no helper event, require one direct work anchor
- explicitly ban soft-control and generic coaching phrasing

Verified output after redesign:
- `/home/hermes/.hermes/cron/output/329913efa98a/2026-08-04_05-41-14.md`

## Important pitfall

When attaching a cron script through `cronjob update`, Hermes expects a script path relative to `~/.hermes/scripts/`.

Wrong:
- `/home/hermes/.hermes/scripts/cron_weekly_events_prep.py`

Right:
- `cron_weekly_events_prep.py`

## Reusable lesson

For recurring user-facing cron jobs:
- deterministic inputs belong in script output;
- synthesis belongs in the agent prompt;
- verification belongs in a live run plus output-file inspection.
