# Live runtime owner and env source verification

Use this reference when a split-host web runtime appears to have the right config in files, but live behavior does not match.

## Durable pattern

When checking backend routing or limits on a remote host:

1. Start from the listening port, not the repo tree.
2. Resolve the live PID from the listener.
3. Inspect:
   - `/proc/<pid>/cwd`
   - `/proc/<pid>/cmdline`
   - `/proc/<pid>/environ`
   - the launching systemd unit
4. If the unit calls a wrapper script, read that script before reading env files.
5. Only then inspect the specific env file actually sourced by the wrapper.

## Why this matters

A host can contain:

- several similar repo copies;
- multiple `runtime_env.sh` files at different directory levels;
- units that inject additional `Environment=` overrides;
- model candidate strings in env that do not become real retry chains after parsing.

## Concrete lesson captured from this session class

A backend process on port `8791` was launched from a wrapper script that sourced `scripts/runtime_env.sh`, while a different `services/backend/runtime_env.sh` nearby still contained older defaults.

The live process environment showed the real per-user reasoning limit, and `/api/health` confirmed it externally. However, reasoning fallback was still not effectively two-step because the deployed parsing/routing path produced a single-model attempt chain at runtime.

## Verification checklist for model fallback

Treat these as separate checks:

1. Env string contains candidate models.
2. Deployed code parses those candidates into the expected ordered list.
3. Attempt-chain resolution for the requested model returns more than one model.
4. Runtime metadata exposes fallback-related fields or health data consistent with the intended chain.

Do not stop after step 1.
