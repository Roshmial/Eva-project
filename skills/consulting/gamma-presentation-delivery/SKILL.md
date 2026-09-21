---
name: gamma-presentation-delivery
description: "Use when creating client slides in Gamma. Build and verify."
version: 1.0.0
metadata:
  hermes:
    tags: [gamma, presentation, consulting, tbm, rsm]
---

# Gamma Presentation Delivery

## Procedure

1. Establish the sales logic before generating slides.
   - Extract the literal requested sequence, stakeholders, cases, evidence requirements, and commercial boundaries.
   - Treat the user’s stated slide order as a hard constraint. Validate the outline slide by slide before generation.
   - For RSM/TBM offers, position the resource-service model and its financial model as one management contour: RSM describes dependencies and consumption; the financial model evaluates the cost and consequences of scenarios.

2. Build a concise card-by-card brief.
   - Use one slide per distinct job in the narrative; remove semantic duplicates before sending the prompt to Gamma.
   - For stakeholder-value slides, make each card operational: `Что` (the management result) and `За счёт чего` (the model capability that makes it possible).
   - When the user requests one role slide, keep all roles on that one slide and use later slides for decisions or cases, not repeated role benefits.
   - Mark client-history figures as historical examples. Mark optimization figures as potential, not a commitment or guaranteed result.

3. Run grounded research where the deck needs external methodology.
   - Prefer primary sources for TBM, FinOps, cloud architecture, and governance claims.
   - Keep externally sourced frameworks separate from client-provided examples; do not turn a client example into a universal benchmark.

4. Generate or adapt through Gamma deliberately.
   - Resolve an existing user-provided credential from approved secret storage or session history before declaring that access is unavailable; never expose it in text or saved artifacts.
   - Generate a `presentation` with `cardOptions.dimensions: "16x9"` whenever the user requests a wide-screen deck.
   - When the user names an existing deck as the design reference, treat its visual system as a hard requirement: inspect the actual export and reuse its Gamma theme instead of approximating the style in prose. Follow `references/gamma-theme-reuse.md` for the verified API path.
   - For corrections to an approved deck, adapt the current Gamma with `/v1.0/generations/from-template`; name only the slides to change, state that all others must remain literal, and avoid a fresh storyline generation unless the user requests one.
   - Use a stable theme and an explicit visual instruction: executive B2B, diagrams and cards, no stock people unless requested. Ask for editable text, cards, lines, and arrows when information must remain legible; decorative generated images often lose labels and causal structure.
   - Prefer a simple matrix or equal cards over a dense hub-and-spoke or long dual-chain diagram when every label is mandatory; Gamma may retain the visual while dropping editable labels.
   - Poll the generation to completion, download the export, and retain the editable Gamma URL plus the exported `.pptx`.
   - Keep no more than two active variants: current and one fallback. After the new export passes verification, archive intermediate adaptations and older Gamma documents, then confirm archive state through the API.

5. Verify the actual generated deck, not the prompt.
   - Inspect exported slide text and count using `python-pptx`; traverse grouped shapes as well as top-level text frames when checking literal labels.
   - Record word count and minimum font size per slide. For this user, keep ordinary body text at 14 pt or larger where practical; reserve 9–11 pt for sources and explicit footnotes. Split or simplify a slide when Gamma compresses core content below 12 pt.
   - Verify the slide ratio is 16:9, slide count matches the intended narrative, required headings survived, and no duplicate stakeholder slide remains.
   - Compare extracted text for every untouched slide against the prior export after a targeted adaptation; archive the prior version only when the named slides changed and all other slides stayed intact.
   - Inspect the actual visual assets or rendered slide for every named visual correction. Text presence does not prove that arrows, labels, spacing, or reading order survived export.
   - When the deck must be Russian, check extracted export text for unintended English headings and captions; regenerate with an explicit Russian-only instruction if any appear.
   - Search the export for every mandatory numeric label and its qualifier. Gamma can create a metric card while omitting the number itself; require figures such as `ДО 15%` as ordinary editable text and verify the literal strings in the PPTX text layer.
   - Search for mandatory facts, role wording, commercial boundaries, case labels, and the continuous management cycle. Regenerate with stronger title-level constraints if Gamma compresses or omits a mandatory point.
   - For a continuous-management slide, make the cycle itself the headline when it is mandatory: `Планировать → Рассчитывать → Решать → Корректировать`.

## RSM/TBM Pitch Pattern

Use this default sequence when the user asks to sell RSM and a TBM-based financial model for hybrid infrastructure:

1. The decision gap: dispersed financial, technical, and demand data.
2. One stakeholder slide: CIO, CFO, infrastructure leader, business — each as `Что / За счёт чего`.
3. The unified RSM + financial-model mechanism.
4. The management decisions the contour makes actionable.
5. Two to four end-to-end cases: requirement → service/SLA → resources → costs → decision.
6. Continuous management cycle.
7. Expansion from hybrid infrastructure to all IT.
8. Typical work, business outputs, two-sided team, and commercial/start format.

## Pitfalls

- Do not generate an outline that sells RSM and the financial model as adjacent deliverables; this obscures the causal chain that the customer is buying.
- Do not replace a requested stakeholder-value slide with a list of stakeholder questions; show the concrete management action and the enabling mechanism.
- Do not repeat the stakeholder slide in different wording; the second occurrence consumes attention that should prove decisions and cases.
- Do not trust Gamma to preserve a required concept merely because it appears in the input; its generation can condense content, so assert critical wording through explicit headings and inspect the exported file.
- Do not report a Gamma deck as wide-screen from the generation intent alone; verify the exported `.pptx` ratio.
- Do not accumulate generation experiments as active deliverables; archive superseded variants only after the replacement is verified, otherwise the client cannot identify the current deck.
- Do not present potential savings, selected-scope results, or historical client outcomes as guaranteed results for a new client.
