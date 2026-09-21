---
name: responsive-web-ui-hardening
description: Minimal-but-real mobile adaptation for local-first web UIs, with emphasis on iPhone portrait usability for chat, profile, and dashboard surfaces.
---

# Purpose

Use this skill when a web UI is functionally working but feels like a compressed desktop layout on mobile. The goal is not a full redesign. The goal is a pragmatic, testable mobile-safe layout that preserves core user flows.

This skill is especially relevant for local-first Hermes-style apps where the fastest win is layout hardening, not new infrastructure.

# When to use

Trigger this skill when the user says things like:
- "ничего не сломано, просто на iPhone неудобно"
- "это сжатый desktop"
- "нужна минимальная mobile-адаптация"
- "сделай под ключ iPhone-версию для основных экранов"

Typical scope:
- chat surfaces
- profile/account surfaces
- dashboard/result cards
- modal readability on narrow screens

Do not start with a full mobile redesign unless the user explicitly asks for it.

# Outcome standard

A good result means:
- the key path is usable in iPhone portrait;
- the main content gets the width, not the navigation chrome;
- visual artifacts remain readable without zooming;
- desktop behavior is not accidentally broken.

# Working approach

## 1. Confirm the target scope first

For a minimal pass, explicitly identify which screens matter now.

Default priority order:
1. login / auth if broken
2. chat list + active chat
3. profile
4. dashboards / result cards
5. admin only if the user asks for it

If admin is out of scope, do not spend the mobile budget there.

## 2. Diagnose the layout class, not just the screenshot

Name the problem precisely. Usually one of these:
- compressed multi-column desktop layout shown on phone
- persistent sidebar stealing width from primary content
- sticky headers / browser chrome consuming too much viewport
- charts/cards sized for desktop proportions
- action rows remaining horizontal when they should stack

This framing prevents wasted time on cosmetic tweaks.

## 3. Apply the minimum viable mobile transformation

### A. App shell
- Collapse left sidebar into a top block on mobile.
- Give main content full width.
- Prefer `flex-direction: column` or single-column grid below a mobile breakpoint.
- Keep spacing tighter but not cramped.

### B. Navigation
- Keep only essential sections visible on mobile.
- If admin is not needed on mobile, hide the admin entry rather than squeezing it in.
- But if the user explicitly expects admin/navigation controls on mobile, do not keep an old CSS rule that hides them at the breakpoint. Rebuild the toolbar so admin and logout live in the same compact row instead of silently dropping admin.
- Use compact nav buttons with touch-safe height.
- If a section is unavailable for the current role, do not rely on CSS-only hiding at narrow breakpoints. Filter navigation by permissions in render logic so the user never sees inaccessible sections first and only then loses access on click.

### C. Chat surfaces
- Never keep sidebar, thread list, and active chat competing horizontally on iPhone.
- Convert thread previews into a top strip or horizontal scroller if needed.
- Make the message lane full width.
- Stack composer/support panels below the message lane.
- Reduce sticky behaviors that consume scarce vertical space.
- If mobile still shows a huge legacy composer/settings slab even though compact mobile CSS exists, check rendered JSX/DOM structure before tweaking media queries again. A common cause is markup drift: styles already support compact `textarea + files + parameters`, but the screen still renders an older long form with steps, policy block, and file lists inline.
- Keep thread-title actions attached to the title row on mobile. If actions like rename/archive fall onto a separate full-width row under the title, the screen starts to feel like compressed desktop chrome instead of a phone-first chat header.
- If the title is long and actions overlap or compete for width, prefer a deliberate two-row mobile layout: title first with safe wrapping, actions second with wrap/gap. Do not force title and actions into one row when it causes overlap.
- Composer tool popovers on mobile should not be fixed overlays that cover the very buttons used to reopen or dismiss them. Prefer popovers anchored above their own buttons inside the composer container, with bounded height and internal scroll when needed.
- When two sibling composer tools solve the same class of interaction (`Файлы` / `Параметры`, attachment/source pickers, etc.), keep them on the same interaction pattern and visual density unless the user explicitly asks for asymmetry. Do not leave one as a compact anchored popover and convert the other into a bottom sheet or oversized desktop-style panel — users read that as inconsistent UX immediately.
- Parameter/settings popovers are a special case on iPhone: first compare them against the already accepted sibling popover before inventing a different mobile pattern. If `Файлы` works and `Параметры` does not, align `Параметры` to the `Файлы` pattern (same anchoring, width class, spacing, section density) before escalating to a separate sheet design. Keep `select`, `input`, and `textarea` at `font-size: 16px` to avoid iPhone Safari auto-zoom that looks like broken page scaling.
- If iPhone Safari still auto-zooms the composer after the 16px fix, add a second guard instead of declaring the CSS sufficient: `-webkit-text-size-adjust: 100%`, `text-size-adjust: 100%`, `-webkit-appearance: none`, and a minimal iPhone-only focus hook that temporarily tightens the `viewport` meta (`maximum-scale=1.0`) on `focusin` for text inputs / textarea and restores it on `focusout`. Verify the delivered bundle contains both the CSS guard and the runtime hook.
- For chat archive UX, do not stop at toggling an `archived` flag. Confirm the product meaning of archive in the actual UI: if archive means "hidden from the main page, visible only in `Все чаты`", then the sidebar/recent-chat strip must filter `!archived`, and archiving the currently open chat should move the user back to the next active chat instead of leaving an archived thread hanging in the primary flow.
- Warning banners about model/data policy should stay visible but compact on mobile: reduce padding, font size, and line-height before considering more structural changes.
- If the user reports that iPhone still looks like a compressed desktop after inner-component fixes, stop tweaking popovers/buttons and inspect the root shell first. A common hidden cause is the app shell still running as a two-column desktop contour (`app-layout` + fixed-width `sidebar` + `main-panel`). On phone breakpoints, explicitly force the shell into a single column and full-width children: `flex-direction: column`, `width/max-width: 100%`, `min-width: 0` on sidebar/main panel, and `overflow-x: hidden` on `html/body/app shell` so the right column cannot remain clipped off-screen.
- For iPad-class devices (for example 11-inch tablets), do not rely only on the phone breakpoint. Add and verify an intermediate tablet breakpoint so the app does not jump straight from desktop density to narrow-phone cleanup.

### D. Profile surfaces
- Collapse two-column profile forms and summary grids into one column.
- Stack tabs/filters/actions vertically when horizontal rows become cramped.
- Make file actions full width when necessary.

### E. Dashboards
- Prefer visual-first but mobile-readable sections.
- Collapse summary grids and matrix layouts to one column.
- Resize pie/donut charts for narrow screens.
- Stack section headers and action controls vertically.
- Keep charts readable before preserving desktop density.

### F. Modals
- On mobile, prefer bottom-sheet-like presentation or at least full-width constrained cards.
- Reduce padding and border radius modestly.
- Ensure tall modals stay scrollable within viewport height.

## 4. Treat mobile browser chrome as part of the layout

On iPhone Safari, the browser UI steals space.

Practical rules:
- avoid overusing sticky banners and sticky headers;
- test with realistic vertical height constraints;
- prefer `100dvh`-aware layout behavior where helpful;
- do not assume the visible viewport matches desktop expectations.

## 5. Verify in layers

Verification should include:
1. code/build verification;
2. runtime availability after restart/deploy;
3. if possible, viewport-level verification on an iPhone-like size.

If screenshot-level verification is blocked by environment issues, still verify:
- the responsive CSS is shipped in the live frontend;
- the runtime serves the updated assets;
- the breakpoint rules and mobile selectors are present in delivered source.

Be explicit that this is partial verification, not fake visual proof.

# Heuristics for minimal iPhone adaptation

Use these defaults unless the product needs something else:
- mobile breakpoint around `820px` for portrait cleanup;
- desktop/tablet collapse around `1080px` for broader stacking;
- horizontal thread scroller is acceptable for "recent chats" in a minimal pass;
- hide non-essential admin entry on mobile if the user says admin is not needed;
- reduce chart size rather than forcing desktop proportions.

# Pitfalls

- Do not call it a "bug fix" if the real issue is non-adapted layout.
- Do not spend the iteration on admin screens if the user explicitly deprioritized mobile admin.
- Do not keep text-heavy sections dominant when the user asked for dashboards and readability.
- Do not claim mobile verification from memory; verify build/runtime and clearly label any remaining visual gap.
- Do not preserve desktop multi-column purity at the cost of phone usability.

# Deliverable checklist

Before finishing, confirm:
- build succeeds;
- runtime is restarted or refreshed if needed;
- chat, profile, and dashboard surfaces have mobile-specific layout rules;
- admin mobile scope matches the user's instruction;
- the user gets a short, honest summary of what was changed and what remains unverified.

# References

- `references/iphone-minimal-adaptation.md` — concrete implementation pattern from a Hermes Web MVP pass: sidebar-to-top layout, horizontal recent chats, stacked composer, single-column profile/dashboard sections, and mobile chart resizing.
- `references/admin-mobile-hiding.md` — the deliberate pattern where the admin navigation entry is hidden on mobile (≤820px) via `.nav-btn-admin { display: none }` while remaining fully functional on desktop for admin users.
- `references/hermes-web-mobile-chat-sidebar-popovers.md` — concrete production notes for mobile chat title/action overlap, iPhone popover-to-sheet conversion for settings panels, 16px form controls to avoid Safari auto-zoom, and compact nav+logout layout.
- `references/iphone-archive-markdown-followups.md` — follow-up note for stubborn iPhone composer zoom, true archive semantics (`hidden from main page, visible in Все чаты`), and the parser+style dual fix for `####`…`######` markdown headings.
