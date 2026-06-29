# Generated document artifact vs regression drift

Use this note when `DOCX/PPTX/XLSX` output was intentionally restructured and an old regression still fails.

## Symptom pattern

- live artifact looks better than before;
- content is present and opens correctly;
- but tests still fail on things like:
  - exact `paragraph.text` concatenation;
  - exact table count;
  - assumption that `label: value` stays in one flat line;
  - assumption that the first table is the business table rather than title metadata.

## Decision rule

Treat this as possible **regression drift**, not immediate product failure.

Ask:
1. Did the artifact preserve the required user-visible meaning?
2. Did formatting improve via more native structure?
3. Did the new structure intentionally change how plain-text extraction linearizes the file?

If yes, update the regression to assert semantic guarantees:
- required headings exist;
- required values exist;
- bold/heading/table semantics survive;
- no tool/apology transcript leaked;
- file opens and matches the intended export type.

## Better assertions

Prefer:
- searching across all paragraphs and table cells;
- checking that a bold run exists somewhere appropriate;
- checking `>= 1` business table when title metadata may also be tables;
- probing the actual generated artifact locally and on the named live runtime.

Avoid:
- asserting one exact flattened string when the document now uses native blocks;
- assuming `document.tables[0]` is the business table after introducing title metadata tables;
- treating improved layout as a failure because serialization changed.

## Practical pattern

1. Confirm the product artifact with a dedicated probe script.
2. If the probe is green but the regression is red, inspect whether the regression is asserting old structure rather than broken behavior.
3. Patch the regression to the new semantic contract.
4. Re-run both the regression and the live probe.
