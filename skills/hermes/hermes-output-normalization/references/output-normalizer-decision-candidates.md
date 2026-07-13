# Output normalizer: decision candidate extraction layer

Use this reference when the core output-normalization pipeline already exists and the next step is to extract structured semantic candidates from normalized terminal results without auto-writing to `decision-log`.

## Goal

Add a soft semantic layer on top of normalized terminal outputs so later workflows can promote useful events into decision logs, issue trackers, or verification summaries without parsing raw tool blobs again.

The first safe shape is a `decision_candidates` array inside the normalized terminal JSON envelope.

## Recommended candidate kinds

Start with four kinds only:
- `artifact`
- `issue`
- `verification`
- `decision`

Keep the taxonomy small. If it already feels ambiguous, it is too early to add more kinds.

## Extraction rule

Do not try to infer rich business meaning in v1. Prefer deterministic heuristics tied to command family, exit code, and obvious output markers.

### `artifact`
Create when:
- a raw artifact path was created for the tool output

Suggested fields:
- `kind`
- `title`
- `summary`
- `command`
- `artifact_path`

### `issue`
Create when:
- exit code is non-zero and output contains strong failure markers such as `FAILED`, `ERROR`, `Traceback`, `FATAL`
- or the command family is inherently failure-oriented and the output clearly shows failure

Suggested fields:
- `kind`
- `title`
- `summary`
- `command`
- `exit_code`

The summary should prefer the first strong error line over a generic category label.

### `verification`
Create when:
- a check/inspection command completed successfully and the result is naturally interpreted as confirmation rather than change
- examples: successful `pytest`, successful `git status`, successful filesystem/sql/json inspection commands

Suggested fields:
- `kind`
- `title`
- `summary`
- `command`

### `decision`
Create when:
- a change-oriented command exposes an actual chosen or changed state
- the first practical case is `git diff` with touched files

Suggested fields:
- `kind`
- `title`
- `summary`
- `command`

## Non-goals

Do not in this layer:
- auto-write to `decision-log.md`
- infer product strategy from arbitrary shell output
- use an LLM by default
- treat every successful command as a decision

This is a candidate layer, not a final truth layer.

## Integration point

Add `decision_candidates` inside the same normalized terminal result that already carries:
- `output`
- `output_persistable`
- `output_summary`
- `output_category`
- optional raw artifact paths

This keeps later consumers from having to re-open the raw blob.

## Good implementation pattern

1. Normalize terminal output first.
2. Persist raw artifact if needed.
3. Extract candidates from the original raw output plus the normalization summary.
4. Store candidates back into the normalized JSON envelope.
5. Let durable persistence keep the candidate array with the persisted version.

## Good tests

At minimum, add tests that prove:
- large normalized outputs with raw artifact paths yield an `artifact` candidate
- failing `pytest` yields an `issue` candidate
- successful inspection commands yield a `verification` candidate
- `git diff` with touched files yields a `decision` candidate

## Pitfalls

- Pitfall: writing directly to `decision-log` from the extractor.
  Fix: stop at `decision_candidates`; promotion belongs to a later workflow.

- Pitfall: using vague titles like `Something happened`.
  Fix: make the title specific to the class of event, for example `Test run completed successfully` or `Terminal command surfaced an issue`.

- Pitfall: overfitting to one exact error string.
  Fix: use a small family of deterministic markers and keep summaries short.

- Pitfall: extracting candidates only from concise output.
  Fix: use the raw output and summary, because concise output may intentionally omit evidence.

## Rollout note

When adding this layer in an active implementation stream, keep it as its own commit after the normalization/persistence split is already green. It is a semantic layer and should be easy to revert independently of artifact storage or `state.db` shaping.
