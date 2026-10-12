# Admin/policy hydration acceptance

Use this when a local-first admin screen renders the shell immediately but hydrates policy/data-source state asynchronously.

## Failure mode

A heading or select can appear before the real data arrives. If you interact too early, you get a false result:
- default select value instead of API-backed value;
- zero repeated rows even though the feature is healthy;
- a UI save test that proves nothing because the form was still in fallback state.

## Acceptance pattern

1. Separate proofs.
- First prove the backend contract directly.
- Then prove the UI round-trip.

2. For backend contract acceptance, verify policy behaviour directly.
- `local_only` must exclude global sources.
- `global_only` must exclude local/internal sources.
- `local_first` may allow both, with local-first semantics handled by runtime.

3. For UI acceptance, wait for hydration-specific signals, not just shell visibility.
Good signals:
- repeated source rows exist (for example `[data-source-key]` count > 0);
- connector rows exist when expected;
- the mode select value matches API state, not a hardcoded/default fallback.

4. Only after hydration:
- change the control;
- save;
- verify the save request succeeded;
- reload;
- wait for hydrated rows again;
- verify the same value in DOM and API.

## Practical note

If browser acceptance is flaky, do not blur the layers together. Report separately:
- backend contract: passed/failed;
- live UI round-trip: passed/failed/blocked.

That keeps confidence honest and avoids claiming a full UI pass from backend-only evidence.
