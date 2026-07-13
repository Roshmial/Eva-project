# Hermes terminal output normalizer v1

This reference captures the first validated local-first implementation pattern for output normalization inside Hermes.

## Why this pattern was chosen

The goal was broader than token savings alone.
The runtime needed:
- smaller terminal payloads in active conversation;
- slower growth of persisted session storage;
- preservation of full raw output for later inspection;
- minimal architectural change and no new standalone service.

The chosen path was a local adapter layer in the executor, not a new daemon and not a per-tool rewrite framework.

## Confirmed insertion points

### Executor seam
Main runtime seam:
- `agent/tool_executor.py`

Integration point:
- after tool result is returned;
- before `maybe_persist_tool_result(...)`;
- before final `make_tool_result_message(...)` append.

This is the preferred place because the executor already has:
- `function_name` / `name`;
- parsed arguments including terminal command;
- tool call id;
- active environment for artifact persistence.

### Existing persistence layer reused
File:
- `tools/tool_result_storage.py`

A helper was added to support raw artifact persistence without forcing the default persisted-output wrapper shape:
- `persist_tool_artifact(content, tool_use_id, env=None)`

### Existing storage fallback kept in place
File:
- `hermes_state.py`

Existing persisted-tool truncation remains as a final safety net.
The normalizer does not replace all storage guards in v1.

## Implemented files in the validated MVP

### New module
- `tools/output_normalizer.py`

Responsibilities:
- classify terminal commands;
- normalize large or recognized terminal outputs;
- optionally persist full raw output as an artifact;
- return a JSON string preserving the terminal tool's result contract.

### Modified runtime files
- `agent/tool_executor.py`
- `tools/tool_result_storage.py`

### Tests added
- `tests/tools/test_output_normalizer.py`
- `tests/run_agent/test_terminal_output_normalization.py`

## Implemented categories in v1

- `git`
- `pytest`
- `logs`
- `filesystem`
- `generic`

In practice, the first high-value coverage came from:
- `git status`
- `git diff` families
- `pytest`
- log-like command outputs
- generic large command output fallback

## Behavioral contract used in v1

For large or recognized terminal outputs:
- `output` becomes a concise normalized summary;
- `output_normalized = true` is added;
- `output_category` is added;
- `output_summary` is added;
- `raw_output_path` is added when raw output is persisted.

The terminal result still remains JSON with the familiar fields such as:
- `output`
- `exit_code`
- `error`

That preserved compatibility with existing consumers.

## Validation signals from the session

The MVP was validated with:
- `py_compile` on modified files;
- targeted tests for the normalizer;
- integration-style test through sequential tool execution;
- related existing storage tests.

Observed green result during the session:
- `74 passed`

## Important implementation lessons

### 1. Keep normalization output contract-compatible
Do not invent a brand-new top-level terminal tool result format in v1.
Instead, enrich the existing JSON result with additional fields.
This sharply reduces blast radius.

### 2. Executor-level normalization is the best first step
Doing this in `agent/tool_executor.py` gave the best trade-off between:
- low architectural churn;
- reuse of existing persistence helpers;
- future extensibility to other tools.

### 3. Preserve raw output separately whenever normalization is substantial
Without raw artifact persistence, the system merely hides data and makes debugging worse.
The raw artifact path is part of the value proposition.

### 4. Use deterministic summaries first
For v1, rule-based summaries were sufficient and safer than adding model-dependent summarization.

## Recommended next extensions

After the validated MVP, the next useful upgrades are:
1. metadata sidecar files for raw artifacts;
2. separate `persistable_output` policy distinct from `concise_output`;
3. filesystem/json/yaml/sql-specific adapters;
4. tighter integration with long-term storage/indexing policy;
5. decision-candidate extraction only after the output layer is stable.
