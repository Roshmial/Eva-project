# Doctor regression on large `state.db` after update

## Symptom

После update `hermes doctor` снова начинает выглядеть зависшим. Типичный visible marker:
- doctor доходит до строки `~/.hermes/state.db exists (N sessions)`;
- дальше долго нет прогресса;
- при прямом вызове `_db_opens_cleanly(Path('~/.hermes/state.db'))` процесс уходит в долгую паузу.

## Confirmed root cause from this session

На live DB размером около `2.08 GB` (`/home/hermes/.hermes/state.db`) в `hermes_state._db_opens_cleanly()` снова выполнялся полный `PRAGMA integrity_check`.

Для этой DB:
- schema parse и обычное чтение `sessions` были быстрыми;
- rolled-back write probe нужен и должен оставаться;
- именно `integrity_check` делал `hermes doctor` практически непригодным как быстрый post-update smoke-check.

## Working remediation

Вернуть size-aware shortcut в `_db_opens_cleanly()`:
- для DB `<= 512 MiB` оставить `PRAGMA integrity_check`;
- для больших DB пропускать полный integrity sweep;
- обязательно сохранить:
  - `PRAGMA journal_mode` как schema-parse probe;
  - `SELECT COUNT(*) FROM sessions` как canonical read;
  - rolled-back write probe через `sessions/messages` для проверки FTS write health.

## Regression test pattern

Добавить test, который:
- строит healthy temporary state DB;
- monkeypatch-ит `Path.stat()` так, чтобы DB выглядела > 512 MiB;
- monkeypatch-ит `sqlite3.connect()` wrapper-ом, который падает при вызове `PRAGMA integrity_check`;
- ожидает, что `_db_opens_cleanly()` вернёт `None` и не вызовет `integrity_check`.

Это защищает именно от post-update regression, когда код снова возвращает `integrity_check` в default-path.

## Verification sequence

После patch не останавливаться на diff:
1. `pytest -q tests/test_state_db_malformed_repair.py`
2. `python3 -m py_compile hermes_state.py hermes_cli/doctor.py tests/test_state_db_malformed_repair.py`
3. прямой вызов `_db_opens_cleanly()` на реальной `state.db`
4. `timeout 120 hermes doctor`

## Session-specific concrete values

- live DB path: `/home/hermes/.hermes/state.db`
- observed size: `2084925440` bytes
- after patch `_db_opens_cleanly(...)` returned `None` in about `0.018s`
- after patch `hermes doctor` completed with `All checks passed!`
