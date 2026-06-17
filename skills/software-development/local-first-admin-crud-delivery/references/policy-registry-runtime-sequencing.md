# Policy registry и sequencing live-приёмки

Короткий session-level конспект для admin/source-policy задач в Hermes Web MVP и похожих local-first admin-контурах.

## Что оказалось важным

1. Верхний уровень source registry нельзя привязывать к одному частному датасету вроде `telegram_digest`.
2. Пользовательская модель может быть существенно шире одного дайджеста: Google API, Telegram API, tender/procurement API, внутренние registry и другие каналы данных.
3. Поэтому верхний уровень должен описывать классы источников, а не один конкретный data product.
4. Для `internal_connector` / `external_connector` допустим вложенный слой auto-discovery с простым статусом `available/unavailable`.

## Практический продуктовый паттерн

Верхний слой:
- `user_attachment_dataset`
- `local_dataset_registry`
- `internal_connector`
- `external_connector`
- `web_research`

Нижний слой только для connector-групп:
- `child_connectors`
- `status: available | unavailable`
- `enabled`
- минимальные operational-поля (`alias`, `route`, `target`, `purpose`) только если они реально доступны из Hermes/env

## Ключевая ловушка

Если live UI уже открылся, но показывает старый/неполный source inventory, не начинай с визуальной полировки.

Типичный ложный путь:
- увидеть, что в чате/админке есть новый блок policy;
- заметить несовпадение с ожидаемым payload;
- сразу лечить layout или labels.

Правильный путь:
1. подтвердить, какой backend реально обслуживает живой порт;
2. снять живые `/bootstrap` и `/api/admin/...` ответы;
3. локализовать `500/502` или stale runtime;
4. подтвердить save/read round-trip policy;
5. только потом оценивать UI и доводить визуально.

## Почему это важно

Пока runtime JSON нестабилен, визуальная приёмка policy-блока обманчива:
- UI может быть уже новым;
- backend payload — старым, неполным или аварийным;
- итоговый verdict по admin acceptance будет ложным.
