---
name: single-file-presentation-artifacts
description: Use when building or debugging local-first single-file presentation artifacts and microservices that generate them.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Single-File Presentation Artifacts

Use this skill when the user wants a local-first presentation generator, a microservice that emits presentation files, or debugging of self-contained HTML deck artifacts such as Bento-style files.

## When to use
- A presentation should be generated as a file artifact, not only as JSON or prose.
- The runtime is local-first and produces a self-contained HTML deck.
- The user asks for a microservice around an existing deck shell/runtime.
- A generated presentation opens as a blank page, white sheet, or seemingly empty deck.

## Core approach
1. Reuse the vendor/runtime shell instead of rebuilding the presentation runtime yourself.
2. Modify only the document payload block inside the shell.
3. Keep the first delivery path conservative: a minimal, boring deck that definitely renders is better than a fancy deck that might open blank.
4. Verify the produced artifact as a real file, not only as API output.

## Preferred architecture
- Keep the deck runtime as an upstream artifact checked into `data/` or downloaded on startup.
- Put generation logic in a thin local service layer.
- Expose a narrow API such as:
  - `GET /health`
  - `POST /render`
  - `GET /artifact/{name}`
- Save outputs to an `output/` directory and hand back the file path plus download path.

## Implementation rules

### 1. Splice only the document block
For Bento-style files, replace the `application/bento+json` block and leave the compressed runtime blocks untouched.

### 2. Escape JSON safely
Escape `<` as `\u003c` before embedding JSON into the inline script block.

### 3. Keep first-pass decks conservative
For smoke-test decks:
- prefer `transition: "none"`;
- prefer simple text and shape elements;
- prefer system fonts such as `system-ui, sans-serif`;
- avoid morph-heavy, animation-heavy, or fancy layout assumptions until the baseline artifact is proven to render.

### 4. Do not assume API success means visual success
A render endpoint returning `200 OK` only proves file generation. It does not prove the deck actually opens or displays content.

## White-page / blank-deck debugging checklist
If the user reports a blank page or empty-looking deck:
1. Parse the produced file and verify the embedded document block exists.
2. Check that the JSON is valid and `slides` is non-empty.
3. Inspect whether the shell template itself had an empty starter document and whether your splice actually replaced it.
4. Simplify the generated deck:
   - remove morph transitions;
   - use plain text rows instead of dense rich text blocks;
   - use `system-ui, sans-serif`;
   - keep backgrounds and text contrast obvious.
5. Check browser/runtime requirements. Some self-contained HTML runtimes need modern browser APIs; if so, note that requirement explicitly in delivery.
6. Re-render and verify the output file again.

## Delivery rules
- Always give the user the actual artifact file.
- Also give the local run path: service URL, health check, and exact output path.
- If visual verification is limited, say exactly what was verified and what browser/runtime requirement remains.

## References
- `references/bento-runtime-notes.md` — Bento-specific generation and debugging notes.

## Pitfalls
- Treating a created file as equivalent to a valid deck.
- Generating an ambitious first demo with morphs and custom fonts before proving the minimal path.
- Overwriting the runtime shell instead of splicing the payload block.
- Forgetting to mention browser requirements for self-contained HTML runtimes.
