# Frontend state visual reconstruction

Use this pattern when the user asks to "show the current screen" of a local web MVP, but a true browser screenshot is blocked by browser-runtime issues or other environment friction.

## Goal
Deliver a visually useful artifact now, without pretending it is a live screenshot.

## Reliable fallback
1. Read the current frontend source of truth:
   - `index.html`
   - inline CSS / component structure
   - `app.js` for visible states and labels
   - `config.js` only if it changes UI-visible labels or routing
2. Reconstruct the screen from code:
   - login screen;
   - main app shell;
   - sidebar / thread list;
   - top bar / status;
   - right-side diagnostic cards;
   - composer and representative messages.
3. Generate an image mockup locally.
4. Send it to the user with an explicit label such as:
   - "это реконструкция по текущему HTML/CSS";
   - "не живой browser-screenshot".

## Why this is still valuable
- lets the user assess layout and information architecture immediately;
- avoids blocking on local browser plumbing;
- is grounded in the current frontend files rather than imagination.

## Important honesty rule
Never present the reconstruction as a real screenshot if the page was not actually rendered and captured live.

## Good user-facing framing
- first sentence: say whether it is live or reconstructed;
- second sentence: state the basis (current frontend code / HTML/CSS);
- then send the image.

## When to prefer this fallback
- the user wants a quick visual check;
- the MVP is local and source-visible;
- browser capture is failing for environment reasons;
- exact pixel fidelity is less important than showing the current structure.

## When NOT to rely on it alone
- the user is validating a visual bug;
- the user needs proof of actual rendering;
- dynamic state, responsive behavior, or runtime data matters.
In those cases, fix the live capture path and return a true screenshot later.
