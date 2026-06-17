# Hermes Web preview lane for CopilotKit

Use this as a concrete pattern when introducing CopilotKit into an already-working local-first Hermes-style React contour.

## Safe rollout pattern

1. Start from the currently working UI contour, not from an older branch or stale copy.
2. Clone it into a sibling directory with a dedicated experimental port.
3. Parameterize the frontend port in both Vite config and launcher script.
4. Mount `CopilotKitProvider` and a lightweight `CopilotPopup` at the React root.
5. Set `runtimeUrl` to `/api/copilotkit` even before the real runtime exists.
6. If needed, add a backend placeholder route that returns an explicit preview-only response.
7. Verify in a real browser that the popup is visible before doing deeper wiring.

## What successful UI-only integration looks like

- The app shell still loads.
- Copilot popup/sidebar is visible.
- The browser title and main page are intact.
- Runtime warnings may still appear.

This means the UI layer is integrated, but not that CopilotKit is fully operational.

## Signals that runtime is still missing

Common browser-console symptoms:
- `/api/copilotkit/info` returns 404 or another non-success status.
- `Agent default not found` or equivalent agent lookup warning.
- Input controls may appear disabled.

Report this as:
- CopilotKit UI embedded successfully.
- Runtime endpoint or agent registration not yet wired.

## Critical wiring checks

Always verify four things separately:
- experimental frontend port;
- experimental backend port;
- proxy target used by the experimental frontend;
- which backend actually answers `/api/copilotkit`.

A common failure mode is editing the experimental backend while the experimental frontend is still proxying to the old backend.

## Local-first rule

Keep data, calculations, auth, and side effects in the existing backend contour.
CopilotKit should be introduced first as:
- UI layer;
- interaction layer;
- structured handoff layer.

Only after that should it gain runtime-backed actions or analytics rendering.
