# Prod live acceptance: session impersonation and thread freshness debugging

Когда нужно проверить реальный prod UI под конкретным пользователем, а пароль пользователя неизвестен или не должен подбираться, можно делать live acceptance через временную session в prod PostgreSQL.

## Когда использовать

- Нужно воспроизвести баг именно в живом UI под конкретным пользователем.
- Есть SSH-доступ к prod runtime и PostgreSQL.
- Нельзя гадать пароль или просить пользователя прислать секрет.
- Нужно отделить backend payload bug от frontend rendering bug.

## Паттерн проверки

1. Подтвердить prod-контур и пользователя по БД.
2. Создать временную session в таблице `app.sessions` для нужного `user_id`.
3. Подложить этот token в `localStorage` фронта (`hermes_web_mvp_token`) на prod origin.
4. Перезагрузить страницу и проверить live UI уже под нужным пользователем.
5. Параллельно снять `/api/threads`, `/api/jobs` и, если нужно, сообщения треда, чтобы сравнить UI с backend payload.

## Минимальный SQL-паттерн

```sql
insert into app.sessions (token, user_id, created_at, last_seen_at, revoked_at)
values ('temporary-live-acceptance-token', <user_id>, now()::text, now()::text, null);
```

После проверки временную session желательно удалить или revoke.

## Минимальный browser/API-паттерн

1. Открыть prod frontend.
2. Выполнить в браузере:

```js
window.localStorage.setItem('hermes_web_mvp_token', 'temporary-live-acceptance-token');
location.reload();
```

3. Проверить backend token напрямую:

```bash
curl -H 'Authorization: Bearer tempor...ken' http://<backend>/api/me
```

## Что это дало в этом кейсе

### 1. Новый чат

Симптом пользователя выглядел как «сбой поиска информации», но live prod показал другое:

- даже обычное сообщение вроде `как дела?` падало с `collection_output_format_unsupported`
- это указывает не на отказ поиска, а на неверный request routing в `data collection` contour
- ошибка возникает уже в builder-е collection artifact, где поддерживаются только `json/csv/xlsx`

Вывод: при жалобах на «поиск» сначала проверить, не ушёл ли обычный чат в structured collection branch.

### 2. Job thread: старая дата в списке чатов

Надёжный способ локализации:

- открыть thread в UI и зафиксировать видимую дату/время
- запросить `/api/threads`
- сравнить у проблемного thread:
  - `freshness_at`
  - `updated_at`
  - `last_message_at`
  - `preview`

В этом кейсе backend для job-thread отдавал:

- свежие `updated_at` и `last_message_at`
- но старый `freshness_at`

Frontend sidebar использовал `freshness_at` первым приоритетом, поэтому слева показывалась старая дата, хотя внутри треда было новое сообщение.

Вывод: при расхождении даты в sidebar и внутри треда сначала проверить, не stale ли именно `freshness_at`.

## Практический debugging heuristic

Если жалоба связана со списком чатов, не ограничиваться UI-наблюдением. Всегда раскладывать на 3 уровня:

1. БД / реальный thread state
2. `/api/threads` payload
3. frontend rendering priority

Это быстро отделяет:

- backend freshness bug
- frontend timestamp selection bug
- stale preview bug
- ложную пользовательскую интерпретацию

## Осторожность

- Не фиксировать в навыке постоянные негативные утверждения про инструменты.
- Если browser runtime ведёт себя нестабильно, сохранить именно паттерн обхода через session+API, а не тезис «browser не работает».
- При работе с prod делать только минимально необходимую временную session и не использовать этот приём как замену нормальной auth-механике в продукте.