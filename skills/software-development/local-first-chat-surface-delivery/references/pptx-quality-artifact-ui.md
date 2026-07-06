# PPTX quality contour in chat/file UI

Когда использовать:
- backend уже умеет считать `quality` / `validation` для generated или exported `.pptx`;
- нужно довести это до реального chat-first UX, а не оставить во внутренних helper-ах.

Что обязательно провести насквозь:
1. core export result
   - единый helper должен возвращать не только `buffer`, но и `quality` / `validation`;
2. artifact/meta layer
   - attachment metadata;
   - top-level `file_response.meta`;
   - `thread_files` API, если UI drawer/preview питается не прямо из message attachments;
3. frontend surfaces
   - assistant file cards в сообщении;
   - thread files drawer/panel;
   - file preview modal.

Рекомендуемый UX-словарь:
- `ok` -> `Качество проверено`
- `degraded` -> `Есть ограничения`
- `failed` -> `Проверка не пройдена`

Если `.pptx` используется как быстрый внутренний draft:
- можно встраивать compact quality banner прямо на титульный слайд;
- делать это только для `degraded` / `failed`;
- для `ok` ничего не добавлять, чтобы не засорять нормальные файлы;
- после встраивания баннера повторно прогонять validation на пересобранном артефакте.

Принцип:
- пользователю показывать короткий status + 1 короткое пояснение;
- не вываливать сырые backend payload-ы `quality` / `validation`.

Примеры коротких пояснений:
- `число слайдов отличается от ожидаемого`
- `часть обязательных секций не найдена`
- `backend не подтвердил корректность структуры файла`

Минимальная проверка после изменений:
- backend regression на propagation в `attachments` / `file_response.meta` / `thread_files`;
- frontend `npm run react:build`;
- при возможности live UI acceptance на реальном runtime через кнопку `Выгрузить PPTX`.

Частый промах:
- quality уже есть в export helper-е, но не поднят в `thread_files`; тогда drawer и preview modal остаются «слепыми», хотя чатовый attachment уже содержит статус.
