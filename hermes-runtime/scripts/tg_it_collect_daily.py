import os
import runpy
import subprocess
import sys

os.environ.setdefault("TG_MONITOR_INSTANCE_ID", "95")
os.environ.setdefault("TG_MONITOR_CONFIG_NAME", "daily_95")
os.environ.setdefault("TG_MONITOR_PROFILE_NAME", "profile_95")

PROJECT_DIR = '/home/hermes/workspace/TG-API'
REFRESH_SCRIPT = '/home/hermes/workspace/eva-data/refresh_eva_hub.py'

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

runpy.run_path(f'{PROJECT_DIR}/collect_daily_pipeline.py', run_name='__main__')
subprocess.run([sys.executable, REFRESH_SCRIPT], check=True)
