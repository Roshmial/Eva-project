#!/usr/bin/env python3
import os
import sys
from pathlib import Path

PYTHON = Path('/home/hermes/workspace/eva-data/.venv/bin/python')
SCRIPT = Path('/home/hermes/workspace/eva-data/backup_eva_hub.py')

if not PYTHON.exists():
    raise SystemExit(f'Eva Python environment not found: {PYTHON}')
os.execv(str(PYTHON), [str(PYTHON), str(SCRIPT), *sys.argv[1:]])
