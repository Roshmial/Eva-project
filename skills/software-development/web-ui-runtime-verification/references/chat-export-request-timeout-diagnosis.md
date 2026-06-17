# Chat runtime diagnosis for export-like user requests

Когда пользователь в Hermes Web видит в чате `Не удалось получить ответ. Проверьте отправку сообщения и повторите попытку.`, а вопрос звучал как просьба подготовить артефакт (`в формате Word`, `docx`, `собери файл`, `отправь документ`), не считай это автоматически фронтовым дефектом.

## Проверочный порядок

1. Найди пользователя, последний thread и последние `chat_tasks`.
- Сверь `user_message_id`, `assistant_message_id`, `status`, `created_at`, `started_at`, `finished_at`, `last_error`.
- Отдельно посмотри `messages.meta_json` у assistant-message: `pending`, `processing_status`, `error_text`, `task_id`.

2. Проверь, что UI показывает backend-истину, а не придуманный текст.
- Если в БД `chat_tasks.status = error` и `last_error` непустой, фронт обычно лишь отображает уже зафиксированную backend-ошибку.
- Для этого класса инцидентов важнее `chat_tasks.last_error`, чем сам пользовательский bubble-текст.

3. Коррелируй это с upstream runtime-логом.
- Сними `journalctl --user -u hermes-gateway.service` за окно между `started_at` и `finished_at`.
- Ищи tool-level warnings/errors: `read_file`, `execute_code`, `write_file`, path errors, policy blocks.
- Если backend пишет только `timed out`, именно gateway/tool log часто даёт реальный контекст, что происходило внутри агентного ранa.

4. Проверь chat runtime configuration.
- Сверь `HERMES_WEB_HERMES_API_TIMEOUT`.
- Для Hermes Web типичный сигнал: `finished_at - started_at` почти ровно равен timeout, а `last_error = timed out`.
- Это означает не "фронт сломался", а то, что downstream/agent-run не вернул финальный completion за отведённое окно.

5. Проверь, есть ли в контуре штатный продуктовый путь под запрошенный артефакт.
- Для Word/docx ищи реальную поддержку в backend/frontend: export route, serializer, generator, библиотеку (`docx`, `python-docx`, и т.п.), UI-кнопку/flow.
- Если такого контура нет, а запрос просит именно готовый файл, агент может уйти в импровизированный tool-flow и зависнуть в нём до timeout.

## Практический вывод

Если одновременно выполняются три условия:
- `chat_tasks.last_error = timed out`;
- в gateway-логе внутри того же окна есть tool warnings/errors;
- в продукте нет явного штатного export-path для запрошенного формата,

то первопричину нужно формулировать так:

`Запрос сменил класс работы: вместо обычного текстового ответа агент попытался выполнить артефактный/tool-driven сценарий, для которого в текущем chat path нет устойчивого продуктового контура. В результате ран не завершился в пределах timeout и backend вернул error state.`

## Что не путать

- Это не то же самое, что общий сбой backend или очереди.
  - Если соседние `chat_tasks` того же пользователя успешно завершались, проблема локальна к конкретному типу запроса.

- Это не обязательно дефект фронта.
  - Если фронт показывает assistant bubble с `processing_status=error`, он может быть полностью корректен.

- Это не всегда проблема модели.
  - Иногда модель вообще не главный лимит; реальный срыв происходит в промежуточном tool-flow или policy block внутри gateway.

## Рекомендуемая реакция

Не повышай timeout вслепую как первый шаг.

Сначала выбери один из двух продуктовых путей:
- либо честно деградировать такие запросы в текстовый ответ (`могу подготовить текст для Word, но не сам .docx`);
- либо внедрить отдельный устойчивый export-flow для нужного формата и уже потом разрешать такие запросы в chat path.
