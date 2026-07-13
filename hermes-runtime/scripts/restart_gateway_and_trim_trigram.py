from __future__ import annotations

import os
import sqlite3
import subprocess
import time
from pathlib import Path

DB = Path('/home/hermes/.hermes/state.db')
SERVICE = 'hermes-gateway.service'


def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return (p.stdout or p.stderr).strip()


def table_count(conn: sqlite3.Connection) -> int:
    return conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE name LIKE 'messages_fts_trigram%'"
    ).fetchone()[0]


def main() -> None:
    before = DB.stat().st_size if DB.exists() else 0
    run(['systemctl', '--user', 'stop', SERVICE])
    try:
        conn = sqlite3.connect(str(DB), timeout=30, isolation_level=None)
        try:
            conn.execute('PRAGMA busy_timeout=30000')
            conn.execute('BEGIN IMMEDIATE')
            for trig in ('messages_fts_trigram_insert', 'messages_fts_trigram_delete', 'messages_fts_trigram_update'):
                conn.execute(f'DROP TRIGGER IF EXISTS {trig}')
            conn.execute('DROP TABLE IF EXISTS messages_fts_trigram')
            conn.commit()
            conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            conn.execute('VACUUM')
            conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            after_tables = table_count(conn)
        finally:
            conn.close()
    finally:
        run(['systemctl', '--user', 'start', SERVICE])
    after = DB.stat().st_size if DB.exists() else 0
    print(f'Gateway restarted; trigram tables remaining: {after_tables}')
    print(f'state.db before: {before} bytes')
    print(f'state.db after:  {after} bytes')
    print(f'saved: {before - after} bytes')


if __name__ == '__main__':
    main()
