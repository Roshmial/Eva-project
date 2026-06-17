#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REFRESH = Path('/home/hermes/workspace/eva-data/refresh_eva_hub.py')
LOG_DIR = Path('/home/hermes/workspace/eva-data/logs')
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / 'eva_hub_refresh.log'


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    proc = subprocess.run([sys.executable, str(REFRESH)], capture_output=True, text=True)
    entry = {
        'ts': now_iso(),
        'exit_code': proc.returncode,
        'stdout': proc.stdout.strip(),
        'stderr': proc.stderr.strip(),
    }
    with LOG_PATH.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + '\n')
    if proc.returncode == 0:
        return 0
    print(json.dumps(entry, ensure_ascii=False), file=sys.stdout)
    return proc.returncode


if __name__ == '__main__':
    raise SystemExit(main())
