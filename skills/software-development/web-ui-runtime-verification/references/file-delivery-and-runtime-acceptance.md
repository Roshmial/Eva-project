# File delivery and runtime acceptance

## Когда открывать
- Server-side task/probe говорит `completed`, но пользователь жалуется `а где файл?`.
- Backend сообщает, что export/collection выполнен, но в UI нет attachment-кнопки.
- После фикса часть старых thread всё ещё выглядит сломанной, а новые прогоны уже проходят.

## Главный принцип
Не считать file-producing сценарий закрытым, пока не подтверждены все три слоя:
1. backend task завершился;
2. assistant message содержит `meta.attachments[]` с реальным `download_url` / `local_path`;
3. в живом UI у сообщения есть кликабельный attachment.

Текст вида `Сообщений получено: N` или `Файл подготовлен` сам по себе не является доказательством delivery.

## Минимальный acceptance-checklist
1. Запустить сценарий через user-path, а не только прямым backend probe.
2. Проверить последний assistant message в БД/API:
   - `message_kind`
   - `downstream`
   - `attachments`
   - `collection_contract` / `task_source_list`, если это collection/export path.
3. Убедиться, что attachment реально присутствует в UI-сообщении, а не только в meta.
4. Если сценарий завязан на файл, проверить, что attachment ведёт к реальному артефакту, а не к пустому placeholder.

## Важное различие: старые thread vs новые прогоны
После runtime/router fix старые thread могут сохранять старые assistant messages, которые были созданы до исправления.

Поэтому:
- не судить о regression только по старому thread;
- обязательно создать новый thread или новый post-fix run;
- сравнить old-thread result и new-thread result отдельно.

Практическое правило:
- old thread полезен как историческое доказательство бага;
- new thread обязателен как доказательство фикса.

## Telegram / export-specific lesson
Для сценариев, где backend запускает внешний collector/API, нельзя останавливаться на подтверждении вызова внешнего API.

Нужно отдельно проверить:
- не только `api_result.count`,
- но и generation attachment внутри backend message,
- и рендер attachment в UI.

Иначе получается ложнозелёный результат: execution есть, а пользователь delivery не получил.

## Routing lesson for market/dashboard prompts
Формулировки вида:
- `по рынку X`
- `по рынку X и дай дашборд`

нужно отдельно проверять на subject extraction.

Acceptance должен подтверждать, что:
- `subject = X`, а не `X и дай дашборд`;
- запрос не уходит в `missing_fields` / `clarification_request`, если intent уже явно задан.

## Runtime command nuance
Если в проекте есть shell-wrapper вроде `runtime_env.sh`, проверяй его фактическую семантику:
- он может только `export`-ить env;
- он может не исполнять переданную команду автоматически.

Поэтому для live restart / unittest / smoke не полагайся на название скрипта. Сначала проверь, что именно он делает, потом строй restart/runbook вокруг реального поведения.

## Что worth logging in decision-log
Если file-delivery или runtime acceptance добит до живого результата, зафиксируй:
- что именно раньше выглядело зелёным только в логах;
- каким фактом подтверждён реальный user-facing fix;
- какие проверки теперь обязательны для этого класса задач.
