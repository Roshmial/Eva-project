---
name: hermes-local-install-troubleshooting
description: Troubleshoot a local Hermes installation when toolsets are unavailable because optional Python dependencies or config migrations are missing.
version: 1.0.0
created_by: agent
---

# Hermes local install troubleshooting

Use this when Hermes itself is installed and launches, but one or more toolsets are unexpectedly unavailable or partially broken on a local machine.

Typical triggers:
- `hermes doctor` shows a toolset missing even though the rest of Hermes is healthy.
- A tool works in principle but the runtime says a provider package is missing.
- The user asks to audit installed Python packages for Hermes and fill gaps.
- A config version warning appears after package or feature changes.

## Goals

1. Distinguish core dependency problems from optional-extra problems.
2. Install only the missing Python packages in the active Hermes `venv`.
3. Verify with real runtime checks, not only `pip install` success.
4. Migrate config if `hermes doctor` reports an outdated config version.

## Procedure

1. Identify the active Hermes virtualenv.
   - Prefer the Hermes entrypoint path and the Python it uses.
   - Example checks:
     - `which hermes`
     - `python -c 'import sys; print(sys.executable)'` from the Hermes venv if needed.

2. Run a baseline diagnostic.
   - `hermes doctor`
   - `hermes config check`
   - If the failure is a missing Python module, confirm it directly with:
     - `python - <<'PY'`
       `import importlib.util; print(importlib.util.find_spec("ddgs"))`
       `PY`

3. Compare declared dependencies to installed packages.
   - Read `pyproject.toml` in the Hermes repo.
   - Separate:
     - core `project.dependencies`
     - `project.optional-dependencies`
   - Compare against `pip list --format=json` from the active Hermes venv.
   - Normalize package names before diffing (`-` vs `_`) using `packaging.utils.canonicalize_name`, otherwise you can get false negatives.

4. Install only what is truly missing.
   - Use the Hermes venv explicitly, e.g. `/path/to/.venv/bin/python -m pip install ...`
   - Do not assume global `pip` or another interpreter is the right target.
   - If the user asked to fill all missing optional packages, install the actual missing optional extras from `pyproject.toml` plus the immediate runtime package that caused the failure.

5. Re-verify after install.
   - `python -m pip check`
   - `hermes doctor`
   - If the issue affected a specific tool, run a live check of that exact code path.

6. If `hermes doctor` reports config migration needed, run:
   - `hermes doctor --fix`
   - then `hermes config check`

## High-value pitfall

### `web_search` may fail because `ddgs` is missing even when Hermes itself is otherwise healthy

Observed durable pattern:
- `web_search` can be unavailable because the active Hermes venv lacks `ddgs`.
- `duckduckgo_search` may also be absent, but the operational fix is to install `ddgs` in the Hermes venv and then verify the actual search path.
- After install, confirm success with both:
  - `hermes doctor` showing `web` available
  - a direct runtime call through `tools.web_tools.web_search_tool(...)`

Do not stop at `pip install` success.

## Verification checklist

- `pip check` returns no broken requirements.
- `hermes doctor` shows the previously missing toolset as available.
- If config was outdated, `hermes config check` reports the current version.
- The exact failing tool now works in a live invocation.

## When not to save as a rule

Do not encode transient negative claims like "web_search is broken" or "browser tools do not work". Save the repair pattern instead: diagnose active venv, diff declared vs installed packages, install missing extras, run `doctor`, and verify the exact tool path.

## References

- `references/web-search-ddgs-repair.md` — concrete repair recipe for the `web_search`/`ddgs` case, including verification steps.
