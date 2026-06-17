---
name: frontend-backend-contract-reconciliation
description: Diagnose and repair local-first web UIs when frontend code has drifted from the current backend API contract, causing missing controls, broken admin screens, or silent UX regressions.
---

# When to use

Use this skill when a local-first web app shows signs that the React/Vue/frontend layer no longer matches the backend contract, for example:

- runtime errors like `X is not a function` on API helpers
- admin pages failing after backend endpoint consolidation or renames
- expected controls disappearing even though backend capability still exists
- chat/request-parameter UI no longer exposing backend options
- the user says "everything changed on ровном месте" and suspects an unexpected frontend regression

This skill is especially useful for Hermes-style local-first stacks where the backend shape changed from one payload contract to another, but the frontend still expects the old shape.

# Goal

Restore a working UI by reconciling the frontend with the actual backend contract instead of patching symptoms one by one.

# Core principle

Treat this as a contract-drift problem first, not a cosmetic UI bug.

Check three layers separately:

1. frontend calls and expected payload shape
2. backend endpoints and real response shape
3. built artifact/runtime proof that the fixed code actually made it into the bundle

Do not trust assumptions from memory, old notes, or prior UX discussions until the live contract is re-read from code and verified by build/runtime artifacts.

# Workflow

1. Reproduce the symptom from the exact error text.
   - Example: `O.getAdminDataSources is not a function` means the UI is calling an API helper that no longer exists in `api.js`.

2. Inspect the frontend API wrapper first.
   - Find the exported helpers in `src/api.js` or equivalent.
   - Confirm whether the failing helper exists.
   - If it does not exist, identify the current helper/endpoints that replaced it.

3. Inspect the caller in the screen/component.
   - Find where the missing helper is invoked.
   - Read enough surrounding code to understand the UI's expected response shape.
   - Capture the old expected shape explicitly, e.g. `source_registry + processing_policy`.

4. Inspect the backend contract.
   - Read the actual backend routes and normalization functions.
   - Identify the real response and patch shape now served.
   - Separate transport contract from UI convenience shape.

5. Decide whether to:
   - rewire the UI to the new backend contract directly, or
   - add a frontend normalization layer that maps the new backend contract into the old UI shape.

   Prefer a normalization layer when:
   - the backend contract is already coherent,
   - several UI areas depend on the old shape,
   - the user needs a fast recovery without redesigning the whole screen.

6. Restore the user-visible controls the user cares about.
   - Reconcile the UX with the backend capability, not just the data fetch.
   - If the backend still supports options like `model_preference`, `source_mode`, or `explicit_source_ids`, expose them again in the chat parameters UI.

7. Update request payload assembly.
   - Verify that the UI not only renders controls, but also sends the matching backend fields.
   - Common misses: UI selector restored visually, but payload still omits `model_preference` or source-policy fields.

8. Build the frontend.
   - Do not stop at code edits.
   - Produce a real bundle and inspect it for expected markers.

9. Verify with artifact-level proof.
   - Confirm that the built JS contains the restored labels/paths and no longer contains the removed helper call.
   - When possible, also verify in the running runtime.

# What to look for

## Typical drift patterns

- frontend expects helper `getAdminDataSources`, backend now exposes `getAdminDashboardPolicy`
- frontend expects `data_policy.processing_policy/source_registry`, backend now exposes `dashboard_policy + data_sources + llm_routing`
- backend still supports request fields like `model_preference` and `source_mode`, but the chat UI stopped exposing them
- admin editor still saves two old endpoints, while backend now wants a single normalized policy patch

## Good repair pattern

Add a small, explicit normalization function in the frontend that converts backend payloads into the UI shape the screen already knows how to render.

This is often safer and faster than rewriting all components immediately.

# Pitfalls

- Do not treat a missing UI control as proof the backend feature was removed.
- Do not patch only the fetch call; also patch save flow and outgoing request payloads.
- Do not claim success from source code alone; always rebuild and inspect the artifact.
- Do not confuse bootstrap payloads with admin payloads if the backend serves related data in different shapes.
- Do not stop after fixing the crash if the user's real complaint was broader UX regression.

# Verification checklist

- failing helper reference removed from source
- replacement endpoint/helper used consistently in load + save flows
- expected selectors/options visible in source after patch
- frontend build succeeds
- built bundle contains restored user-facing labels and current endpoint path
- built bundle no longer contains removed helper name
- backend tests covering the related capability still pass

# Reference files

- `references/hermes-web-contract-drift-case.md` — concrete example of reconciling Hermes Web frontend with renamed admin endpoints and reshaped chat/admin policy payloads.
