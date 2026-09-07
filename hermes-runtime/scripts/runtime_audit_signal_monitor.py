#!/usr/bin/env python3
"""Wake triage only when the remote runtime audit has actual signals."""
from __future__ import annotations

import subprocess

result = subprocess.run(
    ["python3", "/home/hermes/.hermes/scripts/daily_runtime_audit.py"],
    text=True,
    capture_output=True,
)
if result.returncode:
    print("audit-unavailable:" + (result.stdout + result.stderr).strip())
    raise SystemExit(result.returncode)
text = result.stdout.strip()
print("no-signals" if "Сигналов по ошибкам и некорректной отработке не найдено." in text else text)
