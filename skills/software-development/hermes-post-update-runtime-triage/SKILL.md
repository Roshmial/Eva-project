---
name: hermes-post-update-runtime-triage
description: "Диагностика Hermes после обновления: быстрый smoke-check, отделение runtime-регрессий от setup/auth-шумов, и прицельная проверка browser/runtime/doctor без лишних side effects."
---

# Когда применять

Используй этот навык, когда после `hermes update` или ручного обновления пользователь просит:
- проверить, что обновление реально встало;
- рассказать, что изменилось в новой версии;
- найти post-update regression;
- быстро оценить работоспособность Hermes без credential-зависимых интеграций;
- отдельно проверить browser tools, `hermes doctor`, local browser runtime или session DB.

Особенно полезно, когда пользователь хочет именно практическую проверку "что реально работает", а не пересказ документации.

# Цель

Дать grounded-оценку после обновления:
1. какая версия реально запущена;
2. что нового подтверждается по локальному коду / git / docs;
3. какие core tools живы;
4. где именно regression или partial failure;
5. что является настоящей проблемой runtime, а что просто credential/setup noise.

# Принципы

- Сначала подтверждай живую версию, потом обсуждай change summary.
- Не путай "tool доступен" и "tool реально работоспособен по назначению".
- Для browser tools всегда проверяй не только факт вызова, но и фактическое состояние страницы.
- Для `hermes doctor` не трактуй долгий запуск как автоматическую поломку всего Hermes: на больших `state.db` возможны тяжёлые DB health-checks.
- Исключай credential-зависимые выводы из общего диагноза, если пользователь просил проверку без кредов.
- Не загрязняй persistent memory результатами такого аудита; устойчивые процедуры оформляй как skill.

# Рекомендуемая последовательность

## 1. Подтверди установленную версию

Собери:
- `hermes --version`
- при необходимости `git -C <repo> show --summary --no-patch <current-commit>`
- при необходимости последние релевантные коммиты / теги

Задача этого шага — отделить "апдейт действительно установлен" от "пользователь думает, что установлен".

## 2. Подними подтверждённые изменения версии

Предпочтительный порядок источников:
1. официальный docs / release page;
2. локальный repo (`git log`, теги, docs);
3. только потом — аккуратная реконструкция по коммитам.

В ответе отделяй:
- подтверждённые изменения;
- вероятные/реконструированные изменения.

Не выдавай реконструкцию за официальный changelog, если полного release note нет.

## 3. Сделай базовый non-credential smoke

Минимальный набор:
- `terminal`
- `write_file` / `read_file`
- `patch`
- `search_files`
- `execute_code`
- `session_search`
- `skills_list` / `skill_view`
- `cronjob list`
- по ситуации `text_to_speech`, `vision_analyze`, `image_generate`

Смысл smoke-check — быстро понять, что core loop жив: shell, файлы, Python, локальные знания, планировщик, сессии.

## 4. Browser tools: проверяй слой за слоем

### Минимальная проверка
Недостаточно вызвать только `browser_navigate`. Нужно проверить всю цепочку:
1. `browser_navigate(url)`
2. `browser_console` с выражением, которое возвращает `location.href`, `document.title`, `document.readyState`, часть `document.body.innerText`
3. `browser_snapshot`
4. при сомнении `browser_vision`
5. при необходимости `browser_get_images`

### Ключевой pitfall
Если `browser_navigate` сообщает успех (`url/title`), это ещё не значит, что реальная вкладка загрузилась. Возможен рассинхрон:
- navigate report показывает целевой URL;
- фактический browser state остаётся `about:blank`;
- snapshot пустой;
- vision показывает белый экран.

Такой симптом трактуй как проблему browser runtime / CDP attach / tab state, а не как успешную навигацию.

### Что делать при таком симптоме
- Проверить локальный CDP endpoint и список вкладок.
- Проверить, не живёт ли только `about:blank` tab.
- Проверить локальные browser processes.
- Если на хосте уже есть выделенный локальный headless Chrome service для Hermes browser tools, не оставляй это как ad-hoc состояние: фиксируй `browser.cdp_url` в основном конфиге (`http://127.0.0.1:<port>`), чтобы browser wrapper не дрейфовал между внутренней local-session и внешним CDP runtime.
- Если DOM уже живой (`snapshot`/`eval` корректны), а `browser_vision` или прямой screenshot всё ещё белые, считай это отдельной Linux runtime-проблемой: проверь user-space `fontconfig`/fonts runtime (`FONTCONFIG_PATH`, `FONTCONFIG_FILE`, `XDG_DATA_DIRS`, `LD_LIBRARY_PATH`) и при необходимости добавь `--no-sandbox --disable-dev-shm-usage` в systemd user-service локального Chrome.
- После фикса не останавливайся на одном успешном navigate: повторно проверь всю цепочку `navigate -> console -> snapshot -> vision`.

## 5. `hermes doctor`: не останавливаться на факте таймаута

Если `hermes doctor` зависает или не укладывается в timeout:
1. проверить `hermes doctor --help` — это быстрый sanity-check команды;
2. по возможности запустить doctor отдельно от длинной комбинированной команды;
3. если нужен длительный прогон — выносить в background;
4. обязательно сохранять, до какого именно раздела doctor дошёл;
5. смотреть код `hermes_cli/doctor.py`, если нужно локализовать секцию зависания.

### Важный pitfall для больших state.db
Если doctor стабильно доходит до строки вида:
- `~/.hermes/state.db exists (N sessions)`

и дальше не движется, проверь код после этой строки. Типичный подозреваемый — `_db_opens_cleanly()` из `hermes_state.py`, который делает:
- `PRAGMA journal_mode`
- `PRAGMA integrity_check`
- `SELECT COUNT(*) FROM sessions`
- rollback write probe в `sessions/messages`

На крупной `state.db` долгий или практически зависающий `PRAGMA integrity_check` может создавать ложное ощущение полной поломки doctor, хотя основной runtime при этом жив.

После текущего remediation-path это нужно трактовать так:
- для обычных БД health probe остаётся строгим;
- для very large local `state.db` operator-facing `_db_opens_cleanly()` может сознательно пропускать полный `integrity_check`, если schema parse, canonical read и FTS-triggered rolled-back write уже подтверждают рабочее состояние.
- Если пользователь хочет именно полноценный offline-integrity audit, это должен быть отдельный явный режим/скрипт, а не default-path `hermes doctor`.
- Если после очередного update `hermes doctor` снова начал зависать сразу после строки про `~/.hermes/state.db exists (N sessions)`, сначала сравни текущий `hermes_state._db_opens_cleanly()` с ожидаемой size-aware логикой. Для live DB порядка гигабайтов типичный regression состоит в том, что `PRAGMA integrity_check` возвращается в default-path и снова делает doctor непрактичным как быстрый smoke-check.
- При таком фиксе обязательно добавляй regression test: на искусственно "большой" DB `_db_opens_cleanly()` не должен вызывать `PRAGMA integrity_check`, но обязан сохранить schema-parse probe, canonical read и rolled-back write probe.

## 5.1. Минимальный remediation-path для этого regression

Если подтвердилось, что зависание снова вызвано полным `integrity_check` на большой live DB:
1. вернуть size-aware shortcut в `hermes_state._db_opens_cleanly()`;
2. порог держать консервативным и operator-facing, чтобы обычные DB продолжали проходить строгую проверку;
3. не убирать write probe по `sessions/messages`, иначе можно пропустить FTS write corruption;
4. добавить regression test, который monkeypatch-ит размер DB как "большой" и падает, если код всё-таки вызывает `PRAGMA integrity_check`;
5. после patch обязательно прогнать: targeted pytest, `py_compile`, прямой вызов `_db_opens_cleanly()` на реальной `state.db`, затем `hermes doctor` целиком.

В итоговом диагнозе всегда раскладывай на три корзины:
- работает подтверждённо;
- работает частично / требует доразбора;
- не проверялось из-за credential dependency.

Не смешивай в одну проблему:
- browser/CDP regression;
- `hermes doctor` DB stall;
- OAuth not logged in;
- config migration warning.

## 7. Если есть config version drift — фиксируй это отдельно

Сообщение вида `Config version outdated (vX → vY)` — это отдельный actionable хвост после обновления.

Даже если это не доказанная причина основного регресса, его стоит вынести в отдельный пункт:
- как факт;
- как возможный косвенный фактор;
- как рекомендованный следующий шаг.

## 6.1. Если "падает gateway", сначала раздели crash и внешний restart

После update или runtime-работ пользователь может описывать это как "gateway стабильно падает", но это могут быть два разных класса событий:

1. **Настоящий crash runtime**
- Ищи в `journalctl --user -u hermes-gateway.service` traceback / exception прямо перед `Main process exited`.
- Отдельно проверяй Python-side background watchers gateway, особенно update watcher и long-running background tasks.
- Если в логах есть `UnicodeDecodeError`, `Task exception was never retrieved`, `status=75/TEMPFAIL` или аналогичный exception-path, это именно runtime bug, а не просто restart.

2. **Внешний stop/restart + неуспешный drain**
- Если видишь `Stopping hermes-gateway.service`, `Shutdown context: signal=SIGTERM under_systemd=yes`, затем `Gateway drain timed out ...` и потом `State 'stop-sigterm' timed out. Killing.`, это не самопроизвольный crash.
- Это значит, что gateway получил внешний stop/restart, начал штатное завершение, но не успел погасить активные задачи до `TimeoutStopSec`.
- В таком случае в диагнозе не пиши просто "gateway падает" — разделяй:
  - кто инициировал остановку;
  - был ли runtime crash до остановки;
  - почему shutdown затянулся.

### Практический алгоритм
- Смотри `systemctl --user status hermes-gateway.service` и `systemctl --user show ... -p ActiveEnterTimestamp -p NRestarts -p MainPID`.
- Читай последние 150–300 строк `journalctl --user -u hermes-gateway.service`.
- Отмечай отдельно:
  - `exception/traceback` перед exit;
  - `status=75/TEMPFAIL` или другой exit code;
  - `signal=SIGTERM under_systemd=yes`;
  - `Gateway drain timed out`;
  - `State 'stop-sigterm' timed out. Killing.`
- Только после этого формулируй root cause.

## 6.2. Конкретный post-update pitfall: update watcher не должен падать на не-UTF8 выводе

Gateway update watcher читает служебные файлы вроде `.update_output.txt`, `.update_prompt.json`, `.update_exit_code`, `.update_pending*.json`.

Если эти файлы читаются через голый `Path.read_text()` без `encoding/errors`, watcher может упасть на mixed-encoding / мусорных байтах из update output и утянуть за собой gateway.

Минимальный safe-path:
- для таких файлов читать через `read_text(encoding="utf-8", errors="replace")`;
- отдельно различать decode-noise в update output и реальную поломку update flow;
- после patch обязательно прогнать хотя бы `py_compile` и затем один контролируемый runtime restart gateway вне самого gateway-процесса.

# Формат результата для пользователя

Рекомендуемая структура:
1. короткий вывод: update installed / основной regression / общее состояние;
2. что нового в версии — только подтверждённое, отдельно от гипотез;
3. что проверено по работоспособности;
4. что именно сломано или подозрительно;
5. следующий практический шаг.

Для пользователей, которым важен прикладной итог, не вываливай сырой лог целиком. Переводи его в диагноз, но сохраняй трассируемость: какие именно проверки дали этот вывод.

# Pitfalls

- Не считать `browser_navigate` достаточным подтверждением работоспособности browser tools.
- Не называть весь Hermes "сломавшимся", если завис только `hermes doctor`.
- Не делать вывод "битая база", если есть только долгий `integrity_check` на большом `state.db`.
- Не смешивать credential warnings с post-update regression.
- Не останавливаться на одном таймауте: нужно локализовать, где именно процесс завис.

# Артефакты навыка

- См. `references/post-update-runtime-triage-notes.md` — краткая памятка по browser/runtime/doctor симптомам, выявленным в живой диагностике.
- См. `references/doctor-large-state-db-regression.md` — конкретный remediation-path для regression, где `hermes doctor` после update снова зависает на большой `state.db` из-за возвращённого `PRAGMA integrity_check`.

# Когда завершать

Навык считается выполненным, когда у пользователя есть:
- подтверждённая версия;
- список реально проверенных возможностей;
- отделённый диагноз по browser и/или doctor, если они были в фокусе;
- 1–2 конкретных следующих шага, а не общий призыв "посмотреть позже".
