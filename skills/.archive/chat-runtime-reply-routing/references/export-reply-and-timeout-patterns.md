# Export reply and timeout routing patterns

## Problem shape

A chat runtime may already have enough local state to satisfy a follow-up user reply like "better as a file", but still sends that reply through the normal LLM path. This creates pointless latency and can break the conversation state.

## Durable fix pattern

### 1. Short-circuit export intent in the chat-task processor

Detect explicit file/export intent from the latest user message before the normal LLM branch. If matched:
- find the previous assistant message in the thread;
- build the export locally from that message;
- return an assistant message with `message_kind = file_response` and a standard attachment payload.

### 2. Preserve the existing media flow

If the message contains `MEDIA:`, skip export detection. `MEDIA:` belongs to attachment delivery, not to export-intent routing.

### 3. Use attachment metadata that the UI already understands

Useful fields:
- `assistant_generated: true`
- `source: message_export`
- `original_name`
- `stored_name`
- `relative_path`
- `local_path`
- `mime_type`
- `size_bytes`
- `export_format`

### 4. Timeout budget by attempt stage

A practical split:
- early fallback attempts: short retry timeout;
- last standard attempt: full standard timeout;
- reasoning model: separate reasoning timeout.

This avoids spending the full long timeout on every failed step while still preserving a long final attempt when there is no better fallback left.

## Regression tests worth keeping

1. Runtime-error retry uses short timeout on the first model and full timeout on the last fallback.
2. User reply "лучше сразу в файл" produces a file attachment from the previous assistant answer.
3. `MEDIA:` path still produces the original assistant-generated attachment content.
4. Full backend smoke still passes after the routing change.
