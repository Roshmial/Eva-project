# Token optimization quick-win patterns

Condensed patterns from a successful implementation-first optimization pass.

## Proven rollout order

1. Exact reuse for identical large outputs inside one task.
2. Extend the same reuse path into aggregate turn-budget enforcement.
3. Compact persisted/reference blocks again before prompt inclusion.
4. Add append-only log delta for repeated log inspection loops.
5. Add top-level JSON delta for slightly changing structured payloads.
6. Add a minimal policy selector over the existing surfaces: full / compact / reference / delta.

## Measurement pattern

For each optimization, try to collect:
- raw chars
- live chars after transformation
- chars saved
- activation counts by policy or mechanism

Useful counters:
- persisted_total
- reused_total
- artifact_writes_total
- prompt_compacted_total
- prompt_chars_saved_total
- delta_reused_total
- delta_chars_saved_total
- policy_counts or prompt_policy_counts

## Safe-first heuristics

- Prefer exact identity/hash matching before similarity-based reuse.
- Scope caches to one task unless a broader scope is clearly safe.
- For delta behavior, require obvious continuity: append-only logs or small top-level JSON changes.
- If a delta/reference form already exists, shorten it again before it re-enters the prompt.

## Recommended validation set

- one targeted test proving the new behavior
- one broader regression slice for the touched subsystem
- one tiny synthetic benchmark or probe showing the actual size reduction

## User workflow lesson

When the user asks for quick wins, treat architecture/framework writing as deferred work. Ship the smallest measurable optimization first, then extract a common selector only after several concrete wins are live.
