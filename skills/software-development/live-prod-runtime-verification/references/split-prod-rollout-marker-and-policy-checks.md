# Split-prod rollout marker and policy checks

Use this when a public frontend and a backend/runtime host are deployed separately and a product slice may be only partially live.

## Core lesson
Frontend proof and backend proof are different things.
A public JS bundle can already contain the new UI contract while the backend host still runs old code, or vice versa.

## Verification pattern
1. Public frontend:
   - fetch `/` and identify the active JS bundle;
   - inspect the bundle or live DOM for the expected markers/behaviour.
2. Backend/runtime host:
   - inspect the real source file or service artifact on the host;
   - verify the same contract markers exist there too;
   - check the live unit status and health endpoints after rollout.
3. If SSH is available only to the backend host:
   - use host-level verification for backend/runtime;
   - use public HTTP/bundle proof for the frontend;
   - report that frontend machine-level proof is still narrower if host access is absent.

## Rollout completeness rule
When new backend code imports policy/spec/reference files at startup, deploy those files together with the main Python file.
Do not treat `app.py` as the whole release unit.

## Failure signature
- backend was healthy before restart;
- after deploying new code and restarting, service crashes immediately;
- journal shows `FileNotFoundError` for a new policy/spec JSON under `services/backend/policies/...`.

## Correct interpretation
This is a rollout-package gap.
The right fix is to deploy the missing support file and let the service come back up, not to roll back the whole feature prematurely.
