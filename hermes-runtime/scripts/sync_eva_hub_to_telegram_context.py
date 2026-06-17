#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb

LOCK_RETRY_SECONDS = 75
LOCK_RETRY_DELAY = 5

DB_PATH = Path('/home/hermes/workspace/eva-data/eva_hub.duckdb')
BACKUP_DB_PATH = Path('/home/hermes/workspace/eva-data/backups/eva_hub_latest.duckdb')
OUTPUT_PATH = Path('/home/hermes/.hermes/memories/EVA_TELEGRAM.md')
MAX_INTERACTION_BULLETS = 6
MAX_DECISIONS = 5


def _extract_bullets_from_section(markdown: str, heading: str) -> list[str]:
    lines = markdown.splitlines()
    inside = False
    bullets: list[str] = []
    for line in lines:
        if line.startswith('## '):
            inside = line.strip() == f'## {heading}'
            continue
        if not inside:
            continue
        stripped = line.strip()
        if stripped.startswith('- '):
            bullets.append(stripped[2:].strip())
        elif stripped.startswith('## '):
            break
    return bullets


def _normalize_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text or '').strip()
    return text.replace('`', "'")


def _connect_with_retry() -> duckdb.DuckDBPyConnection:
    deadline = time.time() + LOCK_RETRY_SECONDS
    last_error: Exception | None = None
    while True:
        try:
            return duckdb.connect(str(DB_PATH), read_only=True)
        except duckdb.IOException as exc:
            last_error = exc
            message = str(exc)
            if 'Could not set lock on file' not in message or time.time() >= deadline:
                raise
            time.sleep(LOCK_RETRY_DELAY)
        except Exception as exc:
            last_error = exc
            raise

    if last_error:
        raise last_error
    raise RuntimeError('unreachable')


def _read_context_from_connection(con: duckdb.DuckDBPyConnection) -> tuple[object | None, list[tuple]]:
    interaction_row = con.execute(
        "select content, imported_at from eva.interaction_notes_current limit 1"
    ).fetchone()
    decision_rows = con.execute(
        """
        select entry_date, topic
        from eva.decision_log_latest
        order by entry_date desc, imported_at desc, topic
        limit ?
        """,
        [MAX_DECISIONS],
    ).fetchall()
    return interaction_row, decision_rows


def build_context() -> str:
    source_label = 'live'
    try:
        con = _connect_with_retry()
        interaction_row, decision_rows = _read_context_from_connection(con)
        con.close()
    except Exception as exc:
        if _is_lock_error(exc) and BACKUP_DB_PATH.exists():
            con = duckdb.connect(str(BACKUP_DB_PATH), read_only=True)
            interaction_row, decision_rows = _read_context_from_connection(con)
            con.close()
            source_label = 'backup'
        else:
            raise

    interaction_content = interaction_row[0] if interaction_row else ''
    imported_at = interaction_row[1] if interaction_row else None
    memory_bullets = _extract_bullets_from_section(interaction_content, 'Что держать в memory')
    memory_bullets = [_normalize_text(x) for x in memory_bullets[:MAX_INTERACTION_BULLETS] if _normalize_text(x)]

    lines: list[str] = []

    if imported_at:
        lines.append(f'Контекст из eva_hub ({source_label}), импорт interaction-notes: {imported_at}')

    for bullet in memory_bullets:
        lines.append(f'- {bullet}')

    for entry_date, topic in decision_rows:
        topic_text = _normalize_text(str(topic))
        lines.append(f'- decision-log [{entry_date}]: {topic_text}')

    lines.append(f'Обновлено: {datetime.now(timezone.utc).isoformat()}')
    return '\n'.join(lines).strip() + '\n'


def _is_lock_error(exc: Exception) -> bool:
    return isinstance(exc, duckdb.IOException) and 'Could not set lock on file' in str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description='Синхронизирует компактный Telegram-контекст из Eva Hub в Hermes memories.')
    parser.add_argument('--check', action='store_true', help='Только проверить, отличается ли сгенерированный файл.')
    parser.add_argument('--verbose', action='store_true', help='Печатать статус в stdout.')
    args = parser.parse_args()

    try:
        content = build_context()
    except Exception as exc:
        if _is_lock_error(exc) and OUTPUT_PATH.exists() and not args.check:
            if args.verbose:
                print(f'skipped lock on {DB_PATH}')
            return 0
        raise

    current = OUTPUT_PATH.read_text(encoding='utf-8') if OUTPUT_PATH.exists() else None
    changed = current != content

    if args.check:
        if args.verbose:
            print('changed' if changed else 'unchanged')
        return 1 if changed else 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if changed:
        OUTPUT_PATH.write_text(content, encoding='utf-8')
        if args.verbose:
            print(f'updated {OUTPUT_PATH}')
    else:
        if args.verbose:
            print(f'unchanged {OUTPUT_PATH}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
