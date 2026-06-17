# Chat message timestamp semantics

Use this when the user reports that assistant message times are wrong, "jump", or equal the original user request time even though the model answered later.

## Symptom pattern

- In chat UI, the assistant bubble shows the same timestamp as the triggering user message.
- Backend task metadata shows the run actually finished much later.
- The problem is most visible on slow replies, queued jobs, or long model runs.

## Root-cause pattern

A placeholder assistant message is inserted immediately when the user sends a request:
- `content = "Готовлю ответ…"`
- `meta.pending = true`
- `created_at = request timestamp`

Later, when processing completes, backend updates only:
- `content`
- `meta_json`

and leaves `created_at` unchanged.

Result: frontend faithfully renders `message.created_at`, but that value still reflects placeholder creation time, not real answer completion time.

## Durable repair path

For chat-task based assistant replies:
1. Capture one `finished_at = now_iso()` at task completion.
2. Update the assistant message with:
   - final `content`
   - final `meta_json`
   - `created_at = finished_at`
3. Update `chat_tasks.finished_at` with the same value.
4. Prefer also updating `threads.updated_at` with that same timestamp for consistent ordering.
5. Apply the same timestamp rule to error finalization, not only success, so failed assistant turns also reflect when processing actually ended.

## Verification pattern

Do not stop at code inspection.

Verify at two levels:

### 1. DB/API verification

For a freshly created task, compare:
- user message `created_at`
- assistant message `created_at`
- task `finished_at`

Expected after the fix:
- `assistant_message.created_at == chat_tasks.finished_at`
- assistant time may differ from user message time

### 2. UI verification

Confirm the chat bubble time is sourced from `message.created_at` and now reflects the real completion moment.

## Good regression assertion

For a background-processed chat test, assert:
- task status becomes `completed`
- assistant message `meta.pending == false`
- assistant message `created_at == task.finished_at`

Do not overfit the test to `assistant.created_at != user.created_at`, because fast mocked runs can complete within the same second and still be correct.
