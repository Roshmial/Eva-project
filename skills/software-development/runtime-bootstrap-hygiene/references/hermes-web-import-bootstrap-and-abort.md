# Hermes Web: import-time bootstrap vs smoke-test abort

## Symptom

Targeted backend tests reached `OK` but the Python process still exited with:

- `terminate called without an active exception`
- `Fatal Python error: Aborted`

Important distinction: assertions passed. The failure was post-test teardown noise.

## Isolation path that worked

1. Reproduce with one targeted unittest.
2. Reproduce on plain `exec_module(app.py)` without running product logic.
3. Reduce import-time noise by lazy-loading optional heavy dependencies.
4. Re-check plain import.
5. Inspect what still executes at import time.
6. Find module-bottom runtime bootstrap calls.

## Root cause found

`services/backend/app.py` executed runtime side effects during import:

- `init_db()`
- `recover_interrupted_chat_tasks()`
- `start_scheduler()`
- `start_chat_processor()`

That made the module import itself stateful and unsafe for smoke harnesses.

## Fix pattern used

### 1. Add import bootstrap guard

Use an env gate such as:

`IMPORT_BOOTSTRAP_ENABLED = os.getenv("HERMES_WEB_IMPORT_BOOTSTRAP_ENABLED", "1") != "0"`

Then run module-bottom bootstrap only when the flag is enabled.

### 2. Make smoke harness explicit

Before importing the backend in tests:

- set `HERMES_WEB_IMPORT_BOOTSTRAP_ENABLED=0`
- import the module
- call only the minimum setup explicitly, in this case:
  - `init_db()`
  - `recover_interrupted_chat_tasks()`

### 3. Lazy-load optional heavy dependencies

Useful cleanup that reduced noise and import cost:

- PyMuPDF / `fitz`
- `python-docx`
- `python-pptx`
- `openpyxl`
- `PIL`
- `markdown`
- `BeautifulSoup`
- `reportlab`

## Verification shape

Treat these as separate checks:

1. local plain import with bootstrap disabled exits cleanly;
2. targeted unittest exits with code 0;
3. remote file sync is confirmed by hash match;
4. remote `py_compile` passes;
5. live health is checked;
6. live restart is only claimed if it actually happened.

## Operational note

If restart is blocked by the runtime/gateway you are currently inside, record that honestly. Do not upgrade "files synced + compile ok + current health ok" into "restarted and verified".
