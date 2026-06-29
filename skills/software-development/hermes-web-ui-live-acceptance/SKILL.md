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
   - If Playwright Chromium is blocked only by missing shared libraries and you do not have sudo, use a local user-space bootstrap instead of stopping: `apt download` the needed Ubuntu packages, unpack them with `dpkg-deb -x` under the project, assemble `LD_LIBRARY_PATH`, and launch browser automation through that wrapper. Capture the package list / wrapper pattern in a skill reference, not as an environment complaint.
   - Once the browser starts, verify that the app actually hydrated into the intended screen. A launched browser that still shows login/empty root is not an acceptance pass.

4. Test the full user path, not just the broken screen.
   - Navigate into the target screen from the real sidebar/top-level nav.
   - Then move back out into another screen.
   - Then return to chat and confirm the app still renders and navigation still works.

5. Verify ownership of the live data you are accepting.
   - Do not treat a successful backend run in any thread as proof that the user can see the result.
   - Before declaring a dashboard, report, or chat artifact "working in UI", confirm the target thread belongs to the intended live user/account.
   - If the artifact lives under a different `user_id` or email, treat that as a contour/acceptance miss, not a UI success.
   - For dashboard acceptance specifically, verify that the intended user's threads actually contain at least one assistant message with the expected `message_kind` such as `dashboard_result` before telling the user to look in the UI.
   - If necessary, inspect runtime storage or API responses to map `thread_id -> user_id/email` and verify you are testing the same chat surface the user is looking at.
   - When the user refers to "the last new thread" or another human label, resolve it explicitly by `user/account + title bucket + updated_at`, not by grabbing the last thread overall.
   - Inspect the actual last 4-6 messages in chronological order before diagnosing the bug; many acceptance misses come from reasoning about the wrong assistant step.
   - If the complaint is "dashboard is empty / not informative / talks about the agent", classify the problem before changing code: renderer defect, transport defect, semantic payload defect, or follow-up routing defect.
   - For contested cases, fetch `/api/threads/<id>` as the live user/session and compare the HTTP payload with the DB payload and the frontend renderer contract.
   - For export/download acceptance, prove that the same credentials work on both surfaces before blaming the export path: compare direct backend login and public-frontend `/api/auth/login` with the same user/password. If backend login succeeds but the public frontend proxy returns `401`, classify the blocker as auth/runtime contour mismatch first, not a document-export defect.
   - If direct API export works but token injection into the browser yields `Сессия истекла` or the public login form rejects known-good credentials, treat that as session-source or auth-secret divergence between contours. Separate "artifact contract works" from "public UI can authenticate into that contour" in your final verdict.

6. For file preview, verify end-to-end.
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
- Resolving "latest thread" loosely and diagnosing the wrong chat, wrong title bucket, or wrong assistant step.
- Seeing a green `dashboard_result` and calling the UI path successful without checking whether the sections contain real subject matter rather than fallback/route scaffolding.
- Misclassifying a short follow-up such as "по этой теме" as a fresh web collection request when it should transform the previous substantive answer into a dashboard.
- Running ad-hoc backend Python against the repo without the live runtime environment, then diagnosing the wrong database. On Hermes Web prod, direct `app` imports may default to local DuckDB when `HERMES_WEB_BACKEND_DSN` / related runtime env are not exported, even though the live backend serves Postgres. For live acceptance or backfill/reply actions, either go through the live HTTP surface with a valid session or mirror the running backend env before importing `app`.
- Declaring a dashboard follow-up fixed just because the assistant returned text. For this class of bug, confirm the assistant message metadata shows the intended transform path (for example `downstream=dashboard:previous_answer_transform`) rather than a fresh collection route or a generic fallback success.
- Opening a task/job modal from admin/users before its metadata is hydrated, then misdiagnosing the resulting blank state as a pure backend defect.
- Fixing the first broken screen but not checking whether the same change broke navigation back to chat/profile.
- Verifying preview through markup inspection instead of a real uploaded file.
- Declaring mobile fixed without an actual narrow viewport run.
- Leaving overlay/backdrop pointer interception in place after adding helpful onboarding UI.
- Treating a browser run as successful just because Chromium launched. If the page lands in `401` / expired-session login state or renders an empty root, acceptance is still blocked; switch to a real login flow and only then drive UI-state/navigation.
- Calling a public UI export path broken when the real defect is contour auth divergence: the same user can log into direct backend `:8791` but not through public frontend `/api/auth/login`. In that case fix or escalate runtime/auth wiring before judging the export button or file delivery path.
- Proving export only through direct API and then implying public UI acceptance is done. Keep those as separate claims unless the same contour and session source were verified.

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
- See `references/bi-dashboard-followup-routing-and-acceptance.md` for the pattern where the apparent UI/dashboard problem is actually one of four classes: wrong target thread, semantic dashboard fallback, transport mismatch, or follow-up routing failure such as `text -> dashboard` being misrouted into fresh web collection.
- See `references/local-playwright-user-space-runtime.md` for the user-space Playwright bootstrap pattern: local `apt download` + `dpkg-deb -x` + `LD_LIBRARY_PATH` wrapper when browser acceptance is blocked by missing shared libraries and sudo is not available.
- See `references/public-vs-direct-auth-split.md` for the Hermes Web pattern where direct backend login succeeds, public frontend proxy login fails, and document-export acceptance must be split into artifact-contract proof vs public-auth contour proof.
