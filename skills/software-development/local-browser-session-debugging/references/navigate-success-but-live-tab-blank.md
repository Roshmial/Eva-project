# Navigate success payload vs live blank tab

Use this reference when Hermes browser tools appear to navigate successfully, but the actual live tab never leaves `about:blank`.

## Reproduction cues

Typical symptom cluster:

- `browser_navigate("https://example.com")` returns `success=true`, target URL, and a plausible title.
- `browser_snapshot()` returns `(empty page)`.
- `browser_console(expression='({url: location.href, title: document.title, readyState: document.readyState, bodyText: document.body?.innerText || ""})')` reports:
  - `url: "about:blank"`
  - empty title/body text
  - `readyState: "complete"`
- `browser_vision` shows a plain white frame.
- `browser_get_images()` returns zero images.

This combination means the wrapper-level navigate payload is not trustworthy by itself. The live DOM/context stayed on a blank tab.

## Extra confirmation path

If local Chromium/CDP is in use, confirm whether the browser itself still exposes only an `about:blank` page:

- inspect `http://127.0.0.1:<port>/json/version`
- inspect `http://127.0.0.1:<port>/json/list`

If `/json/list` shows only `about:blank`, that is strong evidence that no real page navigation stuck in the underlying browser session.

## Practical rule

For this failure class, rank evidence in this order:

1. live `browser_console` page state;
2. `browser_snapshot` / DOM sample;
3. visual blank-frame confirmation;
4. CDP `/json/list` target list;
5. only then the original `browser_navigate` return payload.

Do not declare navigation successful from the navigate payload alone.
