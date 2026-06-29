---
name: runtime-bootstrap-hygiene
description: Keep Python backends import-safe by separating module import from runtime bootstrap, lazy-loading optional heavy dependencies, and stabilizing smoke tests.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [python, backend, testing, bootstrap, import-safety, smoke-tests, runtime]
---

# Runtime Bootstrap Hygiene

## When to use

Use this skill when a Python backend or service:

- aborts or hangs after tests finish;
- reproduces failures on plain module import (`exec_module`, `import app`, `python -m unittest`) rather than only inside product logic;
- starts schedulers, workers, DB migrations, recovery loops, or network listeners during import;
- eagerly imports optional heavy libraries (document, image, HTML, PDF, ML, browser stacks) even when the current path does not need them;
- needs stable smoke tests that import the app without booting the full runtime.

## Core idea

Module import and runtime bootstrap are different phases.

Import should define code and build lightweight objects. Bootstrap should perform side effects: DB init, migrations, recovery, background threads, schedulers, listeners, caches, warmups.

If import performs runtime side effects, test harnesses become noisy and teardown failures become hard to localize.

## Default approach

### 1. Prove whether the problem is import-time

Do not start by patching tests.

First isolate three reproductions:

1. plain import / `exec_module(app.py)`;
2. one targeted test that should be logically simple;
3. a direct-path probe that avoids unrelated routes.

If plain import already reproduces the crash, treat it as import/bootstrap hygiene, not as a product regression.

### 2. Find import-time side effects

Look for code executed at module bottom or top-level initialization such as:

- `init_db()`
- migrations / seeders / backfills
- recovery of interrupted tasks
- `start_scheduler()` / `thread.start()` / worker loops
- listener startup
- cache warmups
- loading optional binary-heavy libraries at import time

### 3. Split import from bootstrap

Prefer an explicit bootstrap gate.

Patterns that usually work:

- `IMPORT_BOOTSTRAP_ENABLED = os.getenv("...") != "0"`
- `create_app()` returns the Flask/FastAPI app without side effects
- `bootstrap_runtime()` performs DB init, recovery, scheduler startup, worker startup
- tests import with bootstrap disabled, then call only the minimum setup they actually need

Keep production default behavior unchanged unless the user asked for a broader refactor.

### 4. Lazy-load optional heavy dependencies

If a library is only needed for specific export/parsing paths, do not import it at module load.

Typical candidates:

- PDF / office libs
- image libs
- HTML parsing stacks
- report generators
- browser / rendering stacks

Use loader helpers that return `None` on missing dependency and let the runtime path raise a specific product error only when that feature is actually used.

### 5. Keep test harness explicit

In smoke tests:

- disable import bootstrap via env;
- import the module;
- explicitly call only the minimal setup needed, such as `init_db()` or recovery of interrupted tasks;
- do not rely on hidden side effects from import.

## Verification checklist

A fix is not done until all of these are true:

1. plain import with bootstrap disabled exits cleanly;
2. targeted unittest/pytest path exits with code 0, not just `OK` before abort;
3. syntax check / compile check passes;
4. production default path is unchanged or consciously adjusted;
5. if code was synced to live, distinguish clearly between:
   - files updated;
   - remote compile passed;
   - live process restarted;
   - live health checked.

## Pitfalls

- Do not treat post-test abort as a business-logic failure if assertions already passed.
- Do not claim a live restart happened unless it actually happened.
- Do not fix only by suppressing tests; first isolate whether import itself is dirty.
- Do not keep eager imports of optional heavy libraries in the main module just because they are convenient.
- Do not let tests depend on implicit import-time side effects.

## Good minimal pattern

1. Add bootstrap env guard.
2. Move import-time side effects behind the guard.
3. Convert optional heavy imports to lazy loaders.
4. Update smoke tests to opt out of bootstrap and call minimal init explicitly.
5. Verify plain import + targeted test + live/runtime status separately.

## References

- `references/hermes-web-import-bootstrap-and-abort.md` — concrete reproduction and fix pattern from Hermes Web backend.
