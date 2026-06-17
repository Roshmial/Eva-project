# Hermes Web MVP: tunnel-first fix pattern

Контекст класса задач:
- frontend открывали через `ssh -L 8790:127.0.0.1:8790 ...`;
- backend жил на отдельном порту `8788`;
- в UI проявлялось `Failed to fetch`, потому что браузер пользователя не видел backend по исходной схеме.

Что сработало:
- frontend переведён на same-origin API (`/api`);
- добавлен frontend proxy-слой на порту `8790`, который проксирует `/api` на backend `8788`;
- backend оставлен отдельно доступным для прямых smoke-проверок;
- дополнительно убран `favicon.ico` 404, чтобы не засорять console QA.

Что проверять в похожих задачах:
1. `curl` на frontend `/api/health`, `/api/service-info`, `/api/setup/status`.
2. Синтаксис Python/JS.
3. Smoke-тесты backend.
4. Headless Chromium с console errors и screenshot, если встроенный browser tool даёт пустой snapshot.
5. Видимые UI-строки: кнопки, фильтры, onboarding, admin blocks.

Продуктовый урок:
- для пользователя важнее не сценарий “чистой базы”, а явное управление текущей/новой базой;
- админка должна предлагать как минимум шаблонный CSV-импорт пользователей;
- AD/LDAP можно сначала выводить как подготовленный источник с required env и статусом configured/not configured, не выдавая это за завершённый sync.
