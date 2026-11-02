---
name: gamma-targeted-edits
description: "Use when editing a Gamma deck. Make targeted edits only."
---

# Gamma targeted deck edits

## Procedure

1. Treat the approved Gamma as the canonical artifact and keep one verified export as rollback.
   - Identify the exact `gammaId`, URL, slide numbers and acceptance criteria before editing.
   - Change only named slides or elements. Do not regenerate the storyline for a local correction.
   - If the correction changes slide count or inserts a cover, do not use the edit endpoint: it cannot add pages. Regenerate from the approved source or reference template, then use targeted edits only after the new baseline passes structural QA.
   - If the user rejects the entire visual language rather than one layout, stop stacking local edits on the rejected deck. Rebuild once with a conflict-free art direction, preserve approved content, then target only the residual blockers.
   - Keep no more than two active variants: current and one verified fallback.

2. Edit through the Gamma agent or editor with a literal slide contract.
   - For the API, use `POST /v1.0/agent/gammas/{gammaId}/edits`, poll `/v1.0/agent/edits/{editId}`, then export both PPTX and PDF.
   - State which slides may change, that every other slide must remain unchanged, the exact visible copy, required labels, minimum readable size and prohibited layouts. For Misha's premium executive decks, use at least 16 pt for ordinary body text, 14 pt for analytical tables and stage labels, and 10–11 pt only for sources and explicit footnotes.
   - Group related corrections into small batches of roughly two to four slides when Gamma repeatedly only partially follows a whole-deck request; this keeps the visual contract specific while avoiding one edit per element.
   - Prefer large native cards, tables and simple chains. When a miniature diagram behaves like a slide embedded inside a slide, replace it rather than merely enlarging it.
   - Preserve or add a large full image only when it is part of the approved visual language; never substitute icon rows for a request for cinematic/editorial imagery. Keep the image at roughly 35–55% of the slide and verify it is not reduced to a corner decoration.
   - When Misha asks for less abstract and more lively AI imagery, replace object-only CGI metaphors with recognizable enterprise scenes: an AI product team at work, GPU/data-center operations, MLOps observability, model inference in production, or an executive investment decision. Keep the scene editorial and businesslike; prohibit robots, glowing brains, generic neon networks, staged handshakes and tiny decorative icons.
   - Audit copy and visual composition together before editing when the feedback covers both design and text. For each slide, decide `keep` or `rework`, state the slide's decision job, then change only the slides whose image, hierarchy or wording does not perform that job.
   - Mark historical and illustrative metrics visibly; never present them as guaranteed results.

3. Treat the agent summary as a diagnostic, not proof.
   - The summary can report success while omitting text, changing a horizontal chain to a grid, shrinking a key formula or warning about a layout that is actually acceptable.
   - Always inspect the exported artifact before deciding whether another edit is needed.

4. Run text and structural QA after every edit.
   - Verify slide count, 16:9 ratio, mandatory literals, absence of service instructions/placeholders and page bounds.
   - Compare extracted text of every unnamed slide against the prior verified export. Any collateral semantic change fails the targeted edit even if the named slides improved.
   - Use `gamma-presentation-delivery/scripts/qa_gamma_export.py` for the repeatable export gate.

5. Run visual QA in two resolutions.
   - Export PDF, render individual pages and a contact sheet with `gamma-presentation-delivery/scripts/render_pdf_montage.py`.
   - Use the montage only to find suspicious slides; it can make readable text look too small. Recheck every suspected blocker on the full-resolution slide before editing again.
   - Inspect all changed slides individually for reading order, broken words, formula legibility, clipping, contrast and projector-distance readability.

6. Close only on the exact final export.
   - Re-export PPTX and PDF after the last correction; never deliver an earlier preview with a later QA report.
   - Verify the final Gamma URL still resolves and read back metadata after the state-changing edit.
   - Deliver the editable Gamma URL, PPTX, PDF and a concise QA summary. Archive the fallback only after the final version passes.

## Pitfalls

- Do not trust requested composition alone: Gamma may turn a linear chain into a 2×2 grid while preserving text; judge the actual render against the slide's decision job.
- Do not use a contact sheet as the sole legibility test: thumbnails systematically exaggerate small-text problems.
- Do not leave a broken word because the extracted text is complete: line-break defects are visible only in the render.
- Do not accept a calculation slide when totals survive but the bridge, group labels, driver shares or unit definition disappear; the resulting number looks pseudo-precise.
- If the user reports a missing cover or slide that exists in a local render, stop defending the local artifact. Re-export the live `gammaId`, inspect the exact first slide in that export, and correct or relink the live document before claiming completion.
