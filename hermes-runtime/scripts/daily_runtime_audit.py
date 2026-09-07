#!/usr/bin/env python3
"""Run the runtime audit in its real backend contour on host 178."""
from __future__ import annotations

import subprocess
import sys

REMOTE_HOST = "178.104.207.89"
REMOTE_SCRIPT = "/home/hermes/workspace/hermes-web-mvp-react-8793/services/backend/daily_runtime_audit.py"
REMOTE_PYTHON = "/home/hermes/workspace/hermes-web-mvp-react-8793/services/backend/.venv/bin/python"

result = subprocess.run(
    ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", REMOTE_HOST, REMOTE_PYTHON, REMOTE_SCRIPT],
    text=True,
)
sys.exit(result.returncode)
