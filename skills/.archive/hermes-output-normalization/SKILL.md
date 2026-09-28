---
name: hermes-output-normalization
description: Design and implement local-first output normalization for Hermes tools so large results are summarized for the model, raw payloads are preserved as artifacts, and persistence pressure on state.db is reduced without losing debuggability.
---

# When to use

Use this skill when working on any class of Hermes changes where tool outputs are too verbose, too expensive in tokens, or too large for durable storage, especially for `terminal`-heavy workflows.

Typical triggers:
- large `terminal` outputs are polluting context or inflating `state.db`
- you want concise model-facing output while preserving full raw output somewhere retrievable
- you need a safe insertion point for output shaping without rewriting the tool backend itself
- you want to add command-family-specific adapters like `git`, `pytest`, `logs`, `filesystem`, `json`, or `sql`

# Core design rule

Default to a local adapter layer between tool execution and persistence, not a separate service and not a deep rewrite of every tool.

For Hermes, the preferred insertion point is usually:
- tool executes normally
- result is normalized in `agent/tool_executor.py`
- raw output is optionally persisted as an artifact
- concise output is sent forward into model/chat/session history
- existing persistence safeguards remain as fallback protection

This keeps the architecture local-first, minimizes moving parts, and is easy to roll back.

# Recommended architecture

## 1. Put normalization after execution, not inside the terminal backend first

For `terminal`, prefer integrating in `agent/tool_executor.py` after `function_result` is returned and before `maybe_persist_tool_result()` runs.

Why:
- you already have `function_name`, `function_args`, `tool_call_id`, and active env
- you can normalize without changing backend execution semantics
- you reuse existing artifact persistence instead of inventing a parallel subsystem
- rollback is easier than patching the terminal backend directly

## 2. Keep the first version narrow

Start with `terminal` only.

Good first adapters:
- `git`
- `pytest`
- `logs`
- `filesystem`
- generic head/tail fallback

Good next adapters once the base path is stable:
- `json_yaml_data`
- `sqlite_sql`
- `system_service`
- `package_build`

Do not start with browser/file/search-wide universal coverage unless the narrow version already works.

## 3. Preserve raw output separately

When output is large or normalized aggressively:
- keep a concise, model-facing summary in the live result
- persist the raw output as an artifact
- add a metadata sidecar when possible
- keep a slightly richer persisted summary for `state.db` when the live summary would be too thin for later retrieval

Recommended shape:
- raw artifact: `<tool_use_id>.txt`
- metadata sidecar: `<tool_use_id>.txt.meta.json`

Useful metadata fields:
- `command`
- `category`
- `exit_code`
- `summary`
- `char_count`
- `line_count`
- `created_at`

## 4. Let old safety nets remain in place

Do not remove existing truncation or persistence guards in the first pass.

Keep:
- `tools/tool_result_storage.py`
- `maybe_persist_tool_result()`
- `enforce_turn_budget()`
- `hermes_state._persisted_tool_content()`

The new normalizer should improve the common path. The older guards stay as safety rails.

# Implementation sequence

## Step 1. Add a dedicated normalizer module

Create a module such as:
- `tools/output_normalizer.py`

The module should own:
- command classification
- per-category normalization
- optional artifact metadata creation
- fail-open behavior

## Step 2. Normalize only terminal JSON envelopes

For the `terminal` tool, normalize the returned JSON envelope instead of inventing a second protocol.

Pattern:
- parse the returned JSON
- read `output`, `exit_code`, and command
- produce two representations, not one:
  - `output` for live model/chat readability
  - `output_persistable` for `state.db` durability and later retrieval
- add explicit fields like:
  - `output_normalized`
  - `output_category`
  - `output_summary`
  - `output_persistable`
  - `raw_output_path`
  - `raw_output_meta_path`

Important rollout lesson:
- keep `output` concise for the active turn
- let `hermes_state._persisted_tool_content()` prefer `output_persistable` when writing to `state.db`
- drop `output_persistable` from the stored JSON after substitution so the database does not keep both variants redundantly

If parsing fails or the shape is unexpected, return the original string unchanged.

## Step 3. Persist raw artifacts through shared storage helpers

Prefer extending `tools/tool_result_storage.py` with a small reusable helper such as `persist_tool_artifact(...)` instead of creating a separate storage path.

This keeps all large-output persistence conventions in one place.

## Step 4. Add category-specific adapters gradually

### Git
Handle at least:
- `git status`
- `git diff`
- `git diff --stat`

Good concise fields:
- counts of modified/new/deleted/untracked
- touched paths
- insertions/deletions
- short excerpt for diffs

### Pytest
Extract:
- pass/fail summary line
- failing tests
- first failure or error block

### Logs
Extract:
- count of errors/warnings
- error lines or warning lines
- head/tail excerpt

### Filesystem
Handle:
- `ls`
- `tree`
- `find`
- `du`

Return compact structure instead of full listings.

### JSON / YAML
Handle at least:
- `jq`
- `yq`
- `cat *.json`
- large structured blobs printed by Python or shell tools

Preferred summaries:
- object: top-level key count + key sample
- array: item count + first-item structure
- scalar: type + preview
- non-JSON structured text fallback: compact line sample

### SQLite / SQL
Handle at least:
- `sqlite3 ...`
- `SELECT ...` style tabular output

Preferred summaries:
- row/line count
- query type when obvious
- first rows for live display
- longer row sample for persisted history

### Generic fallback
If the command family is unknown:
- summary with line/char counts
- head/tail excerpt
- preserve raw artifact when large

## Decision candidates and manual decision-log promotion

Once the normalization layer is stable, add a second semantic layer that derives compact candidates from normalized terminal results instead of scraping raw output later.

Recommended candidate kinds:
- `artifact`
- `verification`
- `issue`
- `decision`

Good first heuristics:
- `artifact`: raw output was persisted to an artifact file
- `verification`: successful `pytest`, `git status`, filesystem inspection, SQL inspection, or structured-data inspection
- `issue`: non-zero exit plus `FAILED`, `ERROR`, `Traceback`, or `FATAL`
- `decision`: `git diff` or similarly explicit change-reporting commands with concrete touched paths

Keep this layer manual-first:
- add `decision_candidates` to the normalized terminal JSON
- add `decision_log_blocks` as ready-to-promote text blocks
- do not auto-write to `decision-log` in the same rollout

This keeps the system useful for future extraction while avoiding noisy automatic promotion.

## Candidate policy / feature flags

Do not assume every environment wants the same amount of semantic extraction noise. Add a policy layer before broad rollout.

A durable rollout pattern is two-tiered:
- config is the baseline policy
- env vars are the emergency override layer

Config shape:
- `output_normalizer.decision_candidates.enabled`
- `output_normalizer.decision_candidates.kinds.artifact.enabled`
- `output_normalizer.decision_candidates.kinds.verification.enabled`
- `output_normalizer.decision_candidates.kinds.issue.enabled`
- `output_normalizer.decision_candidates.kinds.decision.enabled`

Env override layer:
- global enable flag, e.g. `HERMES_DECISION_CANDIDATES_ENABLED`
- per-kind flags, e.g.
  - `HERMES_DECISION_CANDIDATE_ARTIFACT_ENABLED`
  - `HERMES_DECISION_CANDIDATE_VERIFICATION_ENABLED`
  - `HERMES_DECISION_CANDIDATE_ISSUE_ENABLED`
  - `HERMES_DECISION_CANDIDATE_DECISION_ENABLED`

Recommended default:
- everything enabled by default
- config controls steady-state rollout
- env vars override config when you need temporary forcing during debugging or incident response
- return the effective policy in the normalized result as `decision_candidate_policy`
- return aggregated counts as `decision_candidate_counts`
- tests must prove:
  - global disable
  - per-kind disable
  - config-only disable
  - env override beating config

# Pitfalls

## Pitfall 1. Do not start by editing only `terminal_tool.py`

That is tempting because the raw output originates there, but it is usually the wrong first move for Hermes-wide output governance.

You lose the higher-level context that exists in `tool_executor`, and you risk coupling output shaping to backend execution semantics too early.

## Pitfall 2. Do not replace raw output without a retrieval path

If you summarize aggressively but do not save the full output somewhere readable, debugging quality drops immediately.

Always keep a raw artifact path for large normalized outputs.

## Pitfall 3. Do not remove existing truncation layers in the same patch

The safe rollout is additive:
- add normalization
- keep old guards
- verify behavior
- only later consider consolidation

## Pitfall 4. Do not broaden to every tool in v1

Start narrow. Get `terminal` right first. Then expand based on evidence.

## Pitfall 5. Keep fail-open behavior

Normalization must never become a new single point of failure.

If normalization crashes:
- log at debug level
- return the original tool result
- continue the normal tool pipeline

# Verification checklist

After implementation, verify all of the following:

1. syntax passes
- `python3 -m py_compile ...`

2. focused tests pass
- adapter unit tests
- tool executor integration tests
- existing storage tests
- `state.db` persistence tests that prove `output_persistable` replaces live `output` during durable write

3. old storage protections still work
- large results still persist safely
- `state.db` truncation fallback still behaves

4. the live result is materially smaller and more readable
- concise summaries appear for supported command families
- raw paths are present when expected
- `decision_candidate_policy` reflects the expected config/env outcome
- `decision_candidate_counts` matches the candidate list

5. the persisted result is richer but still bounded
- `output_persistable` is distinct where appropriate
- the stored JSON no longer carries both live and persisted variants redundantly

6. unrelated unstable patches are kept separate
- do not mix output-normalization commits with gateway lifecycle or unrelated runtime fixes

# Recommended commit hygiene

Keep these changes in their own commit series.

Good separation:
- storage/persistence fix commit
- output normalizer MVP commit
- output normalizer v1.1 commit
- gateway stability patches in a different commit

This makes rollback, review, and future rebasing much easier.

## Telemetry and observability

After the policy and adapter surface is stable, add lightweight observability before you invent a heavier metrics subsystem.

## Scope boundary: terminal-only is a first phase, not the whole token-efficiency strategy

A recurring pitfall is to mistake a successful `terminal` normalizer rollout for the complete solution to Hermes token efficiency. It is not.

Be explicit about the current scope:
- the current normalization layer is inserted on the `terminal` tool path
- it improves what the model sees on the next turn for `terminal` results
- it improves what is durably written for `terminal` results through `output_persistable`
- it does not automatically optimize every other heavy-text source in the agent

When a user’s real goal is broader token optimization, do not keep polishing terminal-only helpers indefinitely. Treat the terminal layer as phase 1 and say so clearly.

Recommended phase-2 priority order for broader token efficiency:
- `read_file`
- `search_files`
- `web_extract`
- `session_search`
- long-running `process` / log-style outputs

Design rule for that expansion:
- reuse the same mediation ideas where possible
- distinguish live model-facing output from persistence-friendly output
- avoid claiming “general token optimization is solved” while only one tool family is covered

Recommended first step:
- keep in-process counters inside `tools/output_normalizer.py`
- expose helper functions such as `get_output_normalizer_telemetry()` and `reset_output_normalizer_telemetry()`
- attach a compact per-result snapshot like `output_normalizer_telemetry`

Useful first counters:
- total normalized results
- raw artifacts written
- normalization counts by category
- emitted candidate counts by kind

Why this step is worth doing:
- it gives immediate feedback on whether the layer is helping in real usage
- it stays local-first
- it avoids schema changes and external metrics dependencies
- it gives you a clean basis for later context-savings metrics or debug/status commands

## Context-savings metrics

Once the base telemetry is in place, extend it with size-effect metrics so you can quantify whether normalization is actually buying back context and persistence budget.

Recommended aggregates:
- `raw_chars_total`
- `live_chars_total`
- `persisted_chars_total`
- `live_chars_saved_total`
- `persisted_chars_saved_total`

Recommended per-result snapshot fields:
- `current_raw_chars`
- `current_live_chars`
- `current_persisted_chars`
- `current_live_chars_saved`
- `current_persisted_chars_saved`

Computation rule:
- `live_chars_saved = max(len(raw_output) - len(concise_output), 0)`
- `persisted_chars_saved = max(len(raw_output) - len(output_persistable), 0)`

Why this layer matters:
- it turns `the normalizer feels useful` into a measurable effect
- it shows whether the live view and persisted view are shrinking as intended
- it gives a simple KPI for future rollout decisions without adding external telemetry infrastructure

Verification requirements for context-savings metrics:
- exact-count tests should reset telemetry first
- at least one test should assert exact equality between the computed saved-char fields and the real string lengths
- live checks should show a materially smaller live/persisted payload on a known-large command such as `git status`
- do not describe the numbers as global durable metrics; they are process-local snapshots unless exported deliberately

Verification requirements for telemetry:
- tests must reset counters before exact-count assertions
- tests should prove accumulation across multiple normalized calls
- live checks should confirm category and candidate-kind counts move as expected
- do not present the counters as durable global telemetry; they are process-local unless you deliberately persist/export them

# Support files

See `references/output-normalizer-v1.md` for the concrete implementation pattern, touched files, and tested rollout shape from a real Hermes session.

See `references/output-normalizer-v1-1-v1-2.md` for the follow-on rollout that added metadata sidecars, filesystem/json/sql adapters, and the split between live `output` and persisted `output_persistable`.

See `references/output-normalizer-decision-candidates.md` for the next layer that extracts `decision`, `issue`, `verification`, and `artifact` candidates from normalized terminal outputs without auto-writing to `decision-log`.

See `references/output-normalizer-policy-and-promotion.md` for the follow-up that adds per-kind feature flags and promote-ready `decision_log_blocks` while keeping decision-log writes manual.

See `references/output-normalizer-config-policy-and-live-checks.md` for the config-aware policy layer, env-over-config precedence, `decision_candidate_counts`, and compact live-check recipes.

See `references/output-normalizer-docs-and-adapter-expansion.md` for the follow-up that exposes the feature in example config/docs and extends adapters with `system_service` and `package_build`.

See `references/output-normalizer-telemetry.md` for the lightweight in-process telemetry layer, verification pattern, and guidance on keeping observability local-first before adding heavier metrics plumbing.

See `references/output-normalizer-context-savings.md` for the follow-up that turns telemetry into measurable context/persistence savings with per-result and aggregate char-count metrics.

See `references/output-normalizer-scope-boundary-and-phase-2.md` for the lesson that terminal normalization is only phase 1 of broader token-efficiency work and for the recommended next tool families to cover.
