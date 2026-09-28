# Hermes Web: thread files fallback + recurring digest hardening

## Когда пригодилось

Сессия по доводке Hermes Web user-facing UI, где одновременно всплыли:
- thread files panel показывала `0`, хотя в thread были реальные attachments;
- recurring `ТГ Дайджест` рендерился как тяжёлая строка/сырой markdown вместо читабельного результата;
- встроенный Hermes browser backend не дал надёжной визуальной приёмки, поэтому пришлось отделить code/runtime proof от screenshot-level proof.

## Что оказалось правдой

### 1. `thread_files` может отсутствовать в top-level thread payload

Live `GET /api/threads/<id>` отдавал:
- `thread`
- `messages`

Но **не** всегда отдавал top-level `thread_files`.

При этом реальные файлы были в `messages[].meta.attachments`.

### 2. Нули в files panel не всегда значат, что файлов нет

Если frontend жёстко ждёт только `threadPayload.thread_files || []`, он может показать пусто при реальных вложениях.

Нужен fallback-aggregator:
- пройти по `messages`
- собрать `meta.attachments`
- проставить `thread_file_role`
- сохранить `preview_summary / preview_excerpt / preview_lines`
- различить user-upload vs assistant-generated

### 3. Recurring digest может прийти в грязной форме

В recurring/file-delivery payload возможны как минимум 3 формы:

1. Нормальный markdown digest.
2. Digest + хвост `Файл приложен к сообщению.`.
3. Reasoning-пролог + затем плоский semicolon-список вида:

`- title; channel; date; [пост](...); summary; links`

Если такой текст положить в `<strong>` как headline result-card, пользователь увидит «сплющенный» мусорный блок.

## Практический frontend pattern

### Для thread files

1. Сначала взять top-level `thread_files`, если они есть.
2. Если их нет или они пусты — собрать files из `messages[].meta.attachments`.
3. Для каждого файла сохранить:
   - origin/provenance;
   - assistant/user role;
   - preview fields;
   - created_at/message link.
4. Использовать один resolver во всех путях:
   - initial load;
   - thread select;
   - refresh loop;
   - create thread;
   - archive/unarchive transition.

### Для recurring digest

1. Result-card headline должен быть коротким (`Дайджест подготовлен`).
2. Основной digest надо рендерить ниже как body.
3. Убирать хвост `Файл приложен к сообщению.` из body.
4. Если тело — semicolon-список, переформатировать каждую строку в блок:
   - `**Заголовок**`
   - `Канал: ...`
   - `Дата: ...`
   - `[пост](...)`
   - `Краткое содержание: ...`
   - `Ссылки: ...`

## Acceptance lesson

Если screenshot/browser acceptance блокируется внешним browser/CDP контуром, не надо выдавать это за полноценную визуальную приёмку.

Но всё равно можно честно подтвердить:
- новый bundle реально сервится на live URL;
- bundle содержит нужные UI markers;
- live API payload содержит attachments / recurring fields, на которые опирается новый renderer.

Это сильное runtime proof, но **не** полная visual acceptance.
