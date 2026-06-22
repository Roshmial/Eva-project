---
name: chat-runtime-reply-routing
description: Route chat replies through deterministic backend handlers before LLM fallback when the user intent is operational (export to file, attachment delivery, structured reply handling), and budget timeouts across model fallback chains.
---

# Purpose

Use this skill when a chat/web runtime sometimes sends an operational user reply back into the LLM instead of handling it deterministically in backend code. Typical symptoms:
- the assistant asks whether to return one message or a file, the user answers "better as a file", and the agent stalls or crashes;
- attachment/media replies are stored as plain text instead of first-class attachments;
- every model attempt gets the same long timeout, making fallback chains too slow;
- structured follow-up replies (`clarification_request`, `approval_request`, file/export replies) are mixed with normal free-text generation.

This skill is especially relevant for Hermes-style local-first chat runtimes where backend message processing already owns task queues, message metadata, attachments, and export endpoints.

# Core rule

If the user message is an operational instruction that the backend can satisfy directly, do **not** send it through the normal LLM path first. Short-circuit it inside the chat-task processor and emit a normal assistant message with the correct metadata and attachments.

# When to trigger

Use this skill when you see any of the following:
1. The user is replying to a prior assistant offer about format or delivery: one message vs file, export, attachment, download.
2. The backend already has enough local state to satisfy the request: previous assistant message, export endpoint, generated file path, existing attachment metadata.
3. The system has a model fallback chain and long per-attempt timeouts are causing bad UX.
4. The runtime supports `MEDIA:` or attachment metadata and must not confuse those with export requests.
5. The user sends a short complaint/follow-up like `где файл`, `не работает`, `непонятно`, `повтори ещё раз` after a substantive assistant reply.

For these short complaint follow-ups, do not throw the whole thread back into broad LLM reasoning. Prefer a focused follow-up context built from:
- the latest substantive user request;
- the latest substantive assistant answer;
- the short complaint itself.

Important runtime guard: an *empty/default* `request_policy` object must **not** disable this focused-follow-up path. In Hermes-style runtimes the frontend/backend often sends a policy envelope like `source_mode=''`, `model_preference='auto'`, empty `explicit_source_ids`, and empty `connector_targets`. Treat that as **no effective override**. Only a policy with real source/model constraints should block the focused complaint-recovery path.

This keeps the runtime from losing the user's real complaint inside a long chat history and is especially important for file delivery and post-failure recovery.

# Recommended implementation pattern

## 1) Add deterministic routing before the normal LLM call

In the chat-task processor, inspect the latest user message and branch in this order:
1. explicit backend-only reply routes (export/file delivery, structured approvals/replies);
2. domain-specific deterministic builders (for example dashboard builders);
3. standard LLM processing.

Keep the short-circuit high enough in the flow that the user does not pay LLM latency for a backend-only action.

## 2) For export/file replies, build from the previous assistant message

When the user says "better as a file" or equivalent:
- detect export intent from the latest user text;
- locate the previous assistant message in the thread;
- generate the requested export format from that message;
- create a real attachment payload;
- return a normal assistant message with `message_kind = file_response` (or the project’s equivalent) and the attachment in `meta.attachments`.

Do **not** ask the LLM to restate or reinterpret the same export intent when the backend already has the previous answer and export builders.

## 3) Attachments must be first-class objects, not just text markers

For generated export attachments include durable metadata such as:
- `assistant_generated: true`
- `source: message_export` (or equivalent source tag)
- `original_name`
- `stored_name`
- `relative_path`
- `local_path`
- `mime_type`
- `size_bytes`
- `export_format`
- `download_url` if the UI expects one, or let post-processing fill it.

The important part is that the UI/download flow must see the result as a standard attachment, not as arbitrary assistant text.

## 4) Prevent false positives from media tokens

If the project already supports `MEDIA:/path/to/file` in assistant content, do not let export detection trigger on messages that contain `MEDIA:`. Otherwise you will accidentally convert a legitimate media-delivery flow into an export-from-previous-message flow.

Treat these as separate paths:
- export intent from the user;
- media attachment markers in generated assistant text.

## 5) Budget timeout by attempt position, not one flat timeout for all tries

Bad pattern:
- every attempt in a fallback chain gets the same 180s timeout.

Better pattern:
- intermediate retries get a shorter timeout;
- the last viable model attempt gets the full timeout;
- reasoning models can have their own dedicated timeout budget.

Practical rule:
- `retry_timeout` for early fallback attempts;
- `api_timeout` for the last standard attempt;
- `reasoning_timeout` for the reasoning route.

Also write the chosen timeout into attempt metadata so debugging shows which attempt waited how long.

## 6) Verify with focused tests first, then full smoke

Minimum regression tests to add:
1. fallback retry uses short timeout first and full timeout on the last attempt;
2. user reply like "лучше сразу в файл" exports the previous assistant answer and produces an attachment;
3. media-token flow still works and is not hijacked by export detection.

After focused tests pass, run the full backend smoke suite.

# Pitfalls

- Do not leave format-choice replies to the LLM if the backend already knows how to export the previous answer.
- Do not store export results as plain assistant text without attachment metadata.
- Do not route `MEDIA:` messages through export-intent detection.
- Do not apply the maximum timeout to every step in a model fallback chain.
- Do not stop after patching code; verify both the targeted regression and the full smoke suite.

## Verification checklist

- User reply requesting a file produces a completed assistant message, not a stuck pending/error state.
- The resulting assistant message contains exactly one export attachment with correct metadata.
- Attachment download/open path works through the same mechanism as other assistant-generated files.
- Model-attempt metadata shows the timeout used per attempt.
- Assistant message metadata carries token accounting for every reply path: exact usage when the provider returned it, and estimated response tokens when exact usage is unavailable.
- Backend smoke tests pass after the change.

## Token accounting rule

Для Hermes-style chat runtime полезно писать token accounting не только для чистого LLM-answer path, но и для deterministic backend replies тоже.

Минимум, который стоит сохранять в assistant meta:
- `token_accounting.response_text_tokens_estimated`
- `token_accounting.estimator`
- `token_accounting.llm_usage_exact`

Если upstream/provider реально вернул usage, дополнительно сохранять:
- `token_accounting.llm_prompt_tokens`
- `token_accounting.llm_completion_tokens`
- `token_accounting.llm_total_tokens`

Практический смысл:
- exact usage нужен для маршрутов, где ответ действительно строился через model/provider;
- estimated usage нужен как fallback для deterministic routes, чтобы в логах и postmortem не было пустых дыр по расходу и длине ответа.

Это особенно важно при mixed routing, где часть ответов идёт через LLM, а часть — через backend handlers (`file_response`, `job_created/job_reused`, `clarification_request`, `dashboard_result`, `collection_execution_result`).

# Support files

- See `references/export-reply-and-timeout-patterns.md` for a compact implementation note covering export short-circuiting, `MEDIA:` guardrails, and timeout budgeting.
