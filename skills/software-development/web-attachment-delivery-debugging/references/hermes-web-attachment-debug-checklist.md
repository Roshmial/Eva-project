# Hermes Web attachment debugging checklist

Используй этот список, когда пользователь говорит, что файл «пропал», «не открывается» или «не скачивается».

## 1. Contour first

Зафиксируй:
- frontend host/port
- backend host/port
- local/dev/prod
- DB driver / DSN

Выводы из local DuckDB нельзя автоматически переносить на prod Postgres.

## 2. Identify the exact conversation target

Найди:
- user id / email
- thread id
- последние assistant messages в нужном треде

Если пользователь говорит «последняя переписка», проверяй `threads order by updated_at desc` для этого user.

## 3. Message-layer evidence

Проверь у подозрительных сообщений:
- `message_kind=file_response`
- `meta.attachments`
- `download_url`
- `local_path`
- `processing_status`
- `error_text`

Разделяй:
- attachment delivery failure
- generation timeout / processing error

## 4. File-system evidence

Для каждого attachment:
- существует ли `local_path`
- ненулевой ли размер
- совпадает ли имя файла с тем, что видит пользователь

## 5. API-layer evidence

Проверяй download endpoint именно с валидной user session:
- `GET /api/messages/<id>/attachments/<idx>`
- status
- content-type
- payload length

401 без токена не является доказательством поломки attachment delivery.

## 6. Live UI evidence

Проверь:
- attachment виден в списке файлов
- клик инициирует download
- suggested filename корректный
- при необходимости проверь несколько файлов, а не один

## 7. Reporting pattern

Короткий итог пользователю:
- prod/local contour
- attachment exists / missing
- API works / fails
- UI reproduces / does not reproduce
- next requested evidence from user if issue persists

## Session note captured from this case

В одном из кейсов симптом «у Виктории опять отвалились файлы» не подтвердился на prod:
- prod contour оказался Postgres-based;
- attachments присутствовали в DB meta;
- `.docx` существовали на диске;
- protected attachment endpoints отдавали `200` с валидной user session;
- live UI показывал файлы и запускал download.

Следовательно, при похожем сигнале сначала проверяй session/client-specific сбой, а не объявляй потерю файлов на backend.