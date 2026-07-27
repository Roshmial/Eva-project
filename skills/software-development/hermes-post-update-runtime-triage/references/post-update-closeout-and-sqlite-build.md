# Post-update runtime triage: live remediation notes

## Backup false-positive after update

Symptom class:
- user reports backup error after update;
- backup artifact actually exists;
- logs contain `printf: --: invalid option`.

Interpretation:
- investigate update log, cron output, and journal together;
- if the backup file exists, treat this as shell-wrapper/logging failure, not backup loss.

## SQLite 3.51.3+ closeout without sudo

When `hermes doctor` still warns after wheel-based override:
1. try wheel path first (`pysqlite3` / `pysqlite3-binary`);
2. if wheel only gives `3.51.1`, download official amalgamation for the exact target release (for example `3510300` for `3.51.3`);
3. unpack `pysqlite3` source tarball and copy `sqlite3.c` + `sqlite3.h` into the source root so setup links the bundled SQLite instead of system `libsqlite3`;
4. if Python headers are missing and no root is available, use:
   - `apt download python3.12-dev libpython3.12-dev`
   - `dpkg-deb -x ... extract/`
   - compile with `CFLAGS='-I<extract>/usr/include -I<extract>/usr/include/python3.12 -I<extract>/usr/include/x86_64-linux-gnu/python3.12'`
5. reinstall the built package into Hermes `.venv`;
6. verify:
   - `.venv/bin/python` returns `sqlite3.sqlite_version == 3.51.3`;
   - `sqlite3.__file__` points to `site-packages/pysqlite3/...`;
   - `hermes doctor` reports `✓ SQLite 3.51.3`.

## npm closeout beyond plain install

If user asks to close all tails, do not stop at `agent-browser installed`.

Checklist:
- `npm audit --json`
- `npm ls concurrently shell-quote` or other affected chain
- workspace-level version fix if needed
- `npm install-scripts ls --json`
- `npm install-scripts approve --all`
- rerun `npm install`
- rerun `hermes doctor`

Live example:
- vulnerability path: `concurrently -> shell-quote`
- practical fix: move workspace dependency from `concurrently 10.0.3` to `9.2.4`
- result: `npm audit` returns zero vulnerabilities.
