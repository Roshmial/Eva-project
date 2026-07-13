# Config-aware policy and live checks for Hermes output normalization

## What this rollout added

A later rollout extended the decision-candidate layer in two practical ways:

1. Policy is no longer env-only.
   - Config is the steady-state source of truth.
   - Env vars override config for debugging, rollout control, or incident response.

2. The normalized terminal JSON now exposes lightweight observability fields.
   - `decision_candidate_policy`
   - `decision_candidate_counts`

This makes live inspection much easier because you can see both the effective policy and the actual extracted candidate mix in one place.

## Expected config shape

```yaml
output_normalizer:
  decision_candidates:
    enabled: true
    kinds:
      artifact:
        enabled: true
      verification:
        enabled: true
      issue:
        enabled: true
      decision:
        enabled: true
```

## Env override layer

Global:
- `HERMES_DECISION_CANDIDATES_ENABLED`

Per-kind:
- `HERMES_DECISION_CANDIDATE_ARTIFACT_ENABLED`
- `HERMES_DECISION_CANDIDATE_VERIFICATION_ENABLED`
- `HERMES_DECISION_CANDIDATE_ISSUE_ENABLED`
- `HERMES_DECISION_CANDIDATE_DECISION_ENABLED`

Precedence rule:
- config sets the baseline
- env overrides config when present

## Live-check recipe

Use a short Python probe that exercises three things:
- large `git status` output to confirm artifact + verification candidates and `output_persistable`
- failing `pytest` output to confirm `issue` extraction
- `git diff` output to confirm `decision` extraction and `decision_log_blocks`

Useful assertions during a live check:
- `raw_output_path` exists when output is large enough
- `raw_output_meta_path` exists and contains summary metadata
- `_persisted_tool_content()` replaces live `output` with `output_persistable`
- `decision_candidate_policy` matches expected config/env state
- `decision_candidate_counts` matches the actual candidate list
- disabling a kind in config suppresses it when env is unset
- enabling the same kind via env restores it over config

## Regression tests worth keeping

At minimum keep tests for:
- global disable of all candidates
- per-kind disable via env
- per-kind disable via config only
- env override beating config
- counts reflecting extracted candidate kinds
- decision-log blocks remaining empty when all candidates are disabled

## Practical rollout lesson

This layer is most useful when kept manual-first:
- do not auto-write to `decision-log`
- do return `decision_log_blocks` ready for manual promotion
- do expose policy and counts in the tool result so future automation has stable hooks
