# Backend JSON error contract + model routing round-trip

Когда пользователь видит в Hermes Web фразу вида `Сервис вернул не JSON (500)`, не своди диагностику к frontend parse bug.

Паттерн проверки:

1. Разделить symptom и root cause.
- Сообщение про non-JSON — это frontend-симптом.
- Сначала проверить, не отдаёт ли backend HTML/plain-text на error path вместо `application/json`.

2. Проверить error contract живого backend.
- Сделать прямые HTTP-проверки не только на happy-path, но и на error-path:
  - несуществующий route -> ожидается JSON `404`;
  - неверный method -> ожидается JSON `405`;
  - если есть подозрение на route-level exception -> нужен глобальный JSON error handler для `Exception`/HTTP errors.
- Пока error-path не нормализован, frontend может ложно выглядеть сломанным, хотя первичная проблема в backend handler contract.

3. Для chat/model-routing acceptance не ограничиваться `/health`.
- Проверить login -> bootstrap -> create thread -> send message.
- В bootstrap отдельно подтвердить, что новый runtime helper действительно прокинут в route response. Типичный скрытый разрыв: helper уже считает `llm_routing`, а `/api/bootstrap` всё ещё возвращает старый ручной JSON без этого поля.
- Для новых chat controls проверить, что `model_preference` реально проходит до backend и сохраняется в `chat_tasks.request_policy_json`, а не теряется между frontend payload и очередью.

4. Если в проекте несколько живых портов/контуров, сначала сверить каноническую связку.
- Проверить, какой frontend реально обслуживает пользователя.
- Проверить, в какой backend ходит этот frontend (`vite.config.*`, proxy target, `HERMES_WEB_FRONTEND_BACKEND_BASE`).
- Если новый код виден на одном порту, а пользователь сидит на другом, не объявлять баг исправленным до перезапуска канонического контура.

5. Для local entrypoints предпочитать штатные скрипты проекта.
- После фикса перезапускать backend/frontend через канонические `run_*service*.sh`, а не через произвольный ad-hoc запуск.
- Затем повторить live HTTP-проверки уже на том порту, который использует фронт пользователя.

Минимальный acceptance для этого класса задач:
- `unittest`/smoke зелёный;
- frontend build зелёный;
- `/api/bootstrap` возвращает `llm_routing`;
- реальная отправка сообщения создаёт `chat_task` с ожидаемым `request_policy.model_preference`;
- error-path (`404/405`) возвращает JSON, а не HTML/plain-text.
