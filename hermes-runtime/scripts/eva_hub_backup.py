#!/usr/bin/env python3
import fcntl
import os
import sys
from pathlib import Path

PYTHON = Path('/home/hermes/workspace/eva-data/.venv/bin/python')
SCRIPT = Path('/home/hermes/workspace/eva-data/backup_eva_hub.py')
LOCK_PATH = Path('/home/hermes/workspace/eva-data/eva_hub.lock')

if not PYTHON.exists():
    raise SystemExit(f'Eva Python environment not found: {PYTHON}')

# Serialize backup with the staging refresh. The inherited descriptor keeps
# the exclusive lock held after exec until the backup process exits.
lock_file = LOCK_PATH.open('a+')
os.set_inheritable(lock_file.fileno(), True)
fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
os.execv(str(PYTHON), [str(PYTHON), str(SCRIPT), *sys.argv[1:]])
