---
name: web-attachment-delivery-debugging
description: Диагностика потери/недоступности файлов и message attachments в Hermes Web и похожих chat-first web UI.
---

# Когда применять

Используй навык, когда пользователь говорит, что в web-интерфейсе:
- пропали файлы из чата;
- attachment виден, но не скачивается;
- download работает не у всех пользователей;
- есть сомнение, проблема в frontend, backend, БД, файловой системе или конкретной сессии.

Особенно полезно для Hermes Web и других chat-first UI, где файл проходит путь:
message meta -> DB record -> local file/storage path -> protected API endpoint -> frontend rendering -> browser download.

# Цель

Быстро отделить:
- реальную потерю файла на сервере;
- проблему авторизации/сессии;
- дефект frontend rendering;
- дефект download endpoint;
- путаницу между local/dev/prod контурами.

# Принципы

1. Не смешивай контуры.
   Сначала явно зафиксируй, какой contour проверяешь: local/dev/prod, какой frontend host, какой backend host, какая БД.

2. Не лечи UI вслепую.
   Если пользователь говорит «файлы отвалились», сначала проверь факт существования attachment по данным и API, а не начинай сразу менять React-код.

3. Проверяй всю цепочку доставки.
   Нужно пройти минимум 5 уровней: user/thread -> message meta -> file on disk -> protected API -> live UI download.

4. Разделяй symptom и root cause.
   Один и тот же symptom в UI может означать разные причины: data corruption, неверную сессию, не тот тред, битый download_url, отсутствие файла на диске, client-side glitch.

# Пошаговый протокол

1. Уточни пользователя и последний релевантный тред.
   Для prod-проверок найди user id/email и последние threads по updated_at.

2. Зафиксируй storage/backend contour.
   Проверь, какая БД реально используется в этом контуре:
   - DSN/driver env;
   - health/runtime config;
   - local DuckDB и prod Postgres не должны смешиваться в выводах.

3. Проверь сообщения с attachment-метаданными.
   Для подозрительного thread_id найди последние assistant messages с:
   - `message_kind=file_response`
   - `meta.attachments`
   - `download_url`
   - `local_path` / `relative_path`
   - `processing_status=error`, если пользователь говорит, что генерация «сломалась».

4. Проверь файловую систему.
   Если в meta есть `local_path`, проверь:
   - файл существует;
   - размер ненулевой;
   - имя совпадает с ожидаемым export/download.

5. Проверь защищённый API download с валидной user-сессией.
   Недостаточно получить 401 без токена. Нужна именно проверка с действующей сессией того пользователя, который жалуется.
   Для каждого проблемного attachment проверь:
   - `GET /api/messages/<message_id>/attachments/<idx>`
   - статус
   - content-type
   - размер payload

6. Проверь live frontend.
   Через headless browser или другой live runtime probe проверь:
   - файл виден в UI;
   - у кнопки/ссылки есть правильный download behavior;
   - клик реально инициирует download;
   - suggested filename совпадает с ожидаемым.

7. Только потом формулируй root cause.
   Возможные классы причин:
   - data/storage issue;
   - auth/session issue;
   - rendering issue;
   - endpoint issue;
   - user-side transient glitch.

# Hermes Web: важные частные правила

- Если ранее была локальная проблема с DuckDB, не переноси её автоматически на prod.
- Для prod-проверки сначала установи, что backend реально сидит на Postgres/другой БД, а не на локальном `.duckdb`.
- Если attachment endpoint отдаёт `200`, файл есть на диске, а UI показывает кнопку и download проходит, значит «файлы отвалились» не воспроизведено; дальше ищи session/client-specific проблему.
- Если есть `processing_status=error` или `timed out`, не путай это с потерей уже созданных файлов: это отдельный сбой генерации, а не обязательно сбой attachment delivery.
- Отдельно проверяй, не путается ли attachment delivery с export/generation logic. Симптом «не отдал файл» может означать не потерю вложения, а то, что запрос вида «Отправь мне файл» вообще ушёл не в export-route, а в обычный LLM-path.
- Если backend заявляет `.docx`, подтверждай реальный бинарный файл по HTTP, а не по названию. Минимум проверь: `Content-Type=application/vnd.openxmlformats-officedocument.wordprocessingml.document`, ненулевой размер и zip magic `PK\x03\x04` в первых байтах.
- Если модель пишет про «ограничения среды», «невозможность создать бинарный файл», «установку библиотек» или предлагает Markdown вместо файла, не принимай это как объяснение без backend-проверки. Сначала установи, есть ли в runtime нужная библиотека и может ли backend сам собрать файл без участия LLM.

# Проверка export/generation path

Если речь не о скачивании уже существующего attachment, а о жалобе «агент вместо файла пишет объяснения», добавь ещё 4 шага:

1. Проверь, что именно запустило backend.
   Определи, распознался ли пользовательский запрос как export-request (`docx`, `pdf`, `xlsx` или generic request вроде «Отправь мне файл»).

2. Проверь источник экспорта.
   Установи, какой `exported_message_id` backend выбрал фактически. Это важно: дефект может быть не в файле, а в том, что экспортируется apology/limitation-message вместо последнего содержательного ответа.

3. Отдели backend-ограничение от фантазии модели.
   Если модель пишет, что «не может создать настоящий .docx», проверь runtime напрямую:
   - установлен ли `python-docx` в backend venv;
   - вызывает ли backend локальный export-builder, а не внешний tool/execute path;
   - создаётся ли `.docx` на диске и скачивается ли он по API.

4. Для file-request требуй backend-controlled исход.
   Для запроса на файл правильный финал — либо `message_kind=file_response` с attachment, либо короткая file-specific ошибка. Длинные apology-полотна и рассказы про Markdown считай дефектом контракта, а не допустимым UX.

5. Отдельно проверь false-positive file intent.
   Если пользователь обсуждает баги вокруг файлов, логирование, routing или прошлые ошибки («исправь баг с некорректной генерацией файлов», «я не просил ничего собирать», «включи лог», «почему снова word»), это не должно попадать в `generated_file_response` и не должно автоматически собирать `.docx`.

- Отдельно проверь leakage локального пути в обычный ответ.
  Если attachment не создавался, пользователь не должен видеть служебные пути вроде `/home/hermes/...` в обычном assistant reply. Это уже не delivery успех, а утечка внутреннего runtime-state в UX.
- Разделяй два близких сценария file-intent:
  1. export предыдущего ответа (`Собери файл`, `Пришли файл`) — ожидаемый итог `source=message_export` и `exported_message_id` указывает на уже существующий содержательный assistant message;
  2. generate-and-attach новый файл (`Собери один файл, где будет суммаризация`, `Сделай файл с суммаризацией`, `В одном файле собери итог`) — ожидаемый итог `source=generated_file_response` и `generated_from_request=true`.
  Если второй класс запросов уходит в обычный chat-text с рассказом про Markdown-файл или локальный путь, это routing bug, а не download bug.
- Для summary/file гибридов проверяй не только наличие attachment, но и чистоту финального текста.
  Симптомы отдельного дефекта: summary-ответ заканчивается консультативным хвостом вроде `Рекомендация по реализации`, `Рекомендация по следующему шагу`, `Следующий шаг`, либо generated-file content/preview заражается служебной инструкцией `Подготовь только финальное содержимое документа...`. Это уже не delivery-bug, а нарушение output-contract generated-file path.

# Что обязательно сообщить пользователю

Дай короткий итог в 4 блоках:
- что проверено;
- что подтверждено фактами;
- что НЕ воспроизвелось;
- какой следующий минимальный шаг нужен от пользователя, если проблема остаётся.

# Типовые ловушки

- Лечить frontend до проверки DB/API.
- Путать отсутствие авторизации с отсутствием файла.
- Проверять endpoint без user token и делать вывод, что файл «не открывается».
- Путать локальный runtime с продом.
- Считать любой `processing_status=error` доказательством, что все attachments в треде сломаны.
- Верить тексту модели про «ограничения среды» без проверки backend runtime и фактического binary download.
- Пытаться чинить только timeout, когда реальная проблема в том, что generic file-request ушёл не в export-route.
- Считать любое упоминание слов `файл`, `word`, `экспорт`, `выгрузка` признаком file-intent. В живом Hermes Web это может ошибочно отправить обычный текстовый запрос в `generated_file_response`.
- Не проверять negative cases. После фикса file-flow обязательно проверь не только `собери файл`, но и соседние фразы про баг/логирование/ошибочную генерацию, чтобы убедиться, что они не создают attachment и не светят локальный путь.

# Артефакты навыка

- `references/hermes-web-attachment-debug-checklist.md` — краткий checklist и признаки по уровням chain-of-delivery.
- `references/file-export-contract-hardening.md` — признаки смешения delivery/generation, live-признаки настоящего `.docx` и правила backend-contract для file-request.
- `references/file-intent-false-positive-cases.md` — кейсы ложного file-intent и признаки, которые надо проверять в live runtime.
- `references/summary-file-routing-and-output-contract.md` — различение `message_export` vs `generated_file_response`, summary-tail leakage, local-path leakage и загрязнение generated-file content.
