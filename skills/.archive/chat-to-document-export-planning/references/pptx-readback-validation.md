# PPTX read-back validation

Use this pattern when strengthening a chat-to-PPTX export core without breaking the public download contract.

## Why

A PPTX builder can succeed at `presentation.save(...)` and still produce a weak or suspicious artifact:
- wrong slide count;
- empty text shapes;
- broken structure that only shows up when re-opened;
- internal builder contract drift that accidentally breaks the external export endpoint.

## Preferred implementation

1. Render the presentation into bytes.
2. Re-open those bytes as a temporary `.pptx`.
3. Feed that file through the same normalized XML/zip intake used for source-deck analysis.
4. Build a compact validation report:
   - `valid`
   - `slide_count`
   - `text_shape_count`
   - `slide_titles`
   - `aspect_ratio`
5. Return the validation report to backend orchestration.

## Contract rule

If the internal builder starts returning a richer object such as:

`{buffer, validation}`

then the public export/download route must keep returning the raw file-like `buffer` until the external API is intentionally changed.

## Regression targets

Add tests for both layers:
- validator succeeds on a real fixture `.pptx`;
- generated PPTX returns a successful read-back validation report;
- existing export endpoint still returns a normal downloadable `.pptx` response.

## Anti-patterns

- Do not build a second unrelated parser for validation when the normalized intake path already exists.
- Do not expose internal validation metadata by accident through a file endpoint that historically returned only bytes.
- Do not mark validation complete from helper-level success alone; re-open the produced artifact.