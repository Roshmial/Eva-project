# Sprint 3: markdown/export/lifecycle hardening notes

## Когда пригодится

Используй этот reference, когда в Hermes Web одновременно всплывают симптомы:
- пользователь говорит, что `md` снова «упал» на фронте;
- формат вроде `pptx`/`docx`/`xlsx` «как будто поддержан», но реальный export path даёт отказ или не выдаёт файл;
- в деталях задачи или других user-facing карточках не хватает уже существующих backend-полей;
- feature есть в коде частично, но не доведена до полного lifecycle.

## Практические уроки

### 1. Markdown может ломаться не только в renderer

Симптом:
- `<br>` уже чинили;
- таблицы/markdown всё равно показываются как plain text или «сломанный md».

Проверка:
- смотреть не только `normalizeMarkdownText(...)`/`renderMarkdownContent(...)`, но и детектор rich path вроде `looksLikeRichRecurringBody(...)`.
- если детектор не распознаёт markdown-таблицы, fenced code blocks или blockquote, сообщение уходит в plain-text path, и чинить только renderer бессмысленно.

Минимальный чек:
- markdown-таблица
- fenced code block
- blockquote
- `<br>` внутри таблицы

### 2. Export-format support проверяется как цепочка

Частая ложная готовность:
- есть `build_message_export_pptx(...)` или другой builder;
- но формат не включён в `MESSAGE_EXPORT_FORMATS`, MIME map, `normalize_message_export_format(...)`, routing policy keywords или `build_message_export_stream(...)`.

Проверять нужно весь путь:
1. allowed formats
2. alias normalization (`doc -> docx`, `xls -> xlsx`, `jpg -> jpeg`)
3. MIME type map
4. format detection / routing keywords
5. stream builder switch
6. `/api/messages/<id>/export?format=...`
7. generated-file request path, если поддержан сценарий «сформируй новый ответ и сразу дай файлом»
8. regression tests

### 3. Alias лучше честной нормализацией, чем фальшивой «поддержкой» legacy binary

Если продукт фактически умеет `docx/xlsx/jpeg`, а пользователь просит `doc/xls/jpg`, практичный путь:
- принять запрос как alias;
- серверно нормализовать в реальный поддержанный формат;
- не притворяться, что генерируется настоящий legacy binary `.doc`/`.xls`.

Это особенно важно, чтобы не создавать хрупкую псевдоподдержку ради красивого названия формата.

### 4. User-facing пропуски часто уже закрыты backend-полем

Симптом:
- пользователь просит «добавь владельца задачи»;
- команда склонна думать о новом API.

Проверка:
- сначала проверить текущий jobs payload (`list` и `detail`) на наличие `owner`.
- если поле уже приходит, проблема purely frontend: надо просто вывести его в `Детали задачи`.

### 5. Sprint-долг закрыт только после build + targeted smoke

Минимальная верификация после подобных правок:
- frontend build
- backend smoke на affected export formats
- хотя бы один сценарий generated-file/export intent

`exit 0` от одного скрипта без targeted checks не считать достаточным доказательством закрытия Sprint-долга.
