# Deploy payload adjacent assets: split-runtime reminder

Use this when a split-prod rollout appears to deploy the right code but the target backend still fails after restart.

## Pattern

A backend host can receive the new main file successfully while still missing adjacent runtime assets that the new code now expects.

Typical examples:
- `services/backend/policies/*.json`
- prompt/config payloads loaded from relative paths
- scripts or helper files invoked at runtime

## Fast verification

1. Verify the remote code file really contains the new markers you expect.
2. Verify the referenced support file exists on the same host at the relative path the code uses.
3. If restart fails, inspect service logs immediately for `FileNotFoundError` or equivalent missing-path startup errors.
4. Only after that investigate env composition or restart mechanics.

## Hermes Web example shape

Observed split-prod pattern:
- public frontend already served the newer Sprint bundle;
- backend host still had an older `app.py`;
- after syncing the new backend file, the service still failed because a new policy file under `services/backend/policies/` had not been copied.

Lesson:
- for split-prod rollouts, treat `app.py` plus required policy/config neighbors as one deploy unit.
- do not declare the rollout broken until you confirm whether the failure is stale code, missing adjacent asset, or actual runtime/env misconfiguration.
