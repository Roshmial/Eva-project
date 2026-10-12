# React session restore and JSON contract

Когда применять:
- пользователь говорит, что авторизация "сама слетает" после reload или просто на ровном месте;
- frontend иногда показывает сырой текст `Сервис вернул не JSON` или даже HTML fragment;
- в машине одновременно живут несколько похожих Hermes Web runtime-контуров.

## 1. Сначала отдели реальное истечение сессии от ложного logout

Симптом-ловушка:
- `/api/auth/session` может быть рабочим;
- токен в `localStorage` ещё живой;
- но frontend всё равно очищает token и возвращает login screen.

Частая причина:
- boot-path делает `restoreSession()`;
- затем запускает большой `loadCoreState()`;
- любой побочный `404/500` на вторичном endpoint-е валит общий `catch`;
- `catch` без разбора делает `setStoredToken('')` / `setToken(null)`.

Практический fix:
- чистить token только на явных auth-кодах вроде `invalid_token` / `auth_required`;
- вторичные bootstrap-ресурсы (`files`, `jobs meta`, отдельные reference/load-public вызовы) переводить на `Promise.allSettled(...)` или deferred load;
- app shell и базовый screen не должны зависеть от неключевых загрузок.

## 2. Public/startup запросы тоже должны идти через JSON-safe слой

Анти-паттерн:
- `fetch(...).then(res => res.json())` для `service-info`, `setup/status` и похожих startup routes;
- при HTML fallback или proxy drift пользователь получает сырой parse error.

Надёжный путь:
- использовать тот же безопасный helper, что и для остальных API-запросов;
- на non-JSON response отдавать продуктовую ошибку вроде `Сервис временно ответил некорректно. Обнови экран и повтори действие.`;
- не показывать пользователю сырой `<html>` snippet.

## 3. Проверяй не только код, но и живой процесс на порту

Если в системе несколько checkout/контуров, обязательный порядок такой:
1. Найти PID, который реально слушает нужный порт.
2. Снять `cwd` процесса.
3. Снять `cmdline`.
4. Снять `HERMES_WEB_*` env через `/proc/<pid>/environ`.
5. Только после этого править и перезапускать нужное дерево.

Это помогает не перепутать:
- новый checkout vs старый checkout;
- manual runtime vs уже живущий процесс;
- правильный backend/frontend contour vs визуально похожий, но нецелевой.

## 4. Что отдельно подтвердить после фикса

Минимальный runtime-pass:
- backend health на целевом порту;
- same-origin `/api/service-info` возвращает JSON;
- process env реально содержит нужные значения, например session TTL и лимиты reasoning;
- reload больше не чистит token из-за вторичного boot-сбоя;
- пользователь больше не видит сырой HTML/`не JSON` как UI-текст.

## 5. Формулировка результата

Разделяй выводы:
- что было реальной причиной (`catch-path чистил token слишком агрессивно`);
- что было отдельным user-facing дефектом (`сырой HTML/non-JSON message`);
- что уже подтверждено live runtime;
- что ещё не подтверждено без реального login/send smoke.