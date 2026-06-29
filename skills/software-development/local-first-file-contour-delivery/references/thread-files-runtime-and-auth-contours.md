# Thread files: runtime triage and contour split

## Когда полезно

Используй эту заметку, когда пользователь жалуется, что:
- в профиле файлы есть, но в `Файлы этого диалога` пусто;
- после upload файл виден в `/files`, но не виден в `/threads/<id>`;
- acceptance на одном frontend URL проходит, а на другом тот же login/token отвергается.

## Короткий triage-порядок

1. Проверить upload/storage слой:
- есть ли строка в `app.user_files` с нужными `thread_id` и `message_id`;
- виден ли тот же файл в `/api/files`.

2. Проверить thread-level contract:
- что возвращает `GET /api/threads/<id>`;
- если `thread_files=[]`, а файл уже есть в БД и `/files`, проблема не в upload, а в thread serialization path.

3. Проверить serialization helpers:
- `list_thread_files(...)`
- `serialize_user_file(...)`
- normalizer message attachments / assistant attachments
- любые места, где в download URL добавляется auth token

4. Проверить request-context зависимость:
- если helper вызывает `request.headers`, `request.cookies` или `request.args`, нужен guard через `has_request_context()`;
- иначе helper может работать несимметрично в разных code paths и silently терять thread-level payload.

## Проверка контуров до browser acceptance

Сначала явно разнеси:
- какой frontend URL проверяешь;
- в какой API он смотрит;
- в каком auth-store живёт его login/session.

Минимальный набор probes:
- `GET /api/service-info`
- `GET /api/auth/session` с токеном
- browser login с теми же demo credentials

Если:
- API `8791` принимает demo-login,
- `8793/api/auth/session` с тем же token отвечает 200,
- а похожий frontend `8803` даёт browser `401 invalid_credentials`,

то это не одна и та же acceptance-поверхность. Не приписывай это UI-регрессии.

## Что считать сильным сигналом backend bug

Если одновременно верно всё ниже:
- `app.user_files` содержит строку с нужным `thread_id`;
- `/api/files` файл показывает;
- `GET /api/threads/<id>` возвращает пустой `thread_files`;

то почти наверняка баг находится в thread-level serialization / aggregation, а не во frontend-renderer слое.
