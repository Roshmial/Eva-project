---
name: stateful-admin-ui-roundtrip-debugging
description: Diagnose local-first admin screens where toggles, selectors, and save actions appear clickable but do not persist because state wiring, payload mapping, or split-runtime routing is wrong.
triggers:
  - Admin/settings/policy screen appears interactive but values do not stick
  - User says toggles, defaults, selectors, or assignments do not save
  - Frontend and backend both look partially correct, but live runtime still behaves as broken
  - Split contour where frontend host and backend host may differ
---

# Stateful admin UI round-trip debugging

Use this for local-first React/admin screens with draft state, save buttons, and live backend persistence.

## Goal

Prove where the break actually is in the chain:
parent props -> section component -> local draft state -> save payload -> backend normalization -> response -> post-save re-hydration -> live runtime delivery.

Do not stop at a code-looking fix. The deliverable is a verified live round-trip in the contour the user named.

## Workflow

1. Confirm the live contour
- Identify which host/port the user actually means.
- If frontend and backend are split, confirm the real API upstream the live frontend proxies to.
- Do not assume the backend lives on the same host as the frontend.

2. Inspect the full state chain before editing
- Find the parent screen props passed into the broken section.
- Check whether the section renders persisted state or draft state.
- Check whether the parent passes the handler name the child actually expects.
- For save flows, inspect the exact payload builder and the post-save re-hydration path.

3. Reproduce the round-trip with concrete data
- Read the current GET payload for the admin screen/API.
- Identify which UI controls map to which fields in the PATCH payload.
- Verify backend normalization rules: defaults, fallback behavior, empty-list handling, filtering of inactive keys, connector/group remapping.
- After PATCH, compare the response body with the intended state, not just the request.

4. Fix the smallest true break
- If UI shows stale values, fix prop wiring first.
- If payload is wrong, fix mapping from draft state to API contract.
- If backend overwrites explicit empty/changed state, fix normalizer logic so explicit payload beats defaults.
- If the code is correct but live still shows old behavior, verify which service/process actually serves the active bundle or API.

5. Verify in live runtime
- Rebuild/restart only the services that are actually in the user’s live contour.
- Confirm the live asset or live backend process now contains the fix.
- Re-run the exact failing round-trip against the live contour.

## High-value checks

### 1. Draft state vs persisted state mismatch
Common bug:
- child section renders `admin.someState`
- clicks mutate `draftState`
- save reads `draftState`

Symptom:
- controls appear clickable but visually revert or never reflect changes
- user reports “nothing works” even though save code exists

Fix:
- render the section from draft state
- pass the actual draft handler the section expects
- only fall back to persisted state for first hydrate

### 2. Wrong prop name between parent and child
Common bug:
- child expects `onPolicyDraftChange`
- parent passes `onDataPolicyDraftChange` under a different name, or vice versa

Symptom:
- checkbox/select appears present but changes do nothing or mutate the wrong branch

Fix:
- inspect the parent render call, not only the child component
- align prop names exactly

### 3. Empty-list semantics on backend
Common bug:
- UI intentionally sends an empty list
- backend normalizer treats empty as “missing” and restores defaults

Symptom:
- unassigning/disabling never sticks
- moved connector or cleared group snaps back after save

Fix:
- if the key is explicitly present in payload, preserve the empty list
- only inject defaults when the field is absent, not when it is explicitly empty

### 4. Split frontend/backend contour
Common bug:
- frontend is rebuilt on one host
- live `/api` traffic actually goes to another backend host

Symptom:
- bundle is fresh but behavior is still old
- user still sees broken persistence after frontend-only fix

Fix:
- inspect runtime env / proxy config / serving process
- patch and restart the real backend upstream too

### 5. Forced reloads that make the screen feel slow
Common bug:
- every tab open triggers a forced reload even when data is already present

Symptom:
- user reports “loading became longer” after a fix

Fix:
- use conditional reloads for admin tabs
- force reload only when data is absent or truly stale

## Acceptance checklist

Before saying it is fixed, verify all relevant items:
- The visible control reads from the same draft state that clicks mutate.
- The save handler sends the exact intended payload.
- Backend response preserves the intended change.
- Post-save hydrate shows the new value, not stale persisted state.
- The live frontend bundle is the updated one.
- If split contour exists, the live backend service is also updated.
- Re-entering the screen does not add unnecessary latency from unconditional reloads.

## Pitfalls

- Do not claim success from code inspection alone.
- Do not stop after a local build if the user is testing a remote contour.
- Do not assume a non-working toggle is a pure backend issue; parent/child prop wiring is often the real cause.
- Do not assume a successful PATCH means the UI is fixed; the bug may be in re-hydration.
- Do not optimize loading before proving correctness, but once correctness is fixed, remove unnecessary forced reloads if the user reports slower screen entry.

## References

- `references/policy-screen-roundtrip-pitfalls.md` — concrete patterns from a live Hermes Web policy-screen incident: split contour, wrong prop wiring, backend empty-list normalization, and reload cost.
