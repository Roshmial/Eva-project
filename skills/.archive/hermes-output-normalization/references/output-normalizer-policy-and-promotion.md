# Output normalizer policy and decision-log promotion follow-up

## What was added in the follow-up

A later rollout on top of the Hermes terminal output normalizer added two practical layers:

1. candidate policy flags
2. manual decision-log promotion blocks

This came after the stack already had:
- terminal normalization in `agent/tool_executor.py`
- raw artifact persistence via `tools/tool_result_storage.py`
- metadata sidecars
- distinct live `output` vs durable `output_persistable`
- candidate extraction for `artifact`, `verification`, `issue`, and `decision`

## Policy pattern

Use env-driven flags first because they are low-risk and easy to roll back:

- `HERMES_DECISION_CANDIDATES_ENABLED`
- `HERMES_DECISION_CANDIDATE_ARTIFACT_ENABLED`
- `HERMES_DECISION_CANDIDATE_VERIFICATION_ENABLED`
- `HERMES_DECISION_CANDIDATE_ISSUE_ENABLED`
- `HERMES_DECISION_CANDIDATE_DECISION_ENABLED`

Recommended semantics:
- unset means enabled
- global flag gates all per-kind flags
- per-kind flags allow selective rollout without touching normalization itself

## Manual promotion pattern

Do not auto-write into `decision-log` in the same patch where candidates are first introduced.

Instead:
- keep `decision_candidates` as structured JSON attached to the normalized terminal result
- add `decision_log_blocks` as simple promote-ready text blocks
- let higher layers decide whether to surface or persist them

Useful fields inside each block:
- type
- title
- summary
- command
- artifact_path when present
- exit_code when relevant

This preserves human review and keeps false positives from leaking into durable decision history.

## Candidate heuristics that proved useful

- `artifact`: raw output persisted to artifact storage
- `verification`: successful `pytest`, `git status`, filesystem inspection, SQL inspection, JSON/YAML inspection
- `issue`: non-zero exit with `FAILED`, `ERROR`, `Traceback`, or `FATAL`
- `decision`: `git diff` with concrete touched paths

## Commit hygiene lesson

Keep the following as separate commits when possible:
- semantic extraction of decision candidates
- policy flags and manual promotion blocks
- unrelated gateway/runtime hardening

In the source session, the gateway watcher decode-hardening patch was committed separately from normalizer evolution. That separation made the repository end in a clean state and preserved rollback clarity.

## Minimum verification

After adding policy and promotion layers, verify:
- `py_compile` for the touched files
- existing normalizer/storage/integration tests still pass
- tests proving per-kind candidate disable
- tests proving global candidate disable
- tests proving `decision_log_blocks` are present when expected
