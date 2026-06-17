# Admin reference/users: audit + versioning delivery notes

Когда применять:
- local-first admin surface с backend-справочниками и ручным user CRUD
- пользователь явно просит «проверку», «легирование/логирование», «версионность», «всё должно работать»

Ключевые уроки

1. Для mutable admin-данных недостаточно только create/update endpoint-ов.
Нужен минимальный audit contour:
- `version` в основной сущности (`users`, `reference_items`)
- append-only change log (`user_change_log`, `reference_item_change_log`)
- history endpoint-ы
- видимый frontend-блок истории, иначе аудит остаётся скрытым infrastructure-only слоем

2. Для русского frontend недостаточно перевести подписи форм.
Нужно также перевести пользовательские ошибки API:
- `email_already_exists` → понятная русская ошибка
- `password_too_short` → понятная русская ошибка
- то же для reference-item ошибок и auth/admin ошибок

3. Проверка должна быть end-to-end и включать history.
Минимальный набор:
- login admin
- create user
- patch user
- get user history
- create reference item
- patch reference item
- get reference history
- проверить, что на фронте видны версия и история

4. DuckDB-специфика, которую легко забыть.
- После добавления нового поля в `SELECT u.*` агрегирующий запрос может начать падать из-за `GROUP BY`.
- При миграциях `ALTER TABLE ... ADD COLUMN ... NOT NULL DEFAULT ...` может не пройти; безопаснее иметь fallback: добавить колонку мягко и отдельно backfill/default update.

5. Если пользователь просит «доделывай» без новой декомпозиции, приоритет такой:
- добить рабочий runtime
- проверить live API
- добить фронт-представление аудита/версий
- только потом фиксировать в decision-log

Практический чек-лист
- backend schema: version + change_log
- backend API: list/detail/create/update/history
- frontend admin UI: create/edit/history/version/status
- frontend error mapping: raw backend codes не показывать пользователю
- syntax checks
- live CRUD + history verification
- decision-log update
