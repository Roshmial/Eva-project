---
name: agent-output-normalization-and-storage
description: Design and implement a local-first output normalization layer for agent tools so large results become compact, searchable, and persistence-safe without losing raw artifacts.
---

# Agent Output Normalization and Storage

Use when an agent runtime is suffering from one or more of these patterns:
- large terminal or tool outputs inflate chat context and persistence;
- `state.db` or equivalent transcript storage grows mostly because raw tool payloads are stored verbatim;
- decision logs or summaries duplicate operational logs because there is no clean separation between raw output, concise output, and stored output;
- the system needs better output shaping without introducing a separate external service.

This skill is especially useful in local-first Hermes-style runtimes where the best solution is to add a thin normalization layer inside the existing tool pipeline rather than bolt on a new daemon or SaaS product.

## Core idea

Treat tool output as a multi-surface artifact, not as one blob reused everywhere.

At minimum distinguish:
1. raw output — exact full payload for later inspection;
2. concise output — what the model and user should usually see;
3. persisted output — what should land in session storage or searchable history;
4. metadata — category, command, exit code, artifact path, summary, and size facts.

Do not start by redesigning the whole storage system. First insert a normalization seam into the existing execution path.

## Preferred implementation path

### 1. Reuse the current runtime before adding infrastructure

Default to the existing stack.
For Hermes-like runtimes this usually means:
- keep the current tool execution flow;
- keep the current persistence layer;
- keep the current artifact/temp storage mechanism;
- add a normalizer in the tool execution pipeline.

Avoid creating a standalone service unless the in-process seam is clearly insufficient.

### 2. Insert the normalizer at the executor seam, not inside every tool

Preferred place:
- after the tool has already returned a result;
- before large-result persistence and before the final tool-result message is appended to history.

Why:
- the executor already knows tool name, arguments, tool call id, and active environment;
- one seam can cover multiple command families;
- fallback behavior stays centralized;
- the underlying tool contract changes less.

For Hermes terminal flows, the first seam to inspect is the tool executor path around:
- tool result post-processing;
- `maybe_persist_tool_result(...)`;
- final `make_tool_result_message(...)`.

### 3. Start with deterministic classification

For MVP, do not rely on LLM summarization.
Classify outputs by command family using deterministic rules.
Useful starting categories:
- git;
- tests;
- logs;
- filesystem;
- generic fallback.

Only normalize when one of these is true:
- output is above a threshold;
- command family is known and benefits from structured summary.

### 4. Preserve raw output explicitly

If output is normalized, preserve the full raw output separately.
Best pattern:
- save raw output as an artifact file in the existing temp/artifact storage path;
- return the artifact path inside the normalized result.

This prevents the false trade-off between compact context and recoverability.

### 5. Use the existing persistence limiter as a safety net, not the main design

If the runtime already has a truncation or persisted-output mechanism, keep it.
But move the primary design toward structured normalization first, then let generic truncation remain the last-resort guard.

## MVP scope

Implement only a narrow first version.

### Recommended v1
- a new output normalizer module;
- classifier for `git`, `pytest`/test runs, `logs`, `filesystem`, `generic`;
- raw artifact persistence helper;
- executor integration for terminal results only;
- tests for classification, normalization, and executor integration.

### Explicitly defer in v1
- browser/file/search-wide normalization;
- automatic decision-log writes;
- schema migrations for metadata tables;
- LLM-based summarization by default;
- a separate microservice.

## Output shape guidelines

Good normalized output should:
- keep the most decision-relevant facts first;
- preserve error excerpts when failures happened;
- list notable paths or failing tests where relevant;
- include raw artifact location when full output was externalized.

Examples:

### Git status
Show:
- branch;
- counts of modified/new/deleted/untracked;
- a short notable-path list.

### Git diff
Show:
- file count;
- insertion/deletion counts if derivable;
- touched paths;
- optional short excerpt.

### Test runs
Show:
- summary line;
- failing tests;
- first useful failure excerpt.

### Logs
Show:
- error and warning counts;
- important lines;
- head/tail excerpt.

### Generic fallback
Use:
- short summary with line and char counts;
- head/tail excerpt;
- artifact path if raw output was saved.

## Verification checklist

After implementation, verify all of the following:
1. syntax/compile checks pass;
2. targeted tests pass;
3. a terminal result still remains valid JSON or valid tool-result content for the runtime;
4. normalized outputs are smaller and more readable than the raw versions;
5. raw outputs remain recoverable when normalized;
6. existing fallback persistence still works for oversize results.

## Pitfalls

### Pitfall 1: normalizing inside the terminal tool too early
That couples normalization to one backend implementation and makes later generalization harder.
Prefer executor-level integration first.

### Pitfall 2: dropping the raw output
If the compact result replaces the raw payload with no artifact path, debugging quality drops fast.
Always preserve a recovery path for large normalized results.

### Pitfall 3: trying to solve chat context, state storage, indexing, and decision logs all at once
That usually expands scope too far.
Ship the executor seam first, then extend to persistence/indexing policy.

### Pitfall 4: replacing the existing generic persistence guard too soon
Keep the old truncation/persist-to-file layer until the new normalizer is proven.

### Pitfall 5: creating a one-off skill per command family or incident
Keep this as one class-level umbrella skill and store session-specific implementation notes under `references/`.

## Recommended rollout order

1. Add the new normalizer module.
2. Add a raw-artifact helper if needed.
3. Integrate into the executor only for terminal results.
4. Add regression tests.
5. Run targeted test suites.
6. Only then consider broader categories or state-storage-specific metadata policies.

## Support files

- `references/hermes-terminal-output-normalizer-v1.md` — concrete file paths, categories, integration points, and the first validated MVP implementation pattern.
