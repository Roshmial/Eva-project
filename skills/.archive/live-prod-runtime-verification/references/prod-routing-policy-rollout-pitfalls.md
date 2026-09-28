# Prod routing policy rollout pitfalls

## Scope

Короткая памятка для rollout'а backend routing/policy changes на live Hermes-style contour.

## 1. Policy file may be missing from the live tree

Даже если локально backend уже читает policy-файл, на prod может не существовать сам каталог.
Проверка перед copy:
- существует ли target directory (`services/backend/policies/`);
- если нет — создать его до `scp`/replace.

Иначе rollout ломается не в логике, а в файловой структуре deployment tree.

## 2. Do not guess the service control path

На live host может существовать несколько правдоподобных способов запуска backend:
- systemd system unit;
- user-systemd unit;
- вручную запущенный `waitress-serve`;
- wrapper script.

Сначала выясни фактами:
- `systemctl --user list-units ...`
- `pgrep -af 'waitress|app:app|8791'`
- unit file / launcher script

Потом уже рестартуй.

## 3. Off-process runtime probes may use the wrong env

Если backend запускается через wrapper вроде `run_backend_service.sh` + `scripts/runtime_env.sh`, прямой `python`-probe без этого env может смотреть не в ту БД / не в тот session-secret / не в тот runtime contour.

Симптом:
- helper вроде `issue_session()` отработал;
- live HTTP API отвечает `401` на этот token.

Рабочее правило:
- source тот же runtime env, что и сервис;
- используй тот же `.venv`;
- при сомнениях снимай env из живого процесса `/proc/<pid>/environ`.

## 4. Separate routing success from source-stage failure

Для generic web collection без явных URL важно различать:
- route selected correctly;
- contract built correctly;
- search/source stage actually found candidates.

Если live result = `web_collection_sources_not_found`, а contract и route уже корректны, это не routing regression. Это отдельный blocker класса:
- source discovery;
- provider availability;
- search integration.

## 5. Test-process noise is not automatically runtime failure

Если после успешно завершённого targeted test возникает шум вроде:
- `terminate called without an active exception`
- `Segmentation fault`

не объявляй prod сломанным автоматически.
Сначала отдельно проверь:
- unit test result;
- service process status;
- repeated `/api/health`.

Если service жив и health стабилен, классифицируй это как teardown/probe noise, а не как подтверждённое падение live runtime.
