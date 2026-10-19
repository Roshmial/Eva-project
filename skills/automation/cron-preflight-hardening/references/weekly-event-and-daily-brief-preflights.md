# Weekly event and daily brief preflights

Use these shapes when a recurring user-facing job mixes deterministic context gathering with judgment and writing.

## Weekly event job

The preflight script should emit:

- current local date and the target week boundaries;
- official source clusters and canonical URLs;
- titles or URLs from recent outputs for deduplication;
- explicit freshness markers for any cached helper data.

The agent prompt should require:

- official URLs first;
- direct extraction before broad search when a canonical page exists;
- at most one rescue search per source and a small total search budget;
- stopping after enough verified options exist;
- fewer verified items rather than padding with weak ones.

## Daily brief job

The preflight script should emit:

- current local time and day context;
- the latest valid helper output;
- recent final briefs and recently used links or recommendations;
- explicit missing/stale markers instead of empty values that look healthy.

The agent prompt should:

- treat preflight output as the primary context;
- reserve tools for selective live checks such as weather or a missing fact;
- forbid repeating recent recommendations when another verified option exists;
- require one direct grounded work anchor on an ordinary workday;
- suppress the job rather than invent a filler section when a required source is unavailable.

## Script attachment

Hermes cron resolves scripts relative to `~/.hermes/scripts/`.

Use:

```text
cron_weekly_events_prep.py
```

Do not pass an absolute path in the job definition. Keep the editable project implementation in its project directory if needed, but verify the cron-owned copy under `~/.hermes/scripts/`.

## Verification

For either shape:

1. Run the preflight directly and inspect its compact context.
2. Trigger the real cron job.
3. Read the durable run record and saved output artifact.
4. For user-facing jobs, confirm delivery separately.
5. Compare the result with recent outputs for repetition and style drift.
