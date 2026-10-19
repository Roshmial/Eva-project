import os
import subprocess

os.environ.setdefault("TG_MONITOR_INSTANCE_ID", "95")
os.environ.setdefault("TG_MONITOR_CONFIG_NAME", "daily_95")
os.environ.setdefault("TG_MONITOR_PROFILE_NAME", "profile_95")

PROJECT_DIR = '/home/hermes/workspace/TG-API'
TG_PYTHON = f'{PROJECT_DIR}/.venv/bin/python'

subprocess.run([TG_PYTHON, f'{PROJECT_DIR}/collect_daily_pipeline.py'], check=True, env=os.environ.copy())
