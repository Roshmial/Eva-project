---
name: copilotkit-local-first-web-integration
description: Integrate CopilotKit into an existing local-first React/web app as an isolated preview first, then connect runtime and structured UI actions without breaking the main chat UX.
---

# When to use

Use this skill when you need to add CopilotKit to an existing local-first web product, especially when:

1. there is already a working chat-first UI;
2. you need a safe preview lane on a separate port or copy;
3. you want to prove UI integration before wiring the full runtime;
4. you must avoid breaking the main user-facing interface.

# Core approach

Treat CopilotKit as a UI integration layer first, not as the source of truth for data or actions.

Preferred rollout order:

1. Clone the currently working web contour into an isolated sibling copy.
2. Give the copy its own frontend port and, if possible, its own backend port.
3. Mount CopilotKit at the React root with a preview popup or sidebar.
4. Verify the UI loads in a real browser before building runtime logic.
5. Only then wire `/api/copilotkit` to a real runtime or adapter.
6. Once backend proxying exists, collapse the contour to one canonical route: frontend `runtimeUrl` should point to `/api/copilotkit`, and backend should own forwarding to any sidecar/runtime port.
7. After runtime works, add structured context/actions instead of dumping the whole chat thread into CopilotKit.

For Hermes-style chat-first products, do not stop at “CopilotKit is visible”. The product goal is functional assistance over existing screens and entities: navigation, opening a thread, preparing a message draft, preparing a recurring-job draft, opening an existing file, or similar actions that reuse the app's current state and handlers.

Important for user-facing product contours:
- if the product decision is "chat-first, without CopilotKit UI artifacts", do not leave `CopilotSidebar`, `Open Chat`, `CopilotKit preview`, or similar third-party chrome visible in the canonical frontend;
- a visible CopilotKit popup/sidebar is acceptable only in an isolated preview lane or temporary validation contour;
- in the canonical contour, prefer keeping only the provider/runtime/action bridge layer and expose help through the product's own UI, copy, and flows.

# Minimum viable integration

## Frontend

1. Parameterize the frontend port instead of hardcoding it in Vite or launcher scripts.
2. Mount `CopilotKitProvider` once near the React root.
3. Import v2 components from `@copilotkit/react-core/v2`.
4. Import the v2 stylesheet.
5. Start with `CopilotPopup` or `CopilotSidebar` in preview mode.
6. Keep labels and instructions explicit that the contour is preview-only until runtime is connected.

Important:
- For v2, use `@copilotkit/react-core/v2` for components.
- Do not assume `@copilotkit/react-ui` provides the active v2 components.

## Backend

1. Keep the existing app/backend as source of truth.
2. Add a placeholder `/api/copilotkit` route early if you want the UI contour visible before the runtime exists.
3. Prefer a separate backend port for the experiment, then point the experimental frontend proxy to it.
4. If backend isolation is not ready yet, be explicit that the frontend is still proxying to the old backend.
5. If the backend route answers `501` or is explicitly preview-only, do not pretend it is a usable runtime. Route the frontend to a standalone local runtime through the existing frontend proxy layer (for example `/copilotkit -> 127.0.0.1:<runtime-port>`) and expand runtime CORS to the actual frontend dev ports.
6. As soon as backend proxying is ready, remove the direct frontend-to-runtime route as the product default. The stable product contour should usually be:
   - frontend UI -> `/api/copilotkit`
   - backend -> local runtime or adapter
   - runtime remains an internal implementation detail
7. If you keep the sidecar runtime, parameterize its base URL and timeout in backend env defaults instead of hardcoding them only in Vite.

# Verification sequence

1. Confirm the experimental frontend serves HTML on the new port.
2. Open the page in a real browser.
3. Verify the main app shell still renders.
4. Verify the CopilotKit popup/sidebar is visible.
5. Check browser console for:
   - missing runtime info (`/api/copilotkit/info` 404);
   - agent-not-found warnings;
   - React warnings introduced by the embedded UI.
6. Record separately whether:
   - UI embed works;
   - runtime works;
   - agent wiring works.

Do not collapse these into one binary “works / does not work”.

# Pitfalls

## Pitfall: mixing preview UI success with runtime success

A popup appearing in the browser means only that the UI integration works.
It does not mean the runtime is connected.

Symptoms of preview-only state:
- popup/sidebar renders;
- chat input may be disabled;
- console shows `/api/copilotkit/info` 404 or runtime warnings;
- agent lookup fails.

Report this honestly as: UI integrated, runtime not yet wired.

## Pitfall: wiring the experimental frontend to the old backend by accident

If the new frontend still proxies to the old backend, `/api/copilotkit` changes in the experimental backend will never be exercised.

Always verify:
- frontend port;
- backend port;
- proxy target;
- which backend actually answers `/api/service-info` and `/api/copilotkit`.

## Pitfall: leaving two competing CopilotKit routes alive

A common local-first half-integrated state is:
- frontend proxy `/copilotkit` already points to a working sidecar/runtime port;
- backend still exposes `/api/copilotkit` as a preview-only `501` stub.

In that state the UI can look alive and runtime discovery can succeed, while the backend still claims CopilotKit is not configured.

Do not report this as fully finished. State it explicitly as route divergence and verify both paths separately:
- frontend-visible runtime path (`/copilotkit` through Vite/proxy);
- backend-owned path (`/api/copilotkit` or equivalent);
- which one is the intended canonical route for the product.

If the sidecar path is the temporary truth, say so plainly. If the backend route is meant to become canonical, schedule a short follow-up to remove the stale preview/stub state.

Canonicalization checklist when finishing the integration:
- frontend default `runtimeUrl` points to backend-owned `/api/copilotkit` rather than direct `/copilotkit`;
- backend default port/envs match the actually deployed backend port;
- launcher scripts, Vite proxy, backend env defaults, and smoke scripts all agree on the same ports;
- old preview-only messages and `501 preview_only` behavior are removed from the canonical route;
- runtime sidecar remains reachable directly for diagnostics, but is no longer the primary user-facing route.
- live verification covers not only runtime info/discovery, but also the first thread-aware sidebar calls (`GET /api/copilotkit/threads?agentId=...`, optional subscribe/mutation calls) so the UI does not stall after looking "mostly connected".

### Thread-aware runtime verification

A backend-owned `/api/copilotkit` route can pass discovery checks and still fail the first real sidebar interaction.

Typical sequence from the live UI:
- POST `/api/copilotkit` for runtime metadata / discovery;
- GET `/api/copilotkit/threads?agentId=default`;
- sometimes POST `/api/copilotkit/threads/subscribe`;
- then POST `/api/copilotkit` for the actual message/run path.

Practical rule:
- do not stop at `GET /info` or `POST { method: 'info' }`;
- verify at least one thread-list call from the same frontend contour;
- if upstream runtime returns `405` on thread endpoints but the product only needs the sidebar not to break, a small backend fallback/adapter response may be acceptable as an intermediate contour;
- report that honestly as a compatibility shim, not as full thread persistence.

## Pitfall: duplicate backend instances on one DuckDB make CopilotKit debugging lie

If several backend processes from the same repo are alive on different ports and point to the same DuckDB file, you can get misleading symptoms:
- login or setup intermittently fails with DB lock errors;
- one port answers `/api/service-info`, another answers `/api/copilotkit`, and a third still holds the DB lock;
- the user thinks there are several real deployed versions, while in practice it is one tree started multiple times.

Before blaming CopilotKit, audit the live contour:
- list listeners for frontend/backend/runtime ports;
- identify PID, command line, and working directory for each;
- confirm whether extra ports are just duplicate Vite/backend instances from the same repo;
- kill the duplicates before runtime conclusions.

Treat an unexpected extra port as "operator noise until proven otherwise", not as a separate environment.

## Pitfall: re-opening already settled naming questions during integration work

When the user explicitly says a naming/display-name/alias issue was already resolved, do not spend the CopilotKit verification pass revisiting it.

Stay scoped to the current integration question:
- backend/runtime health;
- frontend embed;
- proxy/canonical route;
- real Copilot actions.

Only return to the old naming question if new runtime evidence shows it is directly breaking the current CopilotKit flow.

## Pitfall: frontend dashboard UI is ready, but the live backend still returns the old text-only analytics path

A dangerous half-finished state is:
- frontend already renders `message.meta.dashboard` and has a starter action/button for analytics;
- backend source code contains a local dashboard route/helper;
- but the live response on the real port still comes back from an older Hermes/analytics path as plain text plus file links, without `meta.dashboard`.

In this state build/tests can be green while the user-visible dashboard never appears.

Verification rule:
- do not stop at code inspection of `should_build_...` / `maybe_build_...` helpers;
- send a real thread message through the live backend route the UI uses;
- then inspect the persisted assistant message returned by the API or fetched back from the thread;
- explicitly confirm whether `assistant_message.meta.dashboard` exists in the live payload.

If the live message lacks `meta.dashboard`, report the contour honestly as:
- frontend render contract prepared;
- backend live route still serving a different reply path;
- dashboard artifact not yet end-to-end verified.

Before changing logic again, run the stale-runtime checklist:
- compare the start time of the PID listening on the target backend port with the mtime of the edited backend file;
- inspect that PID's `cwd` and `HERMES_WEB_*` env, not just the repo on disk;
- check whether a sibling project copy on another port is adding noise or stealing your attention;
- if direct import of the current source returns the expected dashboard payload but the live API still does not, treat this first as a probable stale-process mismatch, not as proof that the helper logic is wrong;
- restart the backend via the project's canonical launcher script, then repeat the same live API check before doing deeper refactors.

This is especially important for chat-first integrations where the UI artifact depends on structured assistant metadata rather than free text.

See `references/live-runtime-code-mismatch-stale-process.md` for the concrete API-first diagnosis pattern.

## Pitfall: debugging CopilotKit before checking whether the cloned preview lane is structurally damaged

If the experimental sibling copy was produced through a lossy copy/export step, files can be damaged before CopilotKit logic is even exercised.

Typical red flags:
- source lines prefixed with `N|` or even `N|N|`;
- `App.jsx` or backend files cut off mid-component or mid-function;
- CSS tail missing, causing unbalanced-brace warnings;
- smoke/build failures that look like logic regressions but are really file corruption.

Recovery rule:
- audit file integrity first;
- restore large damaged files from the nearest healthy sibling copy instead of reconstructing them from memory;
- only then re-apply the intended CopilotKit/dashboard patches;
- re-run backend smoke and frontend build before doing live runtime conclusions.

See `references/copilotkit-cloned-preview-recovery.md` for the recovery pattern.

## Pitfall: duplicate dev servers create fake "multiple versions"

If you see an unexpected extra frontend port (for example `8824`) do not assume it is a second real deployment.

First verify:
- listening PID;
- command line (`vite`, `node`, etc.);
- working directory of the process;
- whether it is the same repo started twice with different ports.

A duplicate Vite server from the same working tree should be treated as operator noise, not as a separate environment. Kill or retire it before doing architecture conclusions, otherwise route audits become misleading.

## Pitfall: treating runtime sidecar root as a user-facing page

A local CopilotKit runtime/sidecar port is often not a browsable product surface.

Typical healthy behavior:
- runtime-specific paths such as `/copilotkit` or `/copilotkit/info` answer;
- the bare runtime root `/` may return `404`.

Do not report `http://127.0.0.1:<runtime-port>/ -> 404` as a product bug by itself.
First distinguish:
- product frontend port;
- backend API port;
- internal CopilotKit runtime port.

Only the frontend port should be judged as a user-facing page.

## Pitfall: backend 500 HTML gets misreported by frontend as "service returned non-JSON"

If the UI shows a banner like `Сервис вернул не JSON (500)`, do not assume the frontend parser is the root problem.

First reproduce the exact backend endpoint and inspect the live server traceback. In this class of apps a missing helper or stale function name in a newly added admin endpoint can produce:
- backend `500` with HTML error page;
- frontend JSON parse failure banner;
- a misleading impression that the UI contract is wrong.

Rule:
- confirm the failing endpoint directly;
- read the traceback;
- fix the backend exception first;
- only then revisit frontend error presentation.


## Pitfall: hardcoded ports in multiple places

Check all of these:
- `vite.config.*`
- launcher scripts
- env defaults
- CORS allowlist
- any browser smoke or health-check scripts

## Pitfall: provider/sidebar injection into a large existing App in one giant replacement

When an existing `App.jsx` has a huge inline `return (...)`, a mechanical one-shot replacement can easily break JSX structure and produce hard-to-read compile errors like `Expected ";" but found "open"` far away from the real mistake.

Safer pattern:
- first extract the current app shell into `const appContent = (...)`;
- then wrap `appContent` with `CopilotKit` in a small final return;
- add `HermesCopilotBridge` and `CopilotSidebar` in separate clearly visible nodes;
- keep modals and overlays intentionally inside or outside the provider instead of inheriting placement from a string replace;
- run a build immediately after each structural patch.

## Pitfall: treating CopilotKit as a decorative widget

If the user asks for functional CopilotKit, do not spend the iteration on generic UI polish or a passive preview bubble.

Minimum useful layer:
1. readable context derived from current screen/state;
2. 2–5 explicit frontend actions that reuse existing handlers;
3. honest separation between what CopilotKit can prepare and what the app/backend still authoritatively saves or executes.


For chat-first products, CopilotKit should usually do one of these:
- surface a preview popup/sidebar;
- turn chat outcomes into structured UI artifacts;
- bridge from discussion to dashboard/draft/action mode.

It should not be treated as a replacement for the existing app state, backend rules, or authoritative analytics layer.

# Deliverable standard

A finished step in this class of work should state explicitly:
- experimental copy path;
- frontend port;
- backend port;
- whether CopilotKit UI is visible;
- whether runtime endpoint responds;
- whether an agent is actually available;
- remaining blockers.

# References

- See `references/hermes-web-preview-lane.md` for a concrete preview-lane pattern and the specific browser/runtime symptoms that distinguish UI-only integration from full runtime wiring.
- See `references/hermes-web-functional-runtime-pattern.md` for the local proxy/runtime pattern, action design, and JSX integration pitfalls discovered while turning a preview contour into a functional CopilotKit layer.
- See `references/backend-owned-canonical-route.md` for the handoff from temporary sidecar-first routing to a single backend-owned canonical route, plus the duplicate-dev-server audit checklist.
- See `references/copilotkit-thread-aware-runtime-verification.md` for the post-discovery sidebar checks (`/threads`, subscribe, first message path) and the DuckDB/duplicate-process audit pattern.
- See `references/copilotkit-cloned-preview-recovery.md` for the recovery pattern when an isolated CopilotKit preview lane was copied with line-number artifacts or truncated source files.
- See `references/live-dashboard-meta-verification.md` for the API-first check that confirms whether the live chat flow really emits `meta.dashboard` or is still returning an older text-only analytics path.
- See `references/live-runtime-code-mismatch-stale-process.md` for the diagnosis pattern when source code and live API behavior diverge because the target port is still served by an older backend process.
- See `references/backend-proxy-pass-through-pattern.md` for the canonical local-first fix when frontend already targets `/api/copilotkit`, the sidecar runtime is healthy, but the main backend still does not proxy the route.
