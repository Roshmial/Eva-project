# Reusing an exact Gamma design system

Use this recipe when an existing Gamma deck is the required visual reference.

1. Identify the reference file ID or document slug and retrieve metadata:
   `GET https://public-api.gamma.app/v1.0/gammas/{gammaId-or-slug}` with `X-API-KEY`.
2. Export and inspect the reference PPTX. Record cover treatment, background, accent colors, card grid, title hierarchy, information density, footer, numbering, and the visual job of each slide. `themeId` preserves colors and fonts only; it does not preserve composition.
3. Choose the adaptation path from structure, not from wording:
   - If the new deck keeps the reference slide count, sequence, or layout jobs, call `POST /v1.0/generations/from-template` with the reference `gammaId`. Map every new slide to its reference composition and explicitly require the design system to remain literal.
   - If the storyline and layouts genuinely diverge, call `POST /v1.0/generations` with the reference `themeId`, `format: "presentation"`, and `cardOptions.dimensions: "16x9"`; reproduce the composition rules explicitly.
   - If the reference is archived and cannot be used by `from-template`, reuse its `themeId` and specify the recorded layout grammar in the generation brief.
4. For a full from-template adaptation, state the exact target slide count, provide numbered content for every slide, and map each slide to a reference layout. Require editable text/shapes, no stock imagery unless present in the reference, and no invented figures.
5. When Gamma drops a dense synthesis slide, adapt only that slide from the generated deck. Replace matrices that lose labels with four equal cards plus a bottom rule bar; verify every mandatory literal in the exported PPTX.
6. Verify the actual result:
   - exact slide count and 16:9 ratio;
   - extracted text and mandatory labels;
   - unchanged slides after targeted edits;
   - minimum font sizes and out-of-bounds text in the PDF/PPTX;
   - visual continuity with the reference, not merely matching `themeId`.
