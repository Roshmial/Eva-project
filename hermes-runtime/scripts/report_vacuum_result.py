#!/usr/bin/env python3
import json
from pathlib import Path

p = Path('/home/hermes/workspace/decision-log-audit/vacuum-storage-result.json')
if not p.exists():
    print('Offline VACUUM не подтвердился: итоговый файл не создан. Нужна ручная проверка hermes-db-optimize-offline.service.')
    raise SystemExit(1)
r = json.loads(p.read_text(encoding='utf-8'))
mb = lambda n: round(int(n) / 1024 / 1024, 1)
if r.get('vacuum_exit_code') == 0 and r.get('integrity') == 'ok' and r.get('foreign_key_violations') == 0 and r.get('gateway_state') == 'active' and r.get('eva_timer_state') == 'active':
    print(f"Готово. Реальный SQLite VACUUM завершён: state.db уменьшен с {mb(r['before_bytes'])} до {mb(r['after_bytes'])} МБ, освобождено {mb(r['reclaimed_bytes'])} МБ. Целостность: ok; foreign key violations: 0; Gateway и Eva timer активны.")
else:
    print('VACUUM завершился с отклонением: ' + json.dumps(r, ensure_ascii=False))
    raise SystemExit(1)
