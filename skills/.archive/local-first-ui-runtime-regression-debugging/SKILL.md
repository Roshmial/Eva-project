---
name: local-first-ui-runtime-regression-debugging
description: Diagnose and repair local-first web UI regressions where build passes but the live UX is still wrong — especially contract-vs-UI drift, modal sizing/preview issues, prop-name mismatches, and browser-tool verification gaps.
---

# When to use

Use this skill when a local-first web UI has one or more of these symptoms:
- the user says the screen is still wrong even after a data-contract or API fix;
- the build succeeds but a screen, modal, or form still breaks at runtime;
- a React cleanup/refactor likely introduced prop-name drift between parent and child components;
- the user complains about noisy composer UI, oversized explanatory text, or poor legibility;
- file preview/lightbox behavior is functionally present but visually too constrained;
- Hermes browser tools partly work (`navigate` / `snapshot` / `console`) but visual verification is flaky, so you need to separate transport/session problems from rendering problems.

# Core rule for this class of task

Do not stop at “contract fixed” or “build green”.
For this class of issue, acceptance is the actual user-visible screen state.

Always distinguish three layers:
1. contract/API correctness;
2. runtime wiring correctness;
3. visible UX correctness.

A fix on layer 1 does not prove layers 2 or 3.

# Working model

Treat these regressions as a portfolio of failure modes, not a single bug:
- API/UI contract drift;
- parent→child prop mismatch;
- stale or overly verbose UI copy surviving a refactor;
- CSS constraints that make a feature technically present but practically unusable;
- browser-tool transport/session issues vs browser rendering issues.

# Workflow

## 1. Start from the screen the user is complaining about

Anchor on the user-visible defect first:
- what exact block looks wrong;
- what specific text is too noisy;
- which modal is too small;
- which navigation action breaks the form.

Do not immediately broaden into architecture unless the runtime evidence forces it.

## 2. Separate “surface owner” from “remote host” thinking

If the user identifies a host/port as a frontend surface, treat it first as a runtime surface to inspect, not as a server to SSH into by default.

Preferred order:
1. live UI/runtime evidence;
2. local code and bundle evidence;
3. host/process inspection only if the first two do not explain the defect.

Pitfall:
- Reaching for SSH too early wastes time and feels like dodging the actual UI problem.

## 3. Check for contract-vs-UI false closure

If you fix an API mismatch, explicitly ask yourself:
- does the screen still contain noisy copy;
- does the layout still match the user’s expected compactness;
- do preview modals still feel too small;
- are all expected controls still present and intelligible?

If not checked, assume the job is not finished.

## 4. For runtime breakage after refactor, audit prop-name drift first

When builds pass but navigation or modals explode at runtime, inspect parent render sites against child signatures.

Look specifically for:
- renamed props not updated at call sites;
- old prop names still passed after component cleanup;
- modals/screens requiring `open`, `userForm`, `userHistory`, `onOpenProfile`, `onToggleUser`, etc., while parent still passes legacy names;
- callback mismatches that only fail when the affected screen is opened.

This is often faster than chasing state logic.

## 5. Treat modal/image preview quality as a real acceptance item

For file preview and profile-file opening:
- increase modal width to fit the actual artifact, not just the old generic modal width;
- size by viewport (`vw` / `vh`) and use `object-fit: contain`;
- increase preview-stage min/max height so large images are readable without awkward dead space;
- confirm the preview is useful, not merely technically present.

Pitfall:
- “Preview exists” is not enough if the user still perceives it as cramped.

## 6. Compactness fixes must remove both structure and copy noise

When the user says the composer/panel is noisy:
- remove redundant headings and helper rows first;
- shorten placeholder/copy, not only spacing;
- keep only the controls the user explicitly expects;
- prefer one compact level of detail over mixed explanatory layers.

Pitfall:
- Reducing padding while leaving long labels and helper text is not a real compactness fix.

## 7. Browser-tool diagnosis: separate transport failure from rendering failure

If Hermes browser tools fail around `browser_vision` / screenshots:
- test whether `browser_navigate`, `browser_snapshot`, and `browser_console` already work;
- if those succeed, the problem is likely screenshot/vision path, not page session acquisition;
- if the 404-class error disappears after switching to a live-session screenshot path, treat blank screenshots as a separate rendering problem, not as the same bug.

Important framing:
- “tool no longer errors” and “visual capture is correct” are two different acceptance gates.

## 8. Rebuild and verify with concrete artifacts

After the fix:
- rebuild the frontend;
- record the actual built asset names;
- confirm the problematic strings/markers disappeared or appeared in the built bundle;
- if browser console is available on the live surface, confirm JS errors are zero on load.

# Verification checklist

Use this before claiming completion:
- Build passes.
- The user’s complained-about noisy text is actually removed or shortened.
- The expected controls are present and simpler.
- The preview modal is wider/taller and scales images to viewport.
- Runtime prop mismatches for the affected screens are corrected.
- Navigation into the affected screen no longer relies on stale prop names.
- Live browser console shows no obvious JS errors on entry.
- If browser screenshot tooling changed, distinguish “404 fixed” from any remaining rendering issue.

# User-specific delivery notes for this class

For this user:
- prefer fixing the current contour over proposing new architecture;
- do not hide behind server-side inspection when the complaint is clearly about the visible UI;
- report honestly when the transport/session bug is fixed but visual rendering still has a separate tail.

# References

- See `references/cdp-404-and-ui-regression-notes-2026-06-15.md` for the concrete regression pattern: browser-tool screenshot path moved to live CDP supervisor first; frontend runtime failure caused by prop-name drift despite successful build; preview modal needed viewport-based widening and autofit.
