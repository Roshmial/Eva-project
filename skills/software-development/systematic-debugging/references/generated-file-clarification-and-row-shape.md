# Generated-file clarification and synthetic row shape

Use this note when a chat/file route appears correct in tests but fails or degrades in live runtime during attachment creation.

## Failure pattern

Typical sequence:
1. User asks for a generated artifact with explicit format, for example `pptx`.
2. Assistant asks a clarification question.
3. User answers briefly without repeating the format.
4. Backend recomputes route selection from only the latest user turn and loses the original export intent.
5. System falls back to generic chat, wrong export format, or errors only when building the attachment.

## What to verify

- The exact user turn that triggered the failing task.
- Previous assistant message meta: especially `message_kind` and route-specific fields.
- Whether the backend reconstructs an effective user request before re-running route selection.
- Whether `detect_message_export_format(...)` and generate-intent checks run on the reconstructed request or only on the last short clarification reply.

## Durable fix pattern

- Preserve explicit export intent across clarification follow-ups when the prior user turn already requested a generated file.
- Add a regression test at the route-decision point, not only at the final export helper.
- Add a live probe that confirms the final artifact keeps the requested format (`pptx`, `docx`, etc.).

## Synthetic row pitfall

Generated-file pipelines often reuse existing export helpers by constructing a temporary assistant-message-like row.

Minimum safe shape usually includes:
- `id`
- `role`
- `created_at`
- `content`
- `meta_json`

If `role` is omitted, helper functions that assume a real assistant row may fail late with `KeyError: 'role'` or equivalent row-shape errors.

## Verification checklist

- Unit/regression test for clarification-preserved export format.
- Unit/regression test for synthetic row export helper path.
- Live runtime probe that checks:
  - `message_kind=file_response`
  - expected `export_format`
  - expected MIME type
  - actual attachment filename/bytes

## Session-derived example

In Hermes Web P0 file-generation work, the live bug was not the upstream model response. The upstream returned valid slide content, but `build_generated_file_reply()` created a synthetic export row without `role`, causing a live `KeyError: 'role'` during attachment creation. A second issue was route loss after clarification: the backend needed to preserve the original `pptx` intent even when the final user reply only contained details like slide count and emphasis.