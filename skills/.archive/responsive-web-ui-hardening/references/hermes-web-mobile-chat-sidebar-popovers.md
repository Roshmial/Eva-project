# Hermes Web mobile chat/sidebar/popover hardening notes

Use this reference when a local-first Hermes-style React UI is functionally live but still feels like a squeezed desktop layout on iPhone portrait.

## Symptoms seen in production
- Chat title is long and action buttons (`Переименовать`, `В архив`) overlap the title.
- Settings popover (`Параметры`) opens partially, appears too narrow/wrongly anchored, or visually shrinks the whole page.
- Message lane wastes vertical space; bubbles and typography feel too large for the viewport.
- Mobile nav hides `Админ` with stale CSS even though the user expects it, while `Выйти` floats separately.

## Durable fixes

### 1. Long title + actions
Preferred mobile pattern:
- title row contains only the title;
- actions move to a second row;
- title gets `overflow-wrap: anywhere`, `word-break: break-word`, tighter `line-height`.

Reason:
Trying to preserve the desktop single-line title/actions layout on narrow screens causes overlap and unreadability.

### 2. Parameters/settings popover on iPhone
If a settings popover contains `select` fields and mobile Safari starts zooming/shrinking the page:
- stop reusing the desktop popover;
- render the settings surface as a fixed mobile sheet;
- use bounded height like `max-height: 72dvh` and internal scroll;
- keep left/right margins instead of hard full-bleed if the surface should still feel like a card.

Recommended mobile traits:
- `position: fixed`
- `left/right` margins instead of desktop anchoring
- `bottom: max(..., env(safe-area-inset-bottom))`
- high `z-index`
- `select/input/textarea { font-size: 16px; }`

### 3. Message density
For mobile chat readability, often the right fix is not only smaller text but also less chrome:
- reduce message bubble padding;
- reduce message lane padding and gaps;
- tighten markdown block spacing;
- reduce heading sizes one step on mobile.

### 4. Mobile nav expectations
Do not keep an old `.nav-btn-admin { display: none; }` rule if the user explicitly expects admin on mobile.
Instead:
- create a compact toolbar row that contains nav buttons and logout together;
- hide non-essential counters like `Всего чатов` before hiding actual navigation.

## Verification pattern
- Build the React frontend.
- Restart the exact prod frontend service.
- Confirm the served HTML references the new assets.
- If true device verification is unavailable, be explicit that runtime/bundle verification succeeded but iPhone visual acceptance still needs a hard refresh on device.
