---
name: local-first-runtime-acceptance-and-deploy-packaging
description: "Доводит local-first web/runtime контур до реально приемочного состояния: выравнивает project root, проверяет live runtime, оформляет deploy-пакет и полную эксплуатационную документацию."
---

# Когда применять

См. также: `references/admin-tabs-headless-async-overwrite.md` — разбор случая, где headless click по admin tabs выглядел как UI-баг, но корень был в async overwrite `admin.section`, и как после продуктового фикса вернуть smoke от `localStorage + reload` обратно к обычному tab-click.


Используй навык, когда нужно не просто "починить код", а довести local-first web-систему до состояния, пригодного для приёмки и переноса на другой сервер:
- есть frontend/backend/runtime на разных портах или в разных процессах;
- нужно доказать, что live runtime действительно использует один и тот же project root;
- нужно завершить не только код, но и deployment docs, user-testing scenario и deploy package;
- есть риск ложной приёмки из-за смешанного контура, старых systemd unit'ов или ручных процессов.

# Цель

Получить не декларацию, а проверенный результат:
- код собран;
- runtime поднят на каноническом контуре;
- live API/UI path проверен;
- документация описывает систему целиком, а не только последние фиксы;
- есть deploy-пакет, пригодный для переноса на другой сервер.

# Основной протокол

## 1. Сначала выровняй канонический runtime contour

Для каждого порта/процесса проверь:
- какой process слушает порт;
- из какого `cwd` он запущен;
- какой `ExecStart` прописан в user-systemd unit;
- нет ли ручного dev-процесса, который маскирует сервисный runtime.

Нельзя считать приёмку валидной, пока не доказано, что frontend, backend и вспомогательный runtime относятся к одному project root.

## 2. Не ограничивайся file-level проверкой

После правок обязательно делай оба слоя верификации:
- build/syntax/test;
- live runtime/API/UI acceptance.

Минимум:
- backend compile/syntax check;
- frontend build;
- smoke/backend tests;
- live HTTP checks;
- login и read/write/read path для ключевого admin/user сценария.

## 3. Для policy/inventory систем разделяй user-layer и admin-layer

Если система управляет источниками данных, policy, inventory или connector groups:
- user-layer должен видеть только прикладные режимы;
- admin-layer должен владеть inventory, allowed sources и classification overrides;
- explicit file/link/dataset/connector — это request-level override, а не отдельный глобальный режим.

## 4. Проверяй round-trip, а не только PATCH 200

Для важных настроек делай минимум:
- `GET` текущего состояния;
- `PATCH`/`POST` изменения;
- повторный `GET` с проверкой, что изменение реально отражено в runtime payload;
- при необходимости restore исходного состояния.

Это особенно важно для:
- dashboard policy;
- source inventory;
- connector classification;
- admin notices;
- feature toggles.

## 5. Если есть runtime mismatch — сначала устрани его, потом продолжай приёмку

Типовой анти-паттерн:
- frontend уже идёт из нового проекта;
- backend всё ещё работает из старого каталога через legacy unit или старый процесс.

В таком случае:
1. останови конфликтующий процесс/сервис;
2. проверь user-systemd unit;
3. выполни `daemon-reload` и `restart`;
4. заново проверь `cwd`, `ExecStart`, порты и HTTP ответы.

## 6. Документация должна быть системной

После технической приёмки оформи не changelog, а комплект эксплуатационных документов:
- короткий `README` как точка входа;
- полное системное описание;
- deployment guide для нового сервера;
- user testing scenario для первого знакомства с системой;
- deploy package README.

## 7. Deploy package делай как явный каталог артефактов

В пакет обычно входят:
- env example;
- systemd unit templates;
- install script;
- verify/smoke script;
- README с порядком применения.

Если архив не собран, но каталог артефактов уже готов, это всё равно полезный промежуточный deliverable — но в финальном отчёте надо честно отделять готовый каталог от проверенного archive artifact.

## 8. Для short-lived внешнего теста на отдельном сервере предпочитай direct-IP contour, а не quick tunnels

Если у пользователя есть фиксированный IP на тестовом сервере и он не хочет:
- выдавать тестировщикам SSH-доступ;
- поднимать домен;
- зависеть от временных tunnel URL,

то базовым сценарием считай прямую публикацию стенда по IP.

Практический порядок:
- снаружи публикуй один пользовательский вход, а не набор внутренних портов;
- frontend можно временно открыть на `0.0.0.0`, если это short-lived pilot и нет готового reverse proxy;
- backend и вспомогательные runtime-порты по возможности оставляй на `127.0.0.1`;
- если frontend ходит в backend через same-origin proxy (`/api`), отдельно проверь, что backend CORS/allowed origins включают внешний `http://<ip>:<port>` или `http://<ip>`;
- после изменения bind/CORS не ограничивайся локальным `curl`: перепроверь внешний HTTP-ответ по публичному IP, `ss -ltnp` и `systemctl --user status`.

Это не production-pattern по умолчанию, а pragmatic pilot contour на 1–2 недели. Для него важнее предсказуемый URL и независимость от чужого tunnel lifecycle, чем идеальная инфраструктурная чистота.

# Пошаговый шаблон работы

1. Проверить порты, процессы, `cwd`, unit files.
2. Убрать конфликтующие ручные процессы.
3. Выровнять user-systemd services на один project root.
4. Довести код и API contract.
5. Прогнать build/syntax/tests.
6. Прогнать live login + key save/read round-trip.
7. Если есть source policy — отдельно проверить реальное изменение runtime payload и restore.
8. Подготовить системную документацию.
9. Подготовить deploy package.
10. Зафиксировать решение в decision-log.

# Питfalls

- `200 OK` на PATCH ещё не значит, что runtime реально применил изменение.
- Нельзя верить только frontend-экрану, если backend может жить из другого каталога.
- Ручной Vite/dev server часто маскирует проблемы service-run контура.
- Для local-first контуров root cause часто не в UI, а в смешанном runtime или гонках вокруг локальной БД.
- Пользовательский тестовый сценарий должен быть написан для роли user, без протаскивания admin-терминов и внутренних technical keys.

# Артефакты навыка

См. `references/runtime-mismatch-and-packaging-checklist.md` — короткий reference по признакам смешанного контура, проверкам round-trip и составу deploy-пакета.
См. `references/fixed-ip-temporary-pilot.md` — short-lived схема публикации стенда по фиксированному IP без домена и без SSH-доступа для тестировщиков.

# Критерий завершения

Задача считается доведённой, когда есть одновременно:
- зелёные build/syntax/tests;
- подтверждённый live runtime на канонических портах;
- проверенный прикладной round-trip по ключевому сценарию;
- системная документация;
- deploy package для переноса на другой сервер.
