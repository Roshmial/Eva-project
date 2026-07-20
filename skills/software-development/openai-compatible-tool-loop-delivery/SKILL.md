---
name: openai-compatible-tool-loop-delivery
description: Diagnose, implement, and verify real user-facing tool execution when a local app talks to an OpenAI-compatible model or adapter.
---

# Purpose

Use this skill when a local-first chat or agent product appears to be connected to an OpenAI-compatible backend, but real tool execution is missing, unstable, or only partially works.

Typical symptom set:
- the model answers in plain text instead of triggering tools
- adapter-level direct probes return `tool_calls`, but the frontend route still behaves like plain chat
- first turn works, second turn after tool execution fails or times out
- provider returns errors like `system message must be the first message`

# Core rule

Always debug tool mode across the whole chain, not just one layer:
1. provider / upstream model behavior
2. adapter normalization into OpenAI-compatible `tool_calls`
3. backend execution loop
4. real authenticated frontend/API path

Do not stop at a successful adapter probe. The task is only done when a real user-path request shows evidence that a tool was actually executed.

# Workflow

## 1. Verify the route actually in use

Confirm the live chain:
- frontend or user API route
- backend service
- adapter/proxy endpoint if present
- upstream provider endpoint

Record the actual model and endpoint from the running process or health endpoint, not from assumptions.

## 2. Probe the adapter directly

Before touching backend logic, prove whether the adapter already does the OpenAI-compatible part:
- send `tools` and `tool_choice`
- check whether the first response returns structured `message.tool_calls`
- check whether second-turn replay with `role=tool` succeeds
- if the provider uses provider-specific state like `functions_state_id`, verify it is preserved between turns

If direct adapter probes pass, the likely missing piece is backend execution, not provider compatibility.

## 3. Inspect backend execution behavior

For the user-facing backend, check four things explicitly:
- does it send `tools` in the first request?
- does it read `tool_calls` from the first response?
- does it execute the requested tool locally and append a `role=tool` message?
- does it make the second model call and return the final assistant text?

A common failure mode is that the backend only extracts `message.content` and completely ignores `tool_calls`.

## 4. Normalize message ordering before blaming the provider

If upstream returns a 400 like `system message must be the first message`, do not patch prompts blindly.

Check normalized message order after all local transformations. In mixed histories, move `system` messages to the front before sending to the provider. If there are several `system` messages, merge them into one deterministic system block.

## 5. Align timeout contours

Tool mode often needs a second upstream round-trip, so verify timeouts at both layers:
- backend request timeout
- adapter upstream timeout

A common contour bug is: backend allows a long wait, but the adapter still times out earlier on the second tool-loop turn. Fix the shorter inner timeout first.

## 6. Keep tool scope small first

For first enablement, start with a tiny built-in tool set that is easy to verify, such as:
- current time
- current date

This proves the loop works without immediately coupling to large external tool catalogs.

## 7. Verify with a real authenticated user-path probe

Final verification must use the same route as the product:
- authenticate
- create or open a thread
- send a message that clearly requires a known tool
- poll until completion
- inspect the stored/public assistant message metadata

Look for explicit proof such as:
- `tool_loop_used: true`
- non-empty `tool_trace`
- final answer matching tool output rather than model hallucination

# Implementation pattern

## Minimum backend additions

1. Extend the model-call helper so it can optionally send:
- `tools`
- `tool_choice`

2. Preserve response fields needed for tool execution:
- `tool_calls`
- `finish_reason`
- provider-specific state such as `functions_state_id`

3. Add a small backend tool executor:
- parse tool arguments safely
- run local tool implementation
- serialize tool result back into the transcript

4. Wrap it in a bounded loop:
- first model call
- if `tool_calls` exist, execute tool(s)
- append assistant tool-call message + tool result message
- second model call
- stop when no more `tool_calls` remain

## Good metadata to keep

Persist or surface these fields when available:
- `tool_loop_used`
- `tool_rounds`
- `tool_trace`
- `functions_state_id`
- `finish_reason`

They make frontend acceptance and future debugging much faster.

# Pitfalls

## Pitfall: declaring success after adapter-only testing

Direct adapter success is necessary but not sufficient. The real bug may still sit in the backend route that ignores `tool_calls`.

## Pitfall: trusting final text without proof of execution

A model can answer a time/date question plausibly without any tool execution. Require metadata proof such as `tool_trace`.

## Pitfall: fixing only the outer timeout

If the adapter has a shorter upstream timeout than the backend, tool mode can still fail mid-loop even after the backend timeout is increased.

## Pitfall: leaving `system` messages scattered in history

Some providers reject this even though others tolerate it. Normalize ordering before concluding the provider is incompatible.

# Done criteria

The task is done only when all of the following are true:
- targeted tests cover helper changes and the tool loop
- adapter tests still pass
- backend tests prove `tools` are sent and tool calls are replayed correctly
- live services are restarted on the target contour
- an authenticated frontend/API probe completes successfully
- the final assistant message metadata proves a tool actually ran

# References

- See `references/gigachat-hermes-web-tool-loop.md` for a concrete local-first pattern: adapter normalization, backend tool loop, `functions_state_id`, message ordering, and timeout contour alignment.
