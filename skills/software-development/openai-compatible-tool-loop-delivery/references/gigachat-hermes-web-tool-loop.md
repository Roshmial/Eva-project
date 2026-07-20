# GigaChat + Hermes Web tool-loop pattern

Session learning distilled into a reusable contour-level recipe.

## Root cause split

The failure was not a single bug. It was a chain:
1. upstream GigaChat tool mode worked only through the adapter, not as raw OpenAI-style upstream behavior
2. adapter already normalized native function flow into OpenAI `tool_calls`
3. user-facing backend still treated the model as plain chat and ignored `tool_calls`
4. once backend tool mode was added, a second contour bug remained: adapter timeout was shorter than backend timeout

## Concrete fixes that mattered

### 1. Backend must execute the tool loop itself

Adapter-level success did not make frontend tool mode work automatically.

Required backend behavior:
- send `tools` + `tool_choice`
- read first-turn `tool_calls`
- preserve `functions_state_id`
- execute local tool implementation
- append assistant tool-call message and `role=tool` result message
- do second model call

## 2. Preserve provider-specific state

For GigaChat, `functions_state_id` needs to survive into the second turn. Without this, multi-step tool replay is fragile.

## 3. Normalize `system` messages aggressively

Provider rejected requests with:
- `Invalid params: system message must be the first message`

Reliable fix:
- collect all `system` messages
- move them to the front
- merge them into one system block when several are present

## 4. Timeout contour must be aligned end-to-end

Observed pattern:
- backend request completed budget: long enough
- adapter upstream timeout: too short
- result: second tool-loop turn died with upstream timeout even though outer request still had time

Practical fix in this contour:
- increase `GIGACHAT_ADAPTER_TIMEOUT_SECONDS`
- verify the live process environment after restart, not just the `.env` file

## 5. Verification proof should come from message metadata

A plausible final answer is not proof of tool execution.

Useful acceptance fields:
- `tool_loop_used: true`
- `tool_rounds`
- `tool_trace`
- `functions_state_id`
- final model name

## Example acceptance signal

A successful user-path probe showed:
- authenticated API thread creation
- message asking for current UTC time
- final assistant reply with current time
- metadata containing `tool_loop_used: true`
- metadata containing `tool_trace[0].name = get_current_time`
- metadata containing tool result with the exact UTC timestamp returned to the user

## Minimal first tool set

For first enablement, built-in backend tools should stay tiny and deterministic:
- `get_current_time`
- `get_current_date`

This keeps acceptance easy and avoids coupling initial verification to wider tool catalogs.
