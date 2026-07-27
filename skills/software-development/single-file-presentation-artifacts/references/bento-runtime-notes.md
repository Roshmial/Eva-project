# Bento runtime notes

## Good baseline pattern
- Use the official `Bento_Slides.bento.html` shell.
- Replace only the `#bento-doc` JSON block.
- Keep the compressed runtime blocks untouched.
- Escape `<` in JSON as `\u003c`.

## Safe first demo
A safer first demo deck is intentionally plain:
- `transition: "none"` on all slides;
- plain text elements per bullet row instead of one large HTML block;
- `system-ui, sans-serif` instead of assuming a custom font is available;
- obvious dark background / light text contrast.

## What went wrong in this session
The first microservice version produced a valid `.bento.html` file and valid embedded JSON, but the user reported a white sheet / empty-looking deck on open. The robust correction path was:
1. stop assuming file generation equals visual correctness;
2. simplify the generated deck structure;
3. remove morph transitions for the smoke deck;
4. rebuild and re-verify the output file.

## Verification ladder
1. `GET /health` returns ok.
2. `POST /render` returns a file path.
3. Parse the generated file and confirm:
   - `format = bento/slides`
   - expected slide count
   - expected transitions
   - expected font family choices
4. Deliver the file and mention that Bento runtime requires a modern browser.

## Browser/runtime caveat
Bento shell uses `DecompressionStream` for its embedded runtime payload. Older browsers may fail to start the deck even when the file itself is correct. Mention this explicitly during handoff.