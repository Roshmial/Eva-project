# Plan-based export checklist

Use this when hardening backend-generated DOCX/PPTX artifacts from chat output.

## Session-derived durable lessons

1. Shared sanitation must happen before format-specific parsing.
2. Technical tail can survive surprisingly far into the pipeline if tests only assert final titles or slide counts.
3. PPTX renderer should not add user-visible service labels such as:
   - `Hermes Web export`
   - `Hermes Web generated export`
   - format badges
   - table badges
4. Plan items should reflect presentation units, not arbitrary text chunks.
5. Typography changes must be verified on actual runs/text frames in generated files, not assumed from constants.

## Good regression targets

### DOCX
- prelude like “I cannot directly create a binary file” is absent;
- tail like “you can create a new presentation” is absent;
- headings/bullets/tables still survive;
- default font is `Arial 12`.

### PPTX
- prelude/tail are absent;
- raw `Слайд N — ...` wrappers do not appear in slide text;
- title/subtitle/body typography matches required defaults;
- specialized slide kinds still render:
  - comparison
  - roadmap
  - risks
  - table
- intermediate source/plan tests prove technical tail was removed before rendering.

## Refactor shape to prefer

`normalize_document_export_body(...)`
-> `extract_presentation_source_from_thread(...)`
-> `build_presentation_plan(...)`
-> typed slide renderers

## Anti-patterns

- topic-name switches controlling export mode;
- frontend-only cleanup for backend-generated artifacts;
- validating only the public reply text while never opening the generated file;
- preserving historical broken exports as a reference implementation.
