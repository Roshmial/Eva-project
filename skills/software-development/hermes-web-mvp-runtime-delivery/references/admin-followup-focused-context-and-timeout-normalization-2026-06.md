# Admin follow-up focused context and timeout normalization (2026-06)

When diagnosing Hermes Web admin chats on prod, separate two failure classes that look similar in UI but have different roots.

## 1. Short follow-up after a long assistant plan

Observed pattern:
- assistant gives a long generic plan/explanation;
- user replies with a very short confirmation like `Да, сделай`, `давай`, `запускай`;
- failing `chat_task` shows empty `request_policy_json` and generic `last_error=timed out`.

Interpretation:
- this is usually not a real connector/action/file route;
- the turn fell back to the generic `call_hermes_api(...)` path with too much surrounding history.

Durable fix pattern:
- detect short follow-up confirmations explicitly;
- detect whether the previous substantive assistant message was long enough to justify narrowed context;
- build a focused follow-up prompt from:
  - last substantive user request,
  - last substantive assistant reply,
  - current short confirmation;
- send that to the standard model path instead of the full history path.

Useful helper split:
- `is_short_followup_confirmation()`
- `latest_substantive_assistant_message_text()`
- `should_use_focused_followup_context()`
- `build_focused_followup_messages()`

## 2. Generic timeout mislabeled as file-generation failure

Observed anti-pattern:
- `normalize_public_error_text()` maps any `timed out` to `Не удалось сформировать файл...`.

Why it is harmful:
- operators start debugging export/file flow even when no file path was involved;
- user sees a false explanation and loses trust in the system state.

Durable rule:
- generic `timed out` must normalize to a generic upstream-timeout message;
- file-specific timeout text is allowed only when the failing path is actually `message_export` / `generated-file`.

## Minimum verification

On the live host verify all of these explicitly:
- historical failing `chat_task` really had empty `request_policy_json`;
- `last_error` contains generic `timed out` rather than file-specific markers;
- `is_short_followup_confirmation("Да, сделай") -> true`;
- `should_use_focused_followup_context(...) -> true` for the repro pattern;
- `normalize_public_error_text("timed out")` returns a generic timeout message, not `Не удалось сформировать файл...`.

## Pitfall

Do not overstate this as a full action system. Focused follow-up context is a containment fix for generic chat turns. If the product truly needs deterministic execution of TG API / export / connector operations, that is a separate architectural step: explicit structured action-routing, not just better prompting.