# Browser empty page vs jsdom mount discriminator

Use this reference when a live web UI shows an empty page in browser tooling, but HTTP/static checks say the frontend is serving normally.

## What this pattern proves

It distinguishes two different failure classes:

1. Real frontend boot failure
- served bundle throws or never mounts;
- `#root` stays empty even when the served JS is executed in an isolated DOM runtime.

2. Browser-wrapper / visual-layer failure
- served bundle exists and mounts real DOM into `#root`;
- but browser tooling still reports a white screen or `(empty page)`.

That second case means: do not claim the UX is healthy, but also do not misdiagnose it as "React never rendered" without stronger evidence.

## Minimal workflow

1. Fetch live `index.html` from the target origin.
2. Fetch the referenced JS/CSS assets directly.
3. Confirm the mount path exists in the JS.
   - Look for `createRoot(`, `document.getElementById("root")`, and a known first-screen string.
4. Run the served JS inside `jsdom`.
   - Add only minimal shims: `fetch`, `matchMedia`, `ResizeObserver`, `IntersectionObserver`, `requestAnimationFrame`, `scrollTo`.
5. Inspect:
   - `document.body.textContent`
   - `document.getElementById('root')?.innerHTML`
6. Classify the result.

## Interpretation table

- HTTP good + `jsdom` mount good + browser screenshot white
  - likely browser-wrapper artifact, viewport/layout issue, or client-specific runtime behavior
  - not proof of mount failure

- HTTP good + `jsdom` mount empty/throws
  - real frontend bundle/runtime defect is likely

- HTTP bad or asset fetch bad
  - deployment/proxy/static serving issue first

## Reporting rule

State separately:
- what is proven about asset serving;
- what is proven about bundle execution;
- what is still unproven about real visual acceptance.

A good sentence shape is:
- "The live bundle executes and mounts the login DOM in `jsdom`, so a zero-render startup failure is not confirmed. The remaining symptom is a real white-screen observation in browser tooling, which points to a visual/browser-runtime layer rather than a missing React mount."
