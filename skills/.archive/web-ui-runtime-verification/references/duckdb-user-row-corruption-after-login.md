# DuckDB user-row corruption after successful login

Когда использовать:
- `POST /api/auth/login` проходит с `200`.
- Сразу после логина почти все auth-protected read-endpoint'ы одинаково падают в `503 auth_backend_temporarily_unavailable`.
- Визуально это легко маскируется под сломанный boot-path, Promise.all или frontend session restore.

Типичный симптом:
- login успешен;
- `/api/me`, `/api/bootstrap`, `/api/files`, `/api/threads`, `/api/jobs/meta` валятся одинаково;
- при этом public/startup surface жив, а token/session уже выданы.

Что проверять первым делом:
1. Не спорить с экраном и не лечить frontend вслепую.
2. Сделать прямые SQL-probes в DuckDB:
   - `select * from users where id=<current_user_id>`
   - `select ... from sessions s join users u on u.id=s.user_id where s.token=? and s.revoked_at is null`
3. Если именно чтение конкретной user-row или join падает на `IO Error: Corrupt database file: computed checksum ...`, root cause — точечная data corruption.

Практический repair-path:
1. Остановить временные runtime-процессы, которые держат эту БД.
2. Обязательно сделать backup исходного `.duckdb`.
3. Поднять свежую schema-compatible repair DB.
4. Перелить в неё содержимое всех таблиц из исходной БД.
5. Повреждённую user-row не читать из старой БД, а пересобрать отдельно валидными значениями.
6. Подменить рабочую локальную БД repaired-версией.
7. После замены заново прогнать live acceptance:
   - login
   - `/api/me`
   - `/api/bootstrap`
   - `/api/files`
   - `/api/threads`
   - `/api/jobs/meta`
   - UI navigation до нужного экрана (`Задачи` или другой целевой экран)

Важно:
- Не путать этот кейс с DuckDB write-contention на auth hot path. Там обычно плавают ошибки параллельных read-эндпоинтов, но прямое чтение user/session rows само по себе не обязано падать на checksum corruption.
- Если `login=200`, а все protected reads одинаково ломаются, проверка данных user/session часто даёт больше сигнала, чем ещё один раунд frontend-debugging.

Минимум, который надо зафиксировать пользователю:
- это не обязательно дефект boot-path;
- причина может сидеть в локальной БД;
- backup сделан до repair;
- после repair тот же live auth flow реально перепроверен end-to-end.
