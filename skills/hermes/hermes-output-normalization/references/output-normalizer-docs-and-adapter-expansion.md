# Output normalizer docs + adapter expansion

Use this reference when the normalization layer is already working and the next task is to make it operationally usable rather than merely code-complete.

What changed in this rollout:
- added config-facing policy example to `cli-config.yaml.example`
- documented env overrides in `website/docs/reference/environment-variables.md`
- added a focused user doc at `website/docs/user-guide/features/output-normalizer.md`
- expanded adapters with `system_service` and `package_build`

Config shape to expose in docs/examples:

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

Env overrides to document:
- `HERMES_DECISION_CANDIDATES_ENABLED`
- `HERMES_DECISION_CANDIDATE_ARTIFACT_ENABLED`
- `HERMES_DECISION_CANDIDATE_VERIFICATION_ENABLED`
- `HERMES_DECISION_CANDIDATE_ISSUE_ENABLED`
- `HERMES_DECISION_CANDIDATE_DECISION_ENABLED`

Adapter expansion pattern:

## `system_service`
Typical commands:
- `systemctl status ...`
- `service ...`
- `docker logs ...`
- `docker inspect ...`

Recommended extraction:
- state/status lines
- problem lines (`failed`, `error`, `inactive`, `not found`)
- concise + persisted head/tail excerpt
- `verification` candidate on successful inspections

## `package_build`
Typical commands:
- `pip install ...`
- `pip3 install ...`
- `uv install ...`
- `npm install`, `pnpm install`, `yarn add`
- `cargo build`, `cargo check`, `cargo install`
- `go build`
- `make build`, `make install`, `make check`

Recommended extraction:
- success lines (`installed`, `added`, `built`, `audited`)
- warnings / deprecated notices
- error lines
- concise + persisted excerpts
- `verification` candidate on successful runs

Verification used in this rollout:
- `py_compile` on changed Python files
- focused pytest suite for normalizer + persistence
- live checks proving `system_service` and `package_build` classify correctly and emit `verification` candidates

Practical lesson:
When the user asks for "finish the improvements", do not stop at code. Add config surface, docs, tests, live verification, and clean commits so the feature is actually operable.
