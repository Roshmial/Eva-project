# Prod token-accounting false-freshness pattern

When a live backend fix seems to exist on disk but not through the public API, check for probe-induced false freshness.

## Symptom

- Public reply from the live API still lacks the new field/behavior.
- An off-process probe that imports `services/backend/app.py` appears to show the new behavior.
- DB rows created by the probe may reflect the new code even before the real service is restarted.

## Root cause

In this backend shape, importing `app.py` is not passive:
- module import runs startup hooks;
- startup hooks can recover pending tasks and start a chat processor thread;
- the probe process can therefore process queued work itself.

That means the probe is no longer observing the running service — it is acting like a second temporary worker.

## Safe verification sequence

1. Verify the behavior through the public user path first.
2. If you need DB inspection, disable chat-processor startup for the probe process.
3. Compare:
   - public API response meta;
   - persisted `messages.meta_json`;
   - code on disk;
   - running service state.
4. If code on disk is newer than public behavior, restart the real service.
5. Re-run the same public probe after restart.

## What this catches

- false claims that a prod rollout is already live;
- confusion between code-state and running-process state;
- accidental verification through an ad-hoc worker instead of the real service.
