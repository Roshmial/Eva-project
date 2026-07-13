# Output normalizer telemetry follow-up

## What was added

A lightweight in-process telemetry layer was added to `tools/output_normalizer.py` to give immediate operational visibility without introducing a database, external metrics backend, or a separate service.

## Telemetry shape

Current counters:
- `normalized_total` — number of terminal results that passed through normalization
- `artifacts_total` — number of times a raw artifact file was written
- `categories` — per-category normalization counts
- `candidate_kinds` — aggregate counts for emitted candidate kinds such as `artifact`, `verification`, `issue`, and `decision`

Runtime helpers:
- `get_output_normalizer_telemetry()`
- `reset_output_normalizer_telemetry()`

Per-result field:
- `output_normalizer_telemetry`

Useful snapshot fields in that per-result payload:
- `normalized_total`
- `artifacts_total`
- `categories`
- `candidate_kinds`
- `current_category`
- `artifact_written`

## Why this shape works

This is deliberately lightweight:
- no schema migration
- no new persistence layer
- no cross-process coordination requirement
- enough visibility for live debugging, smoke checks, and future rollout decisions

It is a good intermediate step before adding any formal metrics export or telemetry persistence.

## Verification pattern

Recommended checks:
1. reset counters
2. run two different normalized command families
3. assert `normalized_total` increments
4. assert category buckets increment independently
5. assert candidate-kind counters reflect the emitted candidates
6. if a large output path is used, assert `artifacts_total` increments

Example live expectation:
- one failing `pytest` call
- one successful `systemctl status ...` call
- telemetry should show:
  - `normalized_total = 2`
  - categories containing `pytest` and `system_service`
  - candidate kinds containing at least `issue` and `verification`

## Pitfalls

- Do not present this as durable fleet-wide telemetry. It is process-local.
- Do not wire this into a heavy metrics system before the data shape proves useful.
- Do not skip `reset_output_normalizer_telemetry()` in tests that assert exact counts.
- Do not store both detailed telemetry history and raw output history in `state.db` unless there is a clear retrieval need; that would reintroduce storage pressure the normalizer is trying to reduce.

## Good next step

If you need richer observability later, add one of these before anything more complex:
- context-savings counters for live vs persisted output lengths
- a debug/status command that prints current normalizer telemetry
- optional periodic export of aggregated counters to a compact local artifact
