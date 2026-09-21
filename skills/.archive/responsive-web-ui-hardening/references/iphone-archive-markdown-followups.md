# iPhone composer zoom + archive semantics + markdown depth follow-ups

Use this note when a Hermes-style local-first chat UI is already mobile-adapted but still has three stubborn defects:

1. iPhone Safari auto-zooms when the user starts typing.
2. `В архив` exists technically but archived chats still remain on the main page.
3. Markdown headings deeper than `###` are visually or functionally unsupported.

## Practical fixes

### 1) iPhone composer auto-zoom
Use a two-layer fix:
- CSS guard on the actual composer textarea/input path:
  - `font-size: 16px`
  - `-webkit-appearance: none`
  - `transform: translateZ(0)`
- Root text sizing guard:
  - `html { -webkit-text-size-adjust: 100%; text-size-adjust: 100%; }`
- If Safari still zooms, add an iPhone-only runtime hook:
  - detect `/iPhone/i` in `navigator.userAgent`
  - on `focusin` for text inputs / textarea, temporarily set viewport content to `width=device-width, initial-scale=1.0, maximum-scale=1.0, viewport-fit=cover`
  - on `focusout`, restore the original viewport meta content

Verification standard:
- build succeeds
- delivered CSS contains the anti-zoom guard
- delivered JS contains the focus hook / `maximum-scale=1.0`
- final device-level confirmation still requires a real iPhone check

### 2) Archive semantics in chat UI
Do not assume `archived=true` automatically produces the expected UX.

If the agreed meaning is:
- archived chat disappears from the main page
- archived chat remains reachable in `Все чаты`

then implement both:
- main sidebar/recent thread list filters to `!thread.archived`
- if the currently open chat is archived, switch the active context to the next non-archived thread (or to no active chat / new chat flow if none remain)

### 3) Markdown headings deeper than H3
A common half-fix is adding CSS for `h4`/`h5`/`h6` while leaving the parser regex limited to `#{1,3}`.

Complete fix requires both:
- parser regex accepts `#{1,6}`
- paragraph boundary logic also treats `#{1,6}` as a heading boundary
- styles exist for `.message-md-heading-4`, `.message-md-heading-5`, `.message-md-heading-6`

## Pitfall
Do not mark markdown support as done after styling alone. If parsing still uses `#{1,3}`, `####` and deeper headings will silently render as plain paragraphs.