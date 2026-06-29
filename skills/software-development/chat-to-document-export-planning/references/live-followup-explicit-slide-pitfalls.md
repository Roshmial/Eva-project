# Live follow-up explicit-slide pitfalls

Use this reference when a chat-first export pipeline already has a draft presentation and the user asks for a second-pass upgrade such as formatting, slide markup, or web illustrations.

## Durable lessons

### 1. Distinguish three failure layers

Do not collapse all bad PPTX outcomes into one bug. Diagnose separately:

1. follow-up routing / context selection;
2. parser / section-boundary recognition;
3. composition / slide-density tuning.

Typical symptom mapping:
- only the tail of the deck gets reformatted -> routing/context problem;
- `Ключевые элементы` / `Типовые слои` become slide titles -> parser boundary problem;
- deck is structurally correct but too many `продолжение 2/3` slides remain -> composition problem.

### 2. Explicit slide markers must be first-class

In live model output, explicit slide markers may appear as:
- `Слайд 2: Определение BI`
- `Слайд 2 - Определение BI`
- `=== Слайд 2: Определение BI ===`

The parser should normalize all of these into the same heading/slide-boundary representation.

### 3. Explicit-slide decks should only split on explicit-slide markers

Once a draft already contains explicit slide markers, internal bold subsections such as:
- `Ключевые элементы BI`
- `Типовые слои`
- `Вывод`

must stay inside the current slide unless there is a new explicit `Слайд N:` boundary.

### 4. Follow-up prompt must constrain output shape, not just content

For presentation-enhancement follow-ups, the prompt should explicitly say:
- rebuild the whole deck, not only the tail;
- preserve original order and approximate number of slides;
- start each slide with `Слайд N: Название`;
- do not use `=== ... ===` wrappers;
- do not turn intra-slide subsections into new slides.

### 5. Verify text regeneration and file export separately

A regenerated assistant answer may look improved while the PPTX export still misbehaves. Always verify:
- regenerated text structure;
- resulting PPTX slide count and first several slide titles/content blocks.

## What improved in this session

The durable fixes that proved useful were:
- adaptive chunk sizing for short bullet-heavy sections;
- parser support for decorated explicit slide markers;
- stricter follow-up prompt to prevent outline spam.

## What remains a later-stage problem

If the deck is still heavy after the above fixes, the next step is semantic condensation / slide-density tuning rather than more parser changes.