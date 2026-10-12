# Chat-task tail closure for Hermes Web runtime verification

Use this when a live cleanup pass is down to the last 1–2 acceptance tails after the main runtime is already green.

## What this session added

### 1. Generic follow-up answers need an explicit message kind
If a normal assistant reply is produced by the generic LLM path and no route-specific kind is assigned, set a stable default like `message_kind=chat_response`.

Why this matters:
- UI/runtime probes otherwise see `processing_status` -> `None` and the flow looks half-finished even when the content is correct.
- Follow-up probes like `Проанализируй предыдущий файл...` become harder to assert and easier to misread as a hang.

Verification pattern:
- Send a follow-up on a thread that already has meaningful prior context or an artifact.
- Wait until the last message is no longer `processing_status`.
- Assert `meta.message_kind == chat_response`.
- Also inspect `token_accounting` if the product exposes per-answer token metadata.

### 2. Upload-driven file-analysis contour must be verified as a real artifact flow
For `user uploads file -> agent analyzes -> returns csv/xlsx/json`, do not stop at `task completed`.

Verify all of these:
- the task leaves `processing_status`;
- final `message_kind` is the expected collection/result kind;
- `meta.attachments[]` exists;
- the attachment is visible in UI or returned in API payload;
- the file is actually downloadable / present at the reported path or URL.

### 3. In backend tests, patch before POST when the endpoint may dispatch immediately
For Hermes Web chat-task tests, `POST /messages` may enqueue and immediately process the task before the test manually calls `process_chat_task(...)`.

Implication:
- If you patch `call_hermes_messages` only after the POST, the real route may already have executed and fail for unrelated reasons.

Safer pattern:
1. Open the patch context first.
2. Perform the POST inside the patch context.
3. Poll the thread until the last message leaves `processing_status`.
4. Assert the final meta/content/artifact.

This is especially important for upload/file-analysis tests and other routes where immediate background dispatch is enabled.

### 4. Prod follow-up probes should reuse a thread with meaningful prior context
A generic follow-up like `Проанализируй предыдущий файл...` can legitimately stay unhelpful or appear stalled if sent in a fresh thread with no prior artifact/context.

Safer prod probe:
- first create or identify a thread where the previous step already produced a file/result;
- then run the follow-up in that same thread;
- only treat `processing_status` persistence as a tail if the thread really contains the prerequisite context.

## Short checklist
- Do I have a real post-fix thread, not an old pre-fix one?
- Does the last message get a stable terminal `message_kind`?
- Did I verify attachment existence, not just status text?
- In tests, did I patch the LLM call before submitting the message?
- For follow-up prompts, does the thread actually contain the previous file/result being referenced?
