# Presentation follow-up and explicit-slide export debugging

Use this pattern when a chat/product flow goes through `draft -> markup -> export` and the user reports that a follow-up only reformats the tail, or that `PPTX/DOCX` export explodes into too many sections/slides.

## Debug split to force early

Do not treat it as one vague "presentation quality" bug. Split the path into at least two checkpoints:

1. `draft -> markup`
   - Did the follow-up route use the right source draft?
   - Did it rebuild the whole presentation or only the last chunk after clarification?
   - Did the prompt preserve slide order / approximate slide count?
   - Did the model invent links/assets because the prompt lacked a truthful degradation rule?

2. `markup -> export`
   - Does the export parser understand explicit slide markers such as `Слайд 1: ...`?
   - Are markdown separators like `---` becoming content instead of structure?
   - Are inner bold headings (`Ключевые элементы`, `Типовые слои`, etc.) being promoted into new slides/sections?

If you skip this split, you can fix routing while leaving the exporter broken, or fix the exporter while still feeding it the wrong source.

## Concrete probe pattern

For the real affected thread/artifact:
- inspect the exact follow-up prompt sent to the model;
- inspect whether the route is marked focused and what draft it pulled in;
- inspect the reply opening to confirm it restarts from `Слайд 1`, `Слайд 2`, ... instead of only rewriting the tail;
- then run a real export and inspect resulting slide count plus first several slide titles.

Healthy signal:
- follow-up reply starts from the beginning of the deck;
- export slide titles track intended deck headings (`Титульный`, `Определение BI`, `Зачем нужно BI`, ...), not inner subsection labels.

## Durable implementation pattern

When assistant output already contains explicit slide markers, treat them as the source of truth for export segmentation:
- parse `Слайд N: ...` / `Слайд N - ...` as level-1 section boundaries;
- ignore `--- / ___ / ***` as separators, not paragraph content;
- in explicit-slide mode, do not let level-2/inner headings open new slides;
- keep title-slide label/value content if it is a real first slide, not metadata noise.

## Regression contract

At minimum, add tests that prove:
- clarification follow-up still preserves original `pptx/docx/presentation` intent;
- presentation enhancement follow-up uses the last substantive draft, not the clarification message;
- explicit `Слайд N:` markers become export section boundaries;
- inner headings do not inflate slide count.

## Live acceptance heuristic

A good repair usually produces all of these together:
- live health still green after deploy;
- follow-up route is focused on the full deck;
- fake web links like `example.com` disappear in favor of recommendation text when web retrieval is unavailable;
- exported slide count drops materially versus the broken case.

This does not guarantee final design quality, but it proves that routing and segmentation are fixed before layout-polish work begins.
