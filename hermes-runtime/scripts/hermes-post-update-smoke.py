#!/usr/bin/env python3
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

CONFIG_PATH = Path('/home/hermes/.hermes/config.yaml')
DEFAULT_CDP = 'http://127.0.0.1:9224'
TEST_URL = 'https://example.com'
TIMEOUT_DOCTOR = 90


def run(cmd, timeout=60, check=False):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(cmd)}\n{result.stdout}")
    return result.returncode, result.stdout.strip()


def read_cdp_url():
    try:
        import yaml
        with CONFIG_PATH.open() as f:
            cfg = yaml.safe_load(f) or {}
        return (((cfg.get('browser') or {}).get('cdp_url')) or DEFAULT_CDP).strip()
    except Exception:
        return DEFAULT_CDP


def http_json(url):
    import urllib.request
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))


def resolve_ws(cdp_url):
    version_url = cdp_url.rstrip('/') + '/json/version'
    payload = http_json(version_url)
    return payload['webSocketDebuggerUrl'], payload


def ok(flag):
    return 'OK' if flag else 'FAIL'


def main():
    started = time.time()
    report = {
        'version': {},
        'config': {},
        'gateway': {},
        'browser': {},
        'doctor': {},
        'overall_ok': False,
    }

    rc, out = run(['hermes', '--version'], timeout=30)
    report['version'] = {'ok': rc == 0, 'output': out}

    rc, out = run(['hermes', 'config', 'check'], timeout=60)
    report['config'] = {
        'ok': rc == 0 and 'Config version: 33' in out,
        'output_tail': '\n'.join(out.splitlines()[:12]),
    }

    rc, out = run(['hermes', 'gateway', 'status'], timeout=30)
    report['gateway'] = {'ok': rc == 0 and 'running' in out.lower(), 'output': out}

    cdp_url = read_cdp_url()
    report['browser']['cdp_url'] = cdp_url
    try:
        ws_url, version_payload = resolve_ws(cdp_url)
        report['browser']['cdp_reachable'] = True
        report['browser']['browser_version'] = version_payload.get('Browser', '')
        report['browser']['ws_url'] = ws_url

        rc, out = run(['agent-browser', '--cdp', ws_url, '--json', 'open', TEST_URL], timeout=90)
        open_payload = json.loads(out)
        report['browser']['open_ok'] = bool(open_payload.get('success'))

        rc, out = run(['agent-browser', '--cdp', ws_url, '--json', 'eval', 'window.location.href'], timeout=90)
        eval_payload = json.loads(out)
        report['browser']['href'] = (((eval_payload.get('data') or {}).get('result')) or '').strip()
        report['browser']['eval_ok'] = report['browser']['href'] == TEST_URL + '/'

        rc, out = run(['agent-browser', '--cdp', ws_url, '--json', 'snapshot', '-c'], timeout=90)
        snap_payload = json.loads(out)
        snapshot_text = (((snap_payload.get('data') or {}).get('snapshot')) or '').strip()
        report['browser']['snapshot_ok'] = 'Example Domain' in snapshot_text
        report['browser']['snapshot_excerpt'] = snapshot_text[:200]

        shot_path = '/tmp/hermes-post-update-smoke.png'
        rc, out = run(['agent-browser', '--cdp', ws_url, 'screenshot', shot_path], timeout=90)
        report['browser']['screenshot_ok'] = rc == 0 and Path(shot_path).exists() and Path(shot_path).stat().st_size > 0
        report['browser']['screenshot_path'] = shot_path if report['browser']['screenshot_ok'] else ''

        report['browser']['ok'] = all([
            report['browser']['cdp_reachable'],
            report['browser']['open_ok'],
            report['browser']['eval_ok'],
            report['browser']['snapshot_ok'],
            report['browser']['screenshot_ok'],
        ])
    except Exception as e:
        report['browser']['ok'] = False
        report['browser']['error'] = repr(e)

    rc, out = run(['bash', '-lc', f'timeout {TIMEOUT_DOCTOR} hermes doctor | tail -n 40'], timeout=TIMEOUT_DOCTOR + 30)
    report['doctor'] = {
        'ok': rc == 0 and 'All checks passed!' in out,
        'output_tail': out,
        'timeout_seconds': TIMEOUT_DOCTOR,
    }

    report['overall_ok'] = all([
        report['version'].get('ok'),
        report['config'].get('ok'),
        report['gateway'].get('ok'),
        report['browser'].get('ok'),
        report['doctor'].get('ok'),
    ])

    print('Hermes post-update smoke')
    print(f"version: {ok(report['version']['ok'])} | {report['version']['output']}")
    print(f"config: {ok(report['config']['ok'])} | config v33 expected")
    print(f"gateway: {ok(report['gateway']['ok'])} | {report['gateway']['output']}")
    print(f"browser: {ok(report['browser'].get('ok', False))} | cdp={cdp_url} | href={report['browser'].get('href', '')}")
    print(f"doctor: {ok(report['doctor']['ok'])} | timeout={TIMEOUT_DOCTOR}s")
    print(f"overall: {ok(report['overall_ok'])} | elapsed={round(time.time() - started, 2)}s")
    print('\nJSON report:')
    print(json.dumps(report, ensure_ascii=False, indent=2))

    sys.exit(0 if report['overall_ok'] else 1)


if __name__ == '__main__':
    main()
