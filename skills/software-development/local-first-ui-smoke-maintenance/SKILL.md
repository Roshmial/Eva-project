---
name: local-first-ui-smoke-maintenance
description: Maintain and repair browser/UI smoke checks for evolving local-first web apps so acceptance scripts stay aligned with the real interface instead of flagging false regressions.
---

# When to use

Use this skill when a local-first web UI has a canonical smoke or acceptance script and one of these happens:
- runtime smoke starts failing after UI restructuring;
- profile/admin/jobs/chat screens still work live, but the scripted check fails;
- selectors, tabs, panels, or containers moved while product behavior stayed correct;
- you need to decide whether a failing smoke is a real product defect or test drift.

# Goal

Keep the acceptance path trustworthy.
A smoke script should fail on real user-facing regressions, not because it assumes an older DOM layout.

# Workflow

1. Reproduce the smoke failure exactly as-is.
   - Run the canonical smoke script first.
   - Capture the exact failing assertion, selector, or timeout.
   - Do not "fix" the app before confirming whether the failure is in product behavior or in the smoke script.

2. Check the live UI against the smoke assumption.
   - Open the app in the browser and walk the same user path manually.
   - Verify whether the target content still exists but is now behind a tab/section/panel.
   - Verify whether the target container id/class changed.

3. Classify the failure.
   - Real regression: the user path is broken in the live app.
   - Smoke drift: the live app works, but the script is checking the wrong tab, wrong section, or stale container.

4. Repair the smoke at the user-flow level, not just the selector level.
   - If content moved behind a tab, click the tab in the script before asserting.
   - If admin content moved from an overview panel to a dedicated screen, navigate there explicitly.
   - Prefer selectors that reflect user intent, such as section buttons and stable ids, over brittle positional selectors.
   - When a smoke fails on labels/placeholders/button text, inspect the current UI contract before retrying. Typical drift signals are renamed placeholders, renamed action buttons, tabbed profile sections, or create-forms that moved into a modal.
   - If the interface has materially diverged from a legacy smoke contract, prefer a React/UI-specific acceptance script over forcing the new UI to imitate stale selectors.

5. Re-run full acceptance after each repair.
   - Require the script to go green end-to-end.
   - If the smoke passes only after weakening assertions too far, restore meaningful checks.

6. Record the drift pattern.
   - Add a short note or reference file describing which UI assumptions changed.
   - This is especially useful for local-first admin surfaces that evolve quickly.

# Practical rules

- Treat the smoke script as a product artifact, not a disposable test.
- If live runtime is healthy and the smoke fails, assume "possible smoke drift" before declaring product regression.
- For this React/local-first class of apps, separate three states before changing code: backend task finished, frontend polling consumed the update, and UI rendered the final artifact. A smoke can fail because only the last two are stuck.
- When a browser-based smoke times out on a pending assistant bubble, verify whether the backend already produced the final message for that thread. If the backend thread payload has the completed assistant message with dashboard/meta but the page still shows `pending`, classify it as frontend runtime/polling/rendering investigation first, not backend generation failure.
- Keep assertions tied to user-visible outcomes:
  - uploaded file visible in the right profile area;
  - admin users render in the actual users panel;
  - jobs list renders on the actual jobs screen;
  - browser console/network errors remain empty.
- When the UI is sectioned, the smoke must explicitly open the relevant section before asserting content.
- For Playwright-based acceptance in this project class, prefer the project runtime wrapper around browser commands so the smoke uses the same browser library environment as the canonical acceptance path.

# Pitfalls

- Do not treat a moved panel as a backend/frontend regression without checking the current UI route/tab structure.
- Do not keep asserting against old containers after a tabbed refactor.
- Do not weaken the smoke into "page loaded" only; keep it user-meaningful.
- Do not call a failure "fixed" until the canonical smoke script itself is green again.

# Verification

Minimum completion bar:
- frontend syntax check passes;
- backend syntax or smoke checks pass if the user flow crosses backend write/read paths;
- canonical UI smoke passes end-to-end;
- live browser walk confirms the script now matches the real UX.

# References

- See `references/hermes-web-mvp-selector-drift.md` for a concrete example of smoke drift caused by profile/admin tab restructuring in Hermes Web MVP.
- See `references/hermes-web-mvp-react-smoke-drift-patterns.md` for React-era drift examples: ambiguous nav labels, renamed placeholders/buttons, modalized create flows, and file/open-link acceptance checks.
