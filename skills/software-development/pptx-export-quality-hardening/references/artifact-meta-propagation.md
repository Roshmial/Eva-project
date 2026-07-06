# PPTX artifact/meta propagation notes

Use this note when PPTX quality hardening has already produced internal `validation` / `quality`, but those fields are not yet visible in the real chat/file delivery path.

## Recommended propagation pattern

1. Keep one internal export-result helper, e.g. `build_message_export_result(...)`.
2. Return `buffer` for every format.
3. For PPTX, also return:
   - `validation`
   - `quality`
4. Make `build_message_export_stream(...)` unwrap only `buffer` to preserve the existing outward download contract.
5. In `build_message_export_attachment(...)`, attach `validation` + `quality` to the stored attachment payload when present.
6. In both reply builders, copy the same fields to top-level message metadata:
   - `generated_file_response`
   - `message_export`

## Why this split works

It preserves compatibility for callers that only need file bytes, while allowing higher layers to inspect artifact quality without re-running PPTX validation logic.

## Test shape

Add tests for both:
- attachment payload contains `validation` + `quality` for `.pptx`;
- generated `file_response` metadata propagates the same fields to both top-level meta and nested attachment.

Do not rely only on direct builder tests. Verify the real artifact/meta path too.
