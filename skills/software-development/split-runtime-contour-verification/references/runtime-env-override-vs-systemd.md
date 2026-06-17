# Runtime env override vs systemd: diagnostic note

Use this pattern when a split runtime looks correctly configured in `systemctl cat`, but the live process still behaves as if an older local-only config is active.

## Symptom shape

- frontend origin serves HTML normally;
- backend health endpoint is alive;
- browser still cannot log in or bootstrap data;
- CORS or target URL headers reflect an unexpected local origin such as `127.0.0.1` even though the unit drop-in advertises the public origin.

## High-probability cause

The service is launched through a shell wrapper that sources an additional env file such as `~/.hermes/.env` or `runtime_env.sh`. That shell layer can override or reconstruct variables after systemd has already injected correct-looking values.

## Verification sequence

1. Inspect the unit and drop-ins with `systemctl --user cat <unit>`.
2. Inspect the launcher script (`run_backend_service.sh`, `runtime_env.sh`, similar).
3. Check whether the launcher sources `~/.hermes/.env` or another shared env file.
4. Read the running process environment from `/proc/$PID/environ`.
5. Compare the live env values with the unit drop-in and with the sourced env file.

## Durable lesson

For split runtime diagnosis, `systemctl cat` is necessary but insufficient. The live process environment is the source of truth when headers, CORS, backend targets, or model-routing values do not match what the unit appears to declare.
