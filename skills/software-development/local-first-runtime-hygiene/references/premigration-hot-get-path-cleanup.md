# Предмиграционный cleanup hot GET-paths в local-first runtime

Когда применять:
- перед крупным переездом или сменой контура, если UI/backend уже работает, но есть latency и скрытая тяжёлая работа;
- когда хочется снять дорогие read-path bottleneck'и без новой инфраструктуры.

Типовые smell-сигналы:
- subprocess, bridge или внешний CLI на обычном GET-path;
- write-on-GET (`sync_*`, registry refresh, bootstrap side effect);
- широкий reference payload там, где endpoint'у нужен узкий набор данных;
- N+1 при сериализации списков (`row -> helper -> дополнительные SELECT` на каждую запись);
- admin/overview endpoint, который на каждый reload повторяет дорогую синхронизацию.

Практический порядок работы:
1. Снять latency по основным public/auth/admin endpoint'ам и выделить top offenders.
2. Для каждого дорогого GET-path отдельно проверить:
   - есть ли subprocess/cron bridge;
   - есть ли write-on-GET;
   - не строится ли полный runtime reference view вместо узкого dataset;
   - нет ли N+1 на списках jobs/items.
3. Чинить в таком порядке:
   - убрать subprocess с hot read-path и заменить локальными данными или коротким TTL-cache;
   - вынести write-on-GET из обычного reload-path;
   - сузить payload до реально нужных datasets;
   - батчить owners/ACL/subscriptions/counts вместо per-row helper calls.
4. После правки обязательно прогнать:
   - smoke/regression;
   - синтаксическую проверку;
   - restart сервиса;
   - live latency probe;
   - обновление runbook и decision-log.

Проверенные полезные паттерны:
- `/api/health` должен быть чистым local liveness/readiness-check, без cron subprocess.
- Для cron bridge на overview/admin/jobs допустим короткий TTL-cache, но не прямой вызов на каждый reload.
- Узкие endpoint'ы вроде `feedback/reasons` и `jobs/meta` не должны собирать весь runtime reference payload.
- `/api/admin/user-sources` и похожие admin GET-paths не должны делать write-on-GET.

Что считать успехом:
- latency снижается на live или live-like audit path, а не только "по коду стало красивее";
- endpoint остаётся рабочим, даже если bridge/path вне его критичного контракта временно недоступен;
- правило зафиксировано в runbook, чтобы регресс не вернулся после следующего цикла.
