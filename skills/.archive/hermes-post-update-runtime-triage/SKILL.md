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

### Обязательный post-update install hygiene check
После `hermes update` или git-based refresh не считай runtime полностью обновлённым, пока не проверишь install-tree зависимости, особенно Node-side хвосты.

Практический минимум:
- `hermes doctor`
- если doctor жалуется на missing browser/npm dependency (например `agent-browser not installed`) — проверить install dir, а не только текущий cwd;
- для git install в первую очередь смотреть реальный `Install directory` из `hermes --version` / `hermes status`;
- при missing Node dependency сначала делать `npm install`, затем при необходимости `npm update` внутри install dir;
- после remediation повторно прогонять `hermes doctor`.

Ключевой вывод: post-update regression может быть не в Python/runtime-коде, а в том, что update не довёл Node install tree до согласованного состояния.

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

### Большая session DB: безопасная оптимизация и завершение

Если `hermes doctor` рекомендует `hermes sessions optimize-storage`, сначала создай консистентную SQLite backup-копию через SQLite backup API, а не копированием `state.db` вместе с изменяющимся WAL. Затем запускай оптимизацию как долговременный background-процесс с отдельным логом: на большой live-базе она может не уложиться в интерактивный tool timeout, а прерывание допустимо только потому, что команда умеет продолжать работу.

После завершения обязательно проверь:
1. финальную строку `Search index optimized` в логе;
2. изменение размера `state.db`;
3. `PRAGMA quick_check`;
4. совпадение числа строк `messages` и `messages_fts`;
5. состояние gateway и доступность списка сессий.

Если после оптимизации `doctor` видит крупный WAL, сначала запусти `hermes doctor --fix`. Если checkpoint не уменьшает WAL при работающем gateway, нужен контролируемый restart gateway; до него нельзя заявлять, что storage cleanup полностью закрыт, потому что соединение live-процесса удерживает WAL.

Pitfall: не удаляй старые session rows ради места до экспорта и проверки архива — `state.db` хранит контекст и ссылки на созданные артефакты, а не сами артефакты из workspace.

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

## 6.3. Версионный drift после update нужно диагностировать отдельно от release-note вопроса

После проверки `hermes --version` обязательно сравни:
- release tag, который пользователь называет;
- точный текущий commit;
- есть ли `HEAD` прямо на tag или runtime уже ушёл дальше по `main`.

Если видишь картину вида `vX.Y.Z-N-g<sha>` или `git log <tag>..HEAD` не пустой, прямо фиксируй это в диагнозе:
- установленный runtime новее named release;
- changelog для named release и фактическое содержимое текущего runtime — это не одно и то же.

Практический смысл:
- для пункта "что нового в версии" опирайся на release tag;
- для пункта "почему сейчас что-то ведёт себя иначе" учитывай все коммиты поверх tag.

Без этого легко перепутать release regression с drift на moving `main`.

## 6.4. Не обновляй `npm` CLI отдельно, пока не проверила engine-совместимость с текущим Node

Если пользователь просит "обновить npm" или приводит его как пример не дообновлённого хвоста:
1. сначала проверить `node -v` и `npm -v`;
2. затем `npm view npm version` и `npm view npm@<latest> engines --json`;
3. обновлять `npm` только если текущий Node попадает в требуемый engine-range.

Причина: отдельный upgrade `npm` часто выглядит как harmless tail update, но реально может сломаться или внести лишний конфликт раньше, чем будет доказана совместимость по engines.

### Практический post-update pattern
Если цель — закрыть хвосты после обновления Hermes, используй такой порядок:
1. проверить `node -v`, `npm -v`;
2. проверить latest major `npm` и его `engines`;
3. если latest major не совместим с текущим Node — не форсить его, а выбрать последнюю совместимую версию внутри текущего major или ближайшего совместимого major;
4. после апдейта `npm` прогнать в install dir Hermes сначала `npm install`, потом `npm update`;
5. затем перепроверить `hermes doctor` и убедиться, что warning вида `agent-browser not installed` исчез.

### Конкретный живой пример совместимости
На live post-update проверке встречался такой кейс:
- `node v24.11.1`
- `npm 11.6.2`
- latest `npm 12.x` требовал `node ^22.22.2 || ^24.15.0 || >=26.0.0`

Вывод в таком случае:
- `npm 12.x` обновлять рано;
- безопасный путь — обновиться до последней совместимой `npm 11.x`, затем выполнить `npm install` и `npm update` в install tree Hermes.

Это полезно фиксировать именно как compatibility-first pattern, а не как частный случай конкретной версии.

## 6.5. Если пользователь просит `доделать хвосты`, не оставляй operator-facing residue как будто это уже closeout

Фразы пользователя вроде:
- `доделай хвосты`;
- `обнови npm, проверь окончательно работу`;
- `доделай все хвосты`;

означают, что нельзя завершать задачу на стадии:
- `doctor зелёный, но warning остался`;
- `npm update сделан, но audit ещё не ноль`;
- `browser работает, но install approvals ещё pending`.

В таком режиме считай хвостами всё, что ещё видно оператору и поддаётся безопасной remediation без тяжёлой архитектурной перестройки:
- `npm audit` уязвимости;
- pending `npm install-scripts` approvals;
- install-tree drift в `package-lock` / workspace deps;
- SQLite advisory, если его можно снизить локальным override внутри Hermes `.venv`.

Правило завершения:
1. убрать все безопасно устранимые хвосты;
2. повторно прогнать `hermes doctor`;
3. повторно сделать browser/file smoke;
4. только потом говорить, что post-update ветка закрыта.

Если хвост принципиально не устраним в текущем контуре без тяжёлой пересборки, это нужно назвать явно как единственный residual risk, а не прятать в формулировку `в целом всё ок`.

## 6.6. SQLite advisory после update: сначала wheel-override, затем при необходимости локальная сборка на точной версии

Если `hermes doctor` упирается не в поломку, а в SQLite version advisory, и пользователь просит закрыть хвосты полностью:
1. сначала проверь, можно ли поднять SQLite через готовый wheel (`pysqlite3-binary` или `pysqlite3`) внутри Hermes `.venv`;
2. если wheel новее системного `sqlite3`, допускается локальный override именно для Hermes runtime;
3. практичный быстрый вариант — `.pth`-hook в `site-packages`, который подменяет `sqlite3` на `pysqlite3` до запуска Hermes;
4. после этого обязательно перепроверь:
   - `.venv/python` реально видит новый `sqlite3`;
   - `hermes doctor` использует уже новый runtime;
   - основной CLI всё ещё работает.

Если wheel не дотягивает до policy-требования doctor (например wheel даёт только `3.51.1`, а doctor хочет `3.51.3+`), не останавливайся на формулировке `функционально уже нормально`. Для self-hosted Hermes допустим второй этап:
5. скачать официальный SQLite amalgamation под нужную версию;
6. пересобрать `pysqlite3` локально внутри Hermes `.venv` уже с приложенными `sqlite3.c` и `sqlite3.h`;
7. если в системе нет установленных Python headers и нет root-доступа, можно временно скачать `python3.12-dev` / `libpython3.12-dev` как `.deb` через `apt download`, распаковать локально `dpkg-deb -x` и передать include-path через `CFLAGS`;
8. после локальной сборки снова проверить `sqlite3.sqlite_version`, `sqlite3.__file__`, `hermes doctor` и `hermes status`.

Практический живой паттерн:
- сначала wheel-path может поднять runtime с системного `3.45.1` до `3.51.1`;
- затем, если нужен именно `3.51.3+`, собрать `pysqlite3` из official amalgamation `3510300`;
- для сборки без sudo может понадобиться локально распакованный `libpython3.12-dev` и `CFLAGS` с include-path на распакованные headers.

Это нужно трактовать как operator-side remediation для self-hosted Hermes, а не как универсальную рекомендацию для любого Python-проекта.

## 6.7. Backup error после update не всегда означает провал бэкапа

Если пользователь пишет, что `backup ушёл с ошибкой` сразу после update:
1. сначала ищи сам backup artifact, а не только stderr-текст;
2. отдельно проверь update log, cron output и journal, чтобы отделить реальную ошибку backup от сбоя shell-обвязки;
3. если в логах есть `printf: --: invalid option`, проверь, не печатала ли обвязка строку, начинающуюся с `---`;
4. если backup-файл реально создан, трактуй инцидент как false-positive в обвязке/логировании, а не как потерю backup.

Живой симптом этого класса:
- backup-файл существует;
- update или cron report показывает `printf: --: invalid option`;
- фактическая проблема не в создании backup, а в shell-выводе статуса/разделителя.

## 6.8. Когда пользователь просит закрыть post-update хвосты до конца, после `npm install` проверь ещё audit и install-script approvals

Если после update пользователь явно просит `доделать все хвосты`, post-update closeout не заканчивается на `agent-browser installed`.

Дополнительный operator-facing checklist:
1. `npm audit --json` в install dir Hermes;
2. `npm ls <problem-package>` для точечной локализации transitive уязвимости;
3. если уязвимость сидит в dev/workspace dependency, сначала искать минимальный совместимый downgrade/upgrade по конкретному workspace, а не делать слепой `npm audit fix --force`;
4. после `npm install` / `npm update` проверить `npm install-scripts ls --json`;
5. если approvals pending и это локальный self-hosted контур, можно безопасно закрыть хвост через `npm install-scripts approve --all`, затем ещё раз прогнать `npm install`.

Живой пример полезного remediation-паттерна:
- `npm audit` показал high severity через `concurrently -> shell-quote`;
- безопасный fix был не `force`, а перевод конкретной workspace dependency `concurrently` на совместимую ветку `9.2.4`;
- после этого `npm audit` стал нулевым, а `install-scripts approve --all` убрал operator-facing pending approvals.

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
- Не объявлять ветку post-update закрытой, если пользователь просил `доделать хвосты`, а `npm audit`, install approvals или SQLite advisory ещё остались и их можно снять безопасно.

# Артефакты навыка

- См. `references/post-update-runtime-triage-notes.md` — краткая памятка по browser/runtime/doctor симптомам, выявленным в живой диагностике.
- См. `references/doctor-large-state-db-regression.md` — конкретный remediation-path для regression, где `hermes doctor` после update снова зависает на большой `state.db` из-за возвращённого `PRAGMA integrity_check`.

# Когда завершать

Навык считается выполненным, когда у пользователя есть:
- подтверждённая версия;
- список реально проверенных возможностей;
- отделённый диагноз по browser и/или doctor, если они были в фокусе;
- 1–2 конкретных следующих шага, а не общий призыв "посмотреть позже".
