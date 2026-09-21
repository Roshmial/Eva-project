# Reusing an exact Gamma design theme

Use this recipe when an existing Gamma deck is the required visual reference but the new deck needs a different storyline.

1. Identify the reference file ID or document slug and retrieve metadata:
   `GET https://public-api.gamma.app/v1.0/gammas/{gammaId-or-slug}` with `X-API-KEY`.
2. Read `themeId` from the response. Inspect the reference PPTX as well: cover treatment, background pattern, accent colors, card grid, title hierarchy, and information density are part of the requirement; the theme alone does not guarantee matching composition.
3. Create the new deck with `POST /v1.0/generations`, passing that exact `themeId`, `format: "presentation"`, and `cardOptions.dimensions: "16x9"`. Use a concise card-by-card brief and explicit composition rules.
4. Do not use `from-template` merely to borrow a look when the storyline changes completely. Use it for targeted adaptations of an active deck.
5. An archived reference cannot be used by `from-template`, but its metadata can still expose a reusable `themeId`; create a fresh generation with the theme instead of abandoning the design reference.
6. Verify the result from the exported PPTX: theme continuity, editable text, mandatory labels, word count, font sizes, and the expected slide count. If a complex diagram drops text, replace it with a grid or cards and regenerate only that slide.
