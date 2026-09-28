# Hermes output normalizer rollout notes: v1.1 + v1.2

This reference captures the concrete rollout pattern that proved useful in a real Hermes session after the initial MVP already existed.

## What changed after MVP

### v1.1
- Added raw artifact metadata sidecars: `<tool_use_id>.txt.meta.json`
- Added filesystem adapter coverage for:
  - `ls`
  - `tree`
  - `find`
  - `du`
- Kept the same insertion point in `agent/tool_executor.py`
- Reused `tools/tool_result_storage.py` rather than creating a parallel artifact store

### v1.2
- Added `json_yaml_data` adapter
- Added `sqlite_sql` adapter
- Introduced a true split between:
  - live `output`
  - persisted `output_persistable`
- Updated `hermes_state._persisted_tool_content()` so durable writes prefer `output_persistable`, then drop that field from the stored JSON to avoid duplication

## Concrete file pattern

Primary files touched:
- `tools/output_normalizer.py`
- `tools/tool_result_storage.py`
- `agent/tool_executor.py`
- `hermes_state.py`
- `tests/tools/test_output_normalizer.py`
- `tests/tools/test_tool_result_storage.py`
- `tests/test_state_db_output_persistable.py`

## Durable design lessons

1. The first good insertion point stayed the same: `agent/tool_executor.py` before `maybe_persist_tool_result()`.
2. Metadata sidecars are worth adding early because they create a clean bridge toward future indexing, retrieval, and decision extraction.
3. `cat *.json` must classify as structured data before broad `cat`/log heuristics, otherwise JSON gets mislabeled as logs.
4. A single normalized `output` is not enough once the system cares about both readability and durable retrieval. Use two views:
   - concise live view
   - richer persisted view
5. The durable layer should not keep both versions redundantly. Replace `output` with `output_persistable` during persistence and remove the extra field before writing to `state.db`.

## Verification pattern that worked

Run all of these together:
- `python3 -m py_compile ...`
- focused normalizer unit tests
- storage helper tests
- tool executor integration tests
- persistence tests for `hermes_state._persisted_tool_content()`

Useful regression assertions:
- filesystem outputs become compact summaries instead of raw listings
- JSON outputs expose key/item structure
- SQL outputs expose row samples
- `output_persistable` differs from live `output` for at least one realistic category such as `git status`
- persisted JSON no longer contains `output_persistable` after transformation for DB write

## Commit hygiene that worked well

Keep separate commits for:
- MVP normalizer
- metadata/filesystem extension
- json/sql extension
- concise vs persisted split
- unrelated gateway/runtime fixes in a different commit line
