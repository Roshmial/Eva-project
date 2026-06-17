# DuckDB auth hot-path и systemd port conflicts в live Hermes Web runtime

Когда local/web runtime использует DuckDB и user services через `systemd --user`, нестабильные `503 auth_backend_temporarily_unavailable` после успешного login могут быть не фронтовым дефектом, а результатом двух скрытых классов проблем.

## 1. Не пиши в supposedly read-only auth-path без крайней необходимости

Симптомы:
- `POST /api/auth/login` проходит;
- следующий `GET /api/auth/session` или `POST /api/threads` иногда даёт `503 auth_backend_temporarily_unavailable`;
- frontend показывает баннеры вроде `Сервис вернул не JSON (500)` или выглядит как будто сломан bootstrap.

Практический вывод:
- `require_auth()` и соседний session middleware не должны делать частые write-операции по умолчанию;
- обновление `last_seen_at`, heartbeat и maintenance cleanup нельзя держать на каждом request в многопользовательском DuckDB-контуре;
- для live acceptance сначала делай auth-path максимально read-only, а heartbeat выноси в редкий отдельный update или best-effort path, который не валит основной запрос.

Если write-path всё же нужен:
- оборачивай его как best-effort;
- `duckdb.TransactionException` на touch/cleanup не должен превращать валидный токен в `503`.

## 2. Не делай DDL на каждом новом DuckDB connection

Скрытая ловушка:
- `duckdb.connect(...)` в каждом request плюс `CREATE SCHEMA IF NOT EXISTS ...` на каждом открытии соединения создаёт лишнюю конкурентную нагрузку и может маскироваться под auth/runtime instability.

Устойчивый паттерн:
- schema/bootstrap делай один раз на процесс;
- request-path должен открывать соединение и переключать schema без повторного DDL;
- для live multi-user acceptance проверь именно login -> auth/session -> create_thread -> send_message, а не только `/health` и unit tests.

## 3. Не смешивай manual runtime и systemd-owned ports

Симптомы:
- порт отвечает, но unit в `systemd --user` в restart loop;
- live verdict получается по случайному process owner, а не по каноническому runtime;
- после ручного `python app.py` или shell-скрипта сервис выглядит живым, но user unit считает, что всё сломано.

Правило:
- если порт штатно управляется через `systemd --user`, перед live acceptance сначала сверяй owner процесса и unit status;
- не поднимай параллельный manual backend поверх того же порта без явной причины;
- если всё же подняла manual runtime для локальной проверки, перед финальным verdict верни канонический owner процесса и только потом повторяй probes.

## 4. Какой live probe считать минимально достаточным

Для concurrency/auth acceptance на DuckDB минимальный практический проход такой:
1. health/service-info;
2. login известным acceptance-аккаунтом;
3. `GET /api/auth/session` тем же token;
4. `POST /api/threads`;
5. параллельные `POST /api/threads/<id>/messages` от нескольких пользователей.

Если health зелёный, а шаги 3–5 падают, не объявляй контур готовым по одному `/health`.

## 5. Что сохранять как durable lesson

Сохраняй не факт конкретного `503`, а класс вывода:
- для DuckDB-backed web runtime auth hot-path должен быть read-mostly;
- schema init не должна жить внутри каждого request connection;
- final live acceptance нужно делать на каноническом process owner, а не на случайном manual процессе поверх systemd-порта.
