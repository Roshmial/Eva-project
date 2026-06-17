# iPhone minimal adaptation pattern for Hermes-style local-first UI

Context:
- The product was functionally working.
- The user explicitly said the issue was not breakage but non-adapted screen forms on iPhone.
- Scope was limited to chats, profile, and dashboards.
- Mobile admin was explicitly out of scope.

## Practical implementation pattern

### Layout
- At ~1080px and below, collapse the app shell from side-by-side layout into vertical stacking.
- Move the sidebar from a fixed left rail into a top mobile block.
- Let the main panel consume full width.

### Navigation
- Keep only essential screens visible in mobile nav.
- Hide the admin entry when the user says mobile admin is not needed.
- Use compact, touch-safe buttons.

### Chats
- Convert the recent thread list from a tall vertical desktop column into a horizontal scroller.
- Keep the active message lane full width.
- Stack the composer/support card below the message lane.
- Reduce sticky UI elements that consume the iPhone viewport.

### Profile
- Collapse all two-column grids to one column.
- Stack tabs and file actions vertically when horizontal compression hurts readability.

### Dashboards
- Collapse summary grids and matrix sections to one column.
- Reduce pie/donut chart size for narrow screens.
- Stack section headers vertically.
- Prioritize readability of visual blocks over preserving desktop density.

### Modals
- Prefer near-full-width mobile sheets/cards with capped viewport height and internal scrolling.

## Verification pattern when browser automation is partially blocked

If full screenshot verification is blocked by environment setup, still verify:
1. frontend build succeeds;
2. frontend runtime restarts cleanly;
3. served HTML/CSS/JS contains the mobile breakpoint rules and selectors you added.

Example signals to verify in delivered source:
- presence of a dedicated mobile breakpoint such as `@media (max-width: 820px)`;
- mobile-specific app shell rules like `flex-direction: column` or `min-height: 100dvh`;
- mobile chart resizing rules;
- selectors that hide or simplify non-essential mobile nav entries.

## Communication lesson

When the user says "nothing is broken, it's just inconvenient on iPhone", frame the work as:
- layout adaptation,
- mobile-safe UX hardening,
not as a bugfix pass.
