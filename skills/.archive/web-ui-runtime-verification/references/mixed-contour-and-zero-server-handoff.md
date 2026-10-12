# Mixed contour and zero-server handoff notes

Короткая выжимка из runtime-приёмки Hermes Web React 8793.

## 1. Не принимай mixed contour

Типичный ложноположительный сценарий:
- frontend уже обслуживается из нового дерева проекта;
- backend на целевом порту всё ещё поднят из старого каталога;
- браузер визуально открывается, но verdict относится к смешанному контуру.

Минимальная проверка перед финальным verdict:
1. найти PID на backend-порту;
2. посмотреть `cwd` процесса;
3. посмотреть `HERMES_WEB_*` env именно у этого PID;
4. сверить их с целевым репозиторием и expected DB/env.

## 2. Проверяй не только процессы, но и `systemd --user`

Если сервисы держатся через user systemd:
- проверяй `WorkingDirectory` и `ExecStart` unit-файлов;
- проверяй `systemctl --user status` и restart-loop;
- помни, что вручную убитый legacy backend может автоматически вернуться через restart policy.

Практический симптом:
- новый backend-процесс падает с `Address already in use`;
- причина не в коде, а в том, что порт уже удерживает unit старого или параллельного контура.

## 3. Разделяй manual dev runtime и healthy systemd runtime

Если `vite` вручную поднимается и принимает HMR-изменения, это ещё не значит, что frontend-service здоров.

Для приёмки различай:
- manual dev runtime works;
- systemd frontend unit healthy.

Отдельный анти-паттерн:
- frontend-service в restart-loop только потому, что порт уже занят вручную поднятым Vite.

## 4. Для передачи на новый пустой сервер нужен отдельный deployment layer

Local runtime acceptance ещё не означает переносимую систему.

Минимум, который стоит передавать вместе с кодом:
- dependency inventory;
- env-example;
- zero-server checklist для Hermes;
- bootstrap-script для свежего Hermes;
- install-project-deps script;
- systemd user units;
- verify-deployment script;
- явная пометка first-run режима: `HERMES_WEB_ENABLE_DEMO_DATA=1` для demo-seed или production-like вариант без него.

## 5. First-run поведение backend тоже часть handoff

Для этого класса local-first backend важно отдельно зафиксировать:
- создаёт ли пустая БД стартовых пользователей сама;
- от какого env-флага это зависит;
- какими учётками можно пройти smoke на fresh server.

В текущем кейсе это было критично для нулевого сервера с новым Hermes.