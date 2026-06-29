# UI DB contour split: live-check pattern

Use this note when a web UI is reachable and healthy, but DB-level fixes on another host do not change what the user sees.

## Failure pattern

You inspect and even clean a PostgreSQL contour on one host, then assume the visible UI reflects that cleanup. Later it turns out the current live UI is actually backed by a local DuckDB runtime contour under a different service tree.

## What to prove before claiming success

1. Which host/port serves the visible UI.
2. Which systemd unit backs the UI-facing backend.
3. Which DB driver that service is actually using.
4. Which concrete DB path or DSN is live for that service.
5. Only then interpret DB cleanup as a UI fix.

## Fast evidence cues

- `systemctl cat <unit>` and wrapper scripts may show only part of the truth.
- Check the backend code/env for the real DB env variable names, not guessed names.
- If the app supports both DuckDB and PostgreSQL, verify the effective driver first.
- Compare live runtime users/rows with the UI-visible account list or login behavior; mismatches often reveal the wrong DB contour.

## Reporting rule

When writing the conclusion, say explicitly:
- which contour was cleaned;
- which contour was actually serving the UI;
- whether the UI verification was done on the same contour or only inferred.
