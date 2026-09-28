# Output normalizer context-savings metrics

This reference captures the follow-up after lightweight telemetry already existed.

## What was added

The in-process telemetry layer in `tools/output_normalizer.py` was extended with size-effect metrics:

- `raw_chars_total`
- `live_chars_total`
- `persisted_chars_total`
- `live_chars_saved_total`
- `persisted_chars_saved_total`

Each normalized result also returns a snapshot with:

- `current_raw_chars`
- `current_live_chars`
- `current_persisted_chars`
- `current_live_chars_saved`
- `current_persisted_chars_saved`

## Computation rule

Use direct string lengths from the same normalization pass:

- `current_raw_chars = len(raw_output)`
- `current_live_chars = len(concise_output)`
- `current_persisted_chars = len(output_persistable)`
- `current_live_chars_saved = len(raw_output) - len(concise_output)`
- `current_persisted_chars_saved = len(raw_output) - len(output_persistable)`

Clamp the saved-char totals with `max(..., 0)` inside telemetry accumulation.

## Verification pattern

Tests should cover two levels:

1. Snapshot correctness on one known-large command
- assert equality against real string lengths
- assert saved-char fields equal raw minus compacted variants

2. Aggregate telemetry correctness
- reset telemetry first
- execute at least two normalized calls
- assert totals for raw/live/persisted chars are populated and non-negative

## Live-check recipe

A useful probe is a large `git status` output with hundreds of repeated lines.

Expected behavior:
- `normalized_total` increments
- category `git` increments
- `current_raw_chars` is much larger than `current_live_chars`
- `current_raw_chars` is much larger than `current_persisted_chars`
- `live_chars_saved_total` and `persisted_chars_saved_total` show a clear positive effect

Example real outcome from the session:
- raw chars: 6104
- live chars: 169
- persisted chars: 172
- live chars saved: 5935
- persisted chars saved: 5932

## Why this matters

This gives a concrete KPI for the normalizer without adding external telemetry or schema changes. It is especially useful when deciding whether a new adapter family is actually earning its maintenance cost.
