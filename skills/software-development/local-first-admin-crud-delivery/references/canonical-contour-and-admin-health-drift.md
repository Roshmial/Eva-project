# Canonical contour vs stale runtime + admin health drift

Когда использовать:
- пользователь явно указал каноническое дерево и порты;
- новый admin route в коде есть, но live contour отвечает не так, как ожидалось;
- admin health/overview падает на live БД, хотя CRUD и отдельные routes уже работают.

Короткий приёмочный паттерн:
1. Явно зафиксировать матрицу `repo -> frontend port -> backend port -> launch script`.
2. Проверить, какой PID реально слушает каждый порт.
3. Сверить `cwd/cmdline`, чтобы исключить stale backend из другого дерева.
4. Дёрнуть exact-route напрямую.
5. После правильного рестарта ожидать смену сигнала `404` на auth-gated `401`, если route существует, но закрыт авторизацией.
6. Только после этого делать browser/UI verdict.

Отдельный durable-урок для admin health:
- зелёные CRUD/policy tests не доказывают корректность overview-аналитики;
- если live traceback говорит, что в `messages` нет `user_id`, это не "странность конкретной БД", а сигнал проверить фактическую модель данных перед написанием агрегатов;
- для user-level метрик предпочитать join по `threads`/другому каноническому владельцу, а не предположение, что `messages` хранит прямой `user_id`.

Типовой симптом:
- DuckDB BinderException вида `Referenced column "user_id" not found in FROM clause` в `admin_health` при том, что `GET /api/admin/users`, `GET /api/admin/events`, `PATCH /api/admin/processing-policy` и `PATCH /api/admin/data-sources` уже проходят.

Что это меняет в workflow:
- live acceptance admin-контура должен включать не только route existence и CRUD, но и отдельный hit по summary/health endpoint, если экран опирается на него.
