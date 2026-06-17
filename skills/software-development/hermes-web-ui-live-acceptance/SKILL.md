---
name: hermes-web-ui-live-acceptance
description: Live acceptance and runtime verification for Hermes Web UI when build success is not enough — especially for screen navigation, mobile behavior, file preview, chat refresh, and split frontend/backend contours.
---

# When to use

Use this skill when working on Hermes Web UI tasks where the risk is not syntax/build failure but runtime breakage:

- a screen opens but crashes after navigation
- a tab or modal works in code review but fails in the browser
- mobile layout hides navigation or blocks taps
- chat updates appear only after manual refresh
- file preview exists in code but must be verified end-to-end
- frontend and backend live on different hosts/ports and acceptance must respect contour separation

This skill is especially relevant for the user's local-first Hermes Web workflow, where `95.182.85.233:8803` is the frontend surface and `178.104.207.89:8791` is the prod backend. Do not assume nearby dev ports on the frontend host are the right backend.

# Core rule

A passing build is necessary but not sufficient. Treat runtime prop/handler drift, overlay interception, hidden mobile navigation, and stale refresh behavior as first-class defects even when `npm run react:build` succeeds.

# Acceptance workflow

1. Confirm the contour before testing.
   - Identify which host/port is the frontend surface.
   - Identify which host/port is the real backend for this contour.
   - If the user names a specific live surface such as `95.182.85.233:8803`, treat that exact contour as the target and stop reasoning from nearby previews or older ports.
   - Do not point a dev proxy at a convenient-looking port without checking it responds as the intended backend.
   - Verify which process is actually serving the named port, its cwd/project root, and which built assets it is serving before you conclude your code change is live.

2. Build first, but do not stop there.
   - Run the frontend build.
   - Use the build only as a gate, not as proof of runtime correctness.

3. Run a live browser acceptance path.
   - Prefer a local dev/preview frontend wired to the intended backend if the user-facing surface is not yet redeployed.
   - Use Playwright/browser automation to click through the exact affected path.
   - Capture console/page errors; runtime `ReferenceError`/missing handler defects often surface only here.

4. Test the full user path, not just the broken screen.
   - Navigate into the target screen from the real sidebar/top-level nav.
   - Then move back out into another screen.
   - Then return to chat and confirm the app still renders and navigation still works.

5. For file preview, verify end-to-end.
   - Create or use a real file belonging to the current acceptance user.
   - Open profile → files.
   - Click the open action.
   - Confirm the modal opens and, for images, that an actual `<img>` preview renders.
   - Do not call preview fixed just because the modal component exists in JSX.

6. For chat refresh, verify behavior with and without pending state.
   - Prefer a path that creates a pending assistant placeholder long enough to observe refresh.
   - If the backend answers too fast, still verify the polling code path and immediate refresh behavior from the live UX.

7. For mobile, test a narrow viewport explicitly.
   - Check that the relevant nav button is visible.
   - Check that tapping it activates the correct screen.
   - Check that overlays do not intercept pointer events.

8. After fixes, re-run build and live acceptance.
   - Record what was verified in decision-log if the issue was a major UI/runtime incident.

# High-value checks

## Jobs/task screen

When the `Задачи` screen is involved, specifically check:

- the nav button is visible on desktop and mobile
- clicking it does not blank the app or unmount the root
- `JobsScreen` receives real handlers, not stale prop names
- create/edit/recipient/access actions are wired to existing functions
- if a user-specific action such as `Пользователи -> Назначить задачу` opens a blank or nearly blank modal, inspect whether the modal depends on `jobsMeta` or other lazily loaded state that is not guaranteed to be hydrated before opening
- prefer to preload required jobs context before opening the modal and show a non-empty loading/fallback state while metadata is still arriving

## Mobile navigation

Check for CSS that hides critical navigation on narrow widths. A mobile-only `display: none` on a core nav button is a regression even if desktop works.

## Overlay/onboarding behavior

Check whether onboarding/help overlays block pointer events to the main navigation. If the intent is advisory, prefer a non-blocking overlay or close it on navigation.

## Chat refresh

Look for polling logic tied to active thread/screen state. Prefer:

- immediate first refresh on entering chat
- faster interval when pending assistant content exists
- slower steady-state interval otherwise

# Common pitfalls

- Treating `npm run react:build` as proof that runtime props are correct.
- Testing the wrong backend because the frontend host also has old/dev ports nearby.
- Assuming a named live port is serving your latest code without checking the serving process, cwd, and current built asset names/hashes.
- Opening a task/job modal from admin/users before its metadata is hydrated, then misdiagnosing the resulting blank state as a pure backend defect.
- Fixing the first broken screen but not checking whether the same change broke navigation back to chat/profile.
- Verifying preview through markup inspection instead of a real uploaded file.
- Declaring mobile fixed without an actual narrow viewport run.
- Leaving overlay/backdrop pointer interception in place after adding helpful onboarding UI.

# Known durable pattern from this class of incidents

A frequent Hermes Web failure mode is `App.jsx` passing non-existent handlers into screen components after UI cleanup/refactors. This can survive build and only explode at runtime when the user opens that screen. When a screen crashes immediately on navigation, inspect parent→screen prop bindings before assuming the child component itself is broken.

# Deliverable standard

Do not finish with only code changes. A completed task in this class should include:

- build result
- live runtime/browser verification result
- explicit note about which contour was tested
- if applicable, decision-log update

# References

- See `references/june-2026-jobs-mobile-refresh.md` for a concrete acceptance pattern covering jobs screen runtime-prop drift, mobile nav visibility, profile file preview, and chat auto-refresh verification.
- See `references/8803-user-job-modal-hydration.md` for the 8803-specific pattern: verify exact live port ownership, confirm built asset rollover, and treat blank `Назначить задачу` modals as a possible jobs-metadata hydration race.
