# Chat runtime debugging patterns

Короткие паттерны для local-first chat/UI задач, когда пользователь жалуется не только на внешний вид, но и на деградацию основных пользовательских инвариантов.

## 1. Сначала acceptance по пользовательским инвариантам, потом soft-polish

Если пользователь перечисляет конкретные chat-регрессии, приоритет проверки такой:
- welcome / zero-state;
- starter prompts;
- дата и preview в списке чатов;
- send on Enter;
- unread / no forced jump semantics;
- доступ к profile files;
- file send / file receive;
- видимый agent activity / error state.

Не продолжай абстрактную визуальную полировку, пока эти инварианты не подтверждены.

## 2. Если экран живёт, а backend intermittently даёт 500 на supposedly read-only boot routes

Подозревай не frontend parse bug, а скрытую запись в auth/session path.

Типичный симптом:
- `/me`, `/bootstrap`, `/threads`, `/jobs/meta` падают по-разному и не на каждом запросе;
- во frontend это выглядит как `Сервис вернул не JSON (500)` или как случайный возврат на login.

Практический корень:
- `require_auth()` или аналогичный middleware делает `UPDATE sessions SET last_seen_at ...` на каждом GET;
- при параллельном boot на DuckDB/single-writer контуре это может давать `TransactionContext Error: Conflict on update!`.

Практический ремонт:
- не считать heartbeat-write частью критического read-path;
- сделать обновление `last_seen_at` best-effort или вынести в более редкий отдельный путь;
- только после этого переоценивать frontend boot.

## 3. Если после рестарта backend фронт снова показывает login screen

Сначала проверь, не потерялась ли просто браузерная сессия.
Не объявляй это регрессом chat UI, пока не выполнен повторный login и не подтверждён целевой экран.

## 4. Если file-send подозрительно «не работает»

Разделяй два слоя:
- backend действительно вернул assistant attachment/meta;
- frontend действительно показал пользователю download/render affordance.

Если frontend вырезает `MEDIA:` из текста, но не строит видимые attachment links из `message.meta.attachments`, пользователь будет воспринимать это как «агент файл не прислал», даже если backend фактически всё сохранил.
