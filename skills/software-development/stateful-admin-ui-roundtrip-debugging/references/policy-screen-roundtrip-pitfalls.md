# Policy screen round-trip pitfalls

Condensed lessons from a live Hermes Web admin/policy incident.

## 1. Frontend can be correct-looking but wired to the wrong state

Observed pattern:
- parent component passed `admin.dataPolicy` into the policy section
- clicks mutated `dataPolicyDraft`
- child expected a different callback name than the parent passed

Result:
- toggles, connector assignments, and default selectors looked interactive
- user experienced the screen as "stable not working"

What to verify:
- child render props exactly match the parent call site
- section renders draft state, not stale persisted state
- callback names line up 1:1

## 2. Backend empty-list handling matters for connector reassignment

Observed pattern:
- UI explicitly sent an empty group like `internal_connector: []`
- backend normalizer restored default members because it treated empty as missing

Result:
- connector type changes and unassignments snapped back after save

Durable fix pattern:
- if a group key is present in payload, preserve its list even when empty
- only restore defaults when the group key is absent

## 3. Split contour means frontend fix may not be enough

Observed pattern:
- live frontend on one host proxied `/api` to a different backend host
- frontend bundle was fresh, but backend behavior still reflected old normalization logic

What to verify:
- real proxy target from runtime env
- actual backend service/process for the live contour
- restart the live backend service after patching the real upstream host

## 4. Re-entry slowness can come from unconditional admin reloads

Observed pattern:
- opening `data_policy` and `operations` forced `loadAdmin(true, section)` every time

Result:
- user noticed slower screen loading after correctness fixes

Durable fix pattern:
- reload only when that section's data is absent or stale enough to justify it

## 5. Live verification should prove the round-trip, not just deploy artifacts

Minimum proof set:
- live bundle contains the frontend fix
- live backend returns the intended PATCH response
- post-save hydration still shows the change
- re-entering the screen does not revert the visible state
