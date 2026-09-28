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
   - When the user requests exactly one slide, treat it as the whole deliverable: consolidate the argument into one readable composition, state `ровно 1 слайд` in the generation brief, and verify the export contains one slide.
   - When the user requests one role slide, keep all roles on that one slide and use later slides for decisions or cases, not repeated role benefits.
   - For a two-slide CEO explanation of a planning-and-actuals model, use two distinct management jobs: slide 1 shows the forward causal chain `catalog and norms → sales plan → resource demand → project economics → company P&L`; slide 2 shows the closed-period boundary and rolling chain `actual consumption → actual direct cost → EAC for open periods → recognized revenue → margin and operating profit`. Keep controls and formulas as compact annotations so the mechanism remains readable at executive distance.
   - Mark client-history figures as historical examples. Mark optimization figures as potential, not a commitment or guaranteed result.
   - In an investment-case deck, lead each application slide with the client situation, decision, and measurable client effect. Put an external case in a compact evidence note; a vendor case supports the effect mechanism and must never become the slide’s protagonist.
   - Express the client effect through measurable fields or formulas such as avoided purchases, lead-time change, released capacity, dual-run duration, RTO/RPO, and expected loss. Use literal client values only when supplied or calculated; otherwise use field names or variables rather than illustrative numbers that can be mistaken for targets.
   - When mirroring a reference case block, preserve its narrative architecture as well as its slide count. For a six-slide block shaped as `summary → detailed cases → synthesis`, do not turn every slide into another methodology step or another independent case.   - For a one-slide infrastructure-value case, lead with incremental value beyond the baseline transformation; omit scale and current-state facts unless they are required to interpret a calculation.
   - Make every value card causal: show how the mechanism forms budget impact and how it removes a Time to Market delay, then tag the resulting money, operational-efficiency, and delivery-speed outcomes with compact markers such as `₽`, `⚙`, and `⏱`.
   - Build value slides in two visual levels: first the two or three client outcomes as large, immediately readable metrics; then the enabling initiatives, each mapped to the budget category and the specific delivery scenario it affects. A slide that opens with mechanisms rather than client outcomes misses the executive job.
   - When a headline saving is decomposed into initiatives, show a quantified contribution only when it comes from client input or a cited benchmark. For the remaining initiatives, name the cost category and calculation base instead of inventing percentages so the total does not become a false allocation.
   - When presenting a duration reduction, state both the absolute and relative estimate against the same denominator. If a seven-day improvement is benchmarked to a two-week window, present it as `до 50% / до 7 дней`; never imply that the full window is the reduction.
- Model Time to Market by delivery scenario, never as a pooled infrastructure total: general standardization applies to typical resource delivery and new-team onboarding; BareMetal applies only to BareMetal issuance; HPC/GPU applies only to queueing and priority access for those scarce resources. Do not add their day estimates together because they describe overlapping or distinct request populations.
- In an infrastructure-value decomposition, make FinOps the primary budget lever and describe its direct Time to Market effect as limited to decision latency; do not use FinOps to inflate delivery-speed claims. Separate a shared automation budget effect from a more specific BareMetal operational effect to avoid double counting.

3. Run grounded research where the deck needs external methodology.
   - Prefer primary sources for TBM, FinOps, cloud architecture, and governance claims.
   - Keep externally sourced frameworks separate from client-provided examples; do not turn a client example into a universal benchmark.

4. Generate or adapt through Gamma deliberately.
   - When the user explicitly requests Gamma, make the editable Gamma document and its URL acceptance criteria; an exported `.pptx` is a verified companion artifact, not a substitute for creating the deck in Gamma.
   - Resolve an existing user-provided credential from approved secret storage or session history before declaring that access is unavailable; never expose it in text or saved artifacts.
   - Generate a `presentation` with `cardOptions.dimensions: "16x9"` whenever the user requests a wide-screen deck.
   - When the user names an existing deck as the design reference, treat the whole visual grammar as a hard requirement: inspect the actual export and preserve cover treatment, grid, card geometry, title hierarchy, density, colors, footer, numbering, and custom-generated visuals. Reusing only `themeId` is insufficient because a Gamma theme does not preserve composition.
   - Compare the title slide first. A reference cover shaped as `full-height custom visual on the left + compact title block on the right` must retain that exact composition; a full-width heading, process diagram, stock illustration, or empty image area is a different design and must block delivery.
   - If the new deck intentionally keeps the reference slide count, sequence, or layout jobs, create it with `/v1.0/generations/from-template` from the reference Gamma and map each new slide to the corresponding reference composition. Use a fresh generation with only `themeId` only when the storyline and layout genuinely diverge. Follow `references/gamma-theme-reuse.md` for the decision rule and API recipe.
   - Treat `from-template` as probabilistic rather than exact. If it changes composition or drops a custom visual, stop iterating through Gamma: duplicate the reference PPTX directly, replace text inside the existing shapes, preserve every shape's geometry/type, and generate a new subject-specific visual in the same artistic language for image slots. Verify shape counts and geometry against the reference before delivery.
   - For corrections to an approved deck, adapt the current Gamma with `/v1.0/generations/from-template`; name only the slides to change, state that all others must remain literal, and avoid a fresh storyline generation unless the user requests one.
   - Use a stable theme and an explicit visual instruction: executive B2B, diagrams and cards, no stock people unless requested. Ask for editable text, cards, lines, and arrows when information must remain legible; decorative generated images often lose labels and causal structure.
   - For a Russian deck created through the Generate API, use `textMode: "generate"` with `textOptions.language: "ru"` and repeat the Russian-only constraint in the prompt; `preserve` ignores language options and can leave generated labels in English.
   - Prefer a simple matrix or equal cards over a dense hub-and-spoke or long dual-chain diagram when every label is mandatory; Gamma may retain the visual while dropping editable labels.
   - Poll the generation to completion, download the export, and retain the editable Gamma URL plus the exported `.pptx`.
   - Keep no more than two active variants by default: current and one fallback. An explicit user request to preserve or duplicate a version overrides this cleanup rule; create the copy through `/v1.0/generations/from-template`, compare its exported text and slide count with the source, and never delete either preserved version. Before any cleanup, verify the endpoint semantics: `DELETE /v1.0/gammas/{gammaId}` reports deletion, so use it only for rejected drafts, never for the viable fallback; then confirm the current Gamma remains active through the API.

5. Verify the actual generated deck, not the prompt.
   - Inspect exported slide text and count using `python-pptx`; traverse grouped shapes as well as top-level text frames when checking literal labels.
   - Record word count and minimum font size per slide. For this user, keep ordinary body text at 14 pt or larger where practical; reserve 9–11 pt for sources and explicit footnotes. Split or simplify a slide when Gamma compresses core content below 12 pt.
   - Verify the slide ratio is 16:9, slide count matches the intended narrative, required headings survived, and no duplicate stakeholder slide remains.
   - Compare extracted text for every untouched slide against the prior export after a targeted adaptation; Gamma can silently rewrite a phrase on an unnamed slide. Treat any collateral semantic change as a failed targeted edit: revert it or keep the prior viable version, and archive the prior version only when the named slides changed and all other slides stayed intact.
   - Inspect the actual visual assets or rendered slide for every named visual correction. Text presence does not prove that arrows, labels, spacing, or reading order survived export. Treat a Gamma thumbnail showing a loading placeholder as unverified and inspect the editable page or a rendered PPTX instead.
   - When the deck must be Russian, check extracted export text for unintended English headings and captions; regenerate with an explicit Russian-only instruction if any appear.
   - Search the export for every mandatory numeric label and its qualifier. Gamma can create a metric card while omitting the number itself; require figures such as `ДО 15%` as ordinary editable text and verify the literal strings in the PPTX text layer.
   - Search for mandatory facts, role wording, commercial boundaries, case labels, and the continuous management cycle. Regenerate with stronger title-level constraints if Gamma compresses or omits a mandatory point.
   - For a continuous-management slide, make the cycle itself the headline when it is mandatory. For operating management use `Планировать → Рассчитывать → Решать → Корректировать`; for a strategy offer use `Стратегия → Реализация дорожной карты → Сопровождение и контроль достижения → Пересмотр стратегии`, and state that value depends on both adaptability and execution support.

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
