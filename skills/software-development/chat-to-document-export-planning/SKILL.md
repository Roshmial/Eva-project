---
name: chat-to-document-export-planning
description: Build and harden chat-to-DOCX/PPTX export pipelines by separating sanitation, content extraction, planning, rendering, and regression verification.
---

## Presentation export packing policy

For PPTX exports, bias planning toward `1 theme = 1 slide` whenever the content is still plausibly readable.

- If the assistant already produced explicit slide markers (`Слайд 1`, `Слайд 2`, headings used as slide boundaries), preserve that structure by default instead of re-inventing a new outline.
- In explicit-slide mode, do not stack extra service slides on top of a user/agent-supplied cover structure. Avoid `auto title + auto overview + explicit Титульный` duplication.
- Before creating `продолжение N`, first try moderate font shrink within readable bounds. Use continuation only after the slide would otherwise become materially unreadable.
- Favor controlled merge of short adjacent sections when the previous slide still has real space; do not open a fresh slide just because a new section starts.
- Keep special layouts (`comparison`, `roadmap`, `risks`) more conservative than plain content slides, but still prefer mild text compression over premature splitting.

# When to use

Use this skill when a chat-first product needs to export assistant output into user-facing DOCX or PPTX artifacts and the current pipeline is leaking technical chatter, formatting noise, or raw conversational structure into the final file.

Typical triggers:
- exported PPTX contains service text like inability disclaimers, backend notes, or “you can create a new presentation” tails;
- exported DOCX/PPTX is assembled directly from raw markdown/text dumps rather than a normalized content model;
- slide count explodes because the system chunks text mechanically instead of planning presentation units;
- typography or layout defaults need to be enforced consistently across generated files;
- a backend route currently “works” but is held together by topic-specific hardcode.

# Core principle

Do **not** fix this class of issue by stacking more topic-specific `if` branches around raw export text.

Instead, move to a staged pipeline:
1. sanitize export body;
2. extract normalized presentation/document source from the sanitized body;
3. build an intermediate plan;
4. render the artifact from that plan;
5. verify with regression tests on real generated files.

# Preferred architecture

## 1) Sanitation layer first

Create or strengthen a backend sanitation step that removes:
- inability disclaimers like “I cannot directly create a binary file…”;
- assistant follow-up tails like “you can create a new presentation…” or “I can help refine details…”;
- backend/service labels like `Hermes Web export`, `generated export`, format badges, or similar non-user-facing metadata;
- duplicate separators and empty chatter before the first meaningful content anchor.

Sanitation should happen **before** DOCX/PPTX-specific parsing so both formats benefit from the same cleanup logic.

## 2) Source extraction layer

Introduce a source extractor such as:
- `extract_presentation_source_from_thread(...)`

Responsibilities:
- consume sanitized body text;
- parse headings, bullets, numbered items, labels, and tables into a normalized structure;
- separate title-slide labels (`Заголовок`, `Подзаголовок`) from content sections;
- normalize section titles (for example, strip `Слайд N — ...` wrappers);
- keep tables as structured payloads rather than flattening them too early.

The extractor should be general-purpose and must not contain topic names like ITFM, ERP, etc.

## 3) Planning layer

Introduce a plan builder such as:
- `build_presentation_plan(...)`

The plan should describe presentation units, not raw text chunks. Typical plan item kinds:
- `title`
- `overview`
- `content`
- `cards`
- `comparison`
- `roadmap`
- `risks`
- `table`

Heuristics belong here, not in the renderer. Examples:
- sections with option/variant language -> `comparison`;
- numbered implementation steps -> `roadmap`;
- risk/constraint language -> `risks`;
- label-only sections -> `cards`;
- tables remain `table`.

### Explicit slide outline mode

If the source already arrives as an explicit slide draft (`Слайд 1: ...`, `Слайд 2: ...`, or normalized equivalents), planning must switch to an `explicit_slide_mode` instead of layering generic presentation scaffolding on top.

In this mode:
- suppress auto-generated `overview` slides;
- suppress title-slide preview bullets derived from later sections;
- treat a first section named `Титульный` / `Title` / `Cover` as the source for the system title slide and do **not** render it again as a normal content slide;
- still allow short adjacent sections to merge when density heuristics say they fit, but preserve the second section as an internal labeled subsection rather than losing it.

Rule of thumb: when the model already gave a slide-by-slide outline, do not inflate the deck with an extra `title + overview + cover-content` trio.

## 4) Rendering layer

Renderer functions should consume plan items and stay mostly dumb:
- `render_pptx_from_plan(...)` or equivalent typed slide functions;
- DOCX builder should render structured blocks/tables without reintroducing service metadata.

Renderer responsibilities:
- apply visual layout and typography;
- map plan item kinds to slide/document structures;
- avoid content selection logic that belongs upstream.

# Formatting defaults captured from this session

For this user’s export expectations:
- DOCX default body font: `Arial`, `12 pt`.
- PPTX title: `Arial`, `20 pt`.
- PPTX on-slide subtitles: `Arial`, `14 pt`.
- PPTX body text: `Arial`, `12 pt`.

If changing fonts/sizes, update regression tests in the same change.

# Implementation sequence

1. Add/strengthen sanitation in the shared export-body normalization path.
2. Add the extractor that builds structured sections/items/tables.
3. Add the plan builder that converts extracted sections into typed plan items.
4. Switch PPTX generation to consume the plan.
5. Keep DOCX on the shared sanitation path even if its renderer remains simpler.
6. Remove user-visible service badges, backend notes, and format labels from rendered artifacts.
7. Run targeted regression tests on actual generated DOCX/PPTX outputs.

# Testing protocol

Always verify with tests that inspect the produced files, not just helper return values.

Minimum regression coverage:
- DOCX omits technical prelude/tail and preserves Word structure;
- DOCX default font is correct;
- PPTX uses widescreen/expected geometry if applicable;
- PPTX omits technical prelude/tail and raw `Слайд N — ...` wrappers;
- PPTX typography defaults are correct on real runs/text frames;
- specialized slide types still render correctly (`comparison`, `roadmap`, `risks`, `table`);
- source extraction / plan-building tests confirm that technical tail does not survive into the intermediate plan.

# Pitfalls

- Do not rely on frontend masking to hide backend export pollution.
- Do not treat old exported files as ground truth if they were produced by a broken builder.
- Do not encode one business topic as the switch for a rendering mode.
- Do not let table badges, export labels, or service captions leak into user-facing slides.
- Do not stop after helper-level tests; inspect generated `.docx` / `.pptx` artifacts in regression tests.
- Do not assume every slide marker will arrive as clean markdown headings. In live follow-up regeneration, models may emit plain `Слайд N: ...` or decorated variants like `=== Слайд N: ... ===`; the parser must normalize both before planning.
- Do not treat internal bold subheads such as `Ключевые элементы`, `Типовые слои`, `Вывод` as new slide boundaries when the draft already has explicit slide markers.
- Do not diagnose all oversized decks as one problem. Separate at least three layers:
  1. follow-up routing/context selection;
  2. parser/section-boundary recognition;
  3. slide-density/composition tuning.
  Fixing the wrong layer creates fake progress.
- Do not let presentation-enhancement follow-ups degrade into outline spam. The follow-up prompt should explicitly require `Слайд N: Название` on its own line, forbid `=== ... ===` wrappers, and forbid converting intra-slide subsections into new slides.
- Do not duplicate the first slide in explicit-slide mode. If the draft starts with `Титульный`, the exporter should produce one system title/cover slide, not a title slide plus an overview slide plus a separate content slide named `Титульный`.

# Live follow-up hardening

When users ask to "добавить разметку", "добавить форматирование", "добавить картинки/ссылки" to an existing presentation draft, treat it as a distinct export-adjacent class:

1. Recover the last substantive presentation draft, not the latest clarification stub.
2. Build a focused follow-up prompt that says:
   - rebuild the whole deck, not only the tail;
   - preserve order and approximate slide count;
   - keep intra-slide subsections inside the current slide;
   - start each slide with a plain explicit marker: `Слайд N: Название`.
3. If real web lookup is unavailable in the runtime, require honest recommendation placeholders instead of fabricated URLs.
4. Re-verify both the regenerated text and the final PPTX export. A route fix alone is not enough.

# Verification checklist

Before declaring success:
- sanitizer removes prelude/tail lines from both DOCX and PPTX paths;
- plan builder receives cleaned content only;
- renderer no longer injects service notes/badges;
- typography matches requested defaults;
- targeted DOCX/PPTX export suite passes.

# References

- See `references/plan-based-export-checklist.md` for a concise checklist and regression targets from this session.
- See `references/live-followup-explicit-slide-pitfalls.md` for follow-up regeneration pitfalls: explicit slide markers, boundary handling, and route-vs-parser-vs-composition diagnosis.
