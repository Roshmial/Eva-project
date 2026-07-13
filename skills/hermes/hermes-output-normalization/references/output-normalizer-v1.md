# Output normalizer implementation reference

This reference captures a concrete Hermes implementation pattern that worked in practice for terminal output normalization.

## Chosen insertion point

Primary runtime hook:
- `agent/tool_executor.py`

Reason:
- sits after tool execution
- has access to `function_name`, `function_args`, `tool_call_id`, and active env
- can normalize before `maybe_persist_tool_result()`
- avoids coupling output shaping to terminal backend execution semantics

## Concrete files touched

### New module
- `tools/output_normalizer.py`

Responsibilities:
- classify terminal commands
- normalize by command family
- preserve JSON envelope shape returned by `terminal`
- persist raw output artifact when large
- attach metadata sidecar path fields to the result

### Storage helper extension
- `tools/tool_result_storage.py`

Added helper concept:
- `persist_tool_artifact(content, tool_use_id, env=None, metadata=None)`

Purpose:
- reuse the existing temp-backed artifact path
- support sibling `.meta.json` write next to raw artifact

### Executor integration
- `agent/tool_executor.py`

Pattern:
- if tool name is `terminal` and result is a string
- call `normalize_terminal_result(...)`
- then continue through existing persistence path

## Implemented v1 adapters

### MVP
- generic
- git
- pytest
- logs

### v1.1
- filesystem
  - `ls`
  - `tree`
  - `find`
  - `du`

## Output fields added to normalized terminal results

- `output_normalized`
- `output_category`
- `output_summary`
- `raw_output_path`
- `raw_output_meta_path`

## Metadata sidecar fields used

- `command`
- `category`
- `exit_code`
- `summary`
- `char_count`
- `line_count`
- `created_at`

## Verification pattern that passed

Syntax:
- `python3 -m py_compile tools/output_normalizer.py tools/tool_result_storage.py agent/tool_executor.py ...`

Focused tests that passed in-session:
- output normalizer unit tests
- terminal output normalization integration test in run_agent path
- tool result storage tests
- existing storage-optimization and state-db regression tests

Observed successful regression run:
- `76 passed`

## Commit hygiene lesson

Keep output-normalization commits separate from unrelated gateway/runtime patches.

A clean sequence that worked well:
1. storage and doctor fixes
2. output normalizer MVP
3. output normalizer v1.1
4. gateway stability patch left separate

## Practical next steps after this reference

Good v1.2 candidates:
- JSON/YAML adapter
- SQL or sqlite adapter
- explicit divergence between `concise_output` and `persistable_output`
- later, decision-candidate extraction based on normalized summaries
