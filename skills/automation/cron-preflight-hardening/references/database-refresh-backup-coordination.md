# Database refresh and backup coordination

Use this recipe when Hermes cron, a systemd timer, or a collector maintains an analytical SQLite/DuckDB hub.

## Separate the responsibilities

Keep collection, analytical refresh, context sync, and backup as separate entry points:

1. Collector updates only its source checkpoint and raw data.
2. Refresh rebuilds the analytical database from source systems.
3. Context sync reads the last committed live database.
4. Backup snapshots only the committed live database.

Do not call a full refresh at the end of every collector when a separate timer already owns refresh. This couples failure domains and can keep a long rebuild running continuously.

## Schedule from completion

For a heavy oneshot service, use a timer based on inactivity:

```ini
[Timer]
OnBootSec=2m
OnUnitInactiveSec=1h
Unit=eva-hub-refresh.service
Persistent=true
```

`OnUnitInactiveSec` starts the interval after completion. Avoid `OnUnitActiveSec` when runtime can exceed the interval, because the next activation may already be overdue when the current run exits.

## Serialize refresh and backup

Use one lock path for every writer or snapshotter.

Systemd refresh:

```ini
[Service]
Type=oneshot
ExecStart=/usr/bin/flock -x /srv/app/data/hub.lock /srv/app/.venv/bin/python /srv/app/refresh.py
```

Python cron launcher that replaces itself with the project interpreter:

```python
import fcntl
import os
from pathlib import Path

lock_file = Path('/srv/app/data/hub.lock').open('a+')
os.set_inheritable(lock_file.fileno(), True)
fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
os.execv('/srv/app/.venv/bin/python', ['/srv/app/.venv/bin/python', '/srv/app/backup.py'])
```

The descriptor must be inheritable: otherwise `execv` closes it and the backup runs unlocked.

## Bound memory during rebuilds

Avoid this shape for large stores:

```python
message_rows = [dict(row) for row in cursor.execute('select ...')]
messages = [transform(row) for row in message_rows]
```

It holds payload text twice. Instead:

1. Compute session/status metadata with SQL aggregates or window functions.
2. Fetch message rows with `fetchmany(1000)` or another measured batch size.
3. Transform and insert one batch at a time.
4. Release the batch before fetching the next one.

Before replacing an existing algorithm, compare old and new derived statuses on the full source without copying content into both structures. Require zero mismatches.

## Preserve the live database

Rebuild to a staging path, validate it, close every connection, then use an atomic replace:

1. Remove only a stale staging file.
2. Build `hub.next.duckdb`.
3. Run integrity/count checks.
4. Close the DuckDB connection.
5. Replace `hub.duckdb` atomically.

An OOM, cancellation, or full disk must leave the previous live database untouched.

## Verification

After changes:

- run the refresh through its real systemd unit and record peak RSS;
- run backup through `hermes cron run`, not only the project script;
- confirm the durable run is `completed`;
- recompute the backup checksum and compare it with the manifest;
- verify the stable `latest` path resolves to the dated backup;
- confirm the timer's next activation appears only after the service becomes inactive;
- run context sync and inspect the updated target artifact.
