# Admin policy/sources live acceptance: contour sync + backend-first round-trip

Когда применять:
- проверка admin-блока policy/sources в local-first web UI;
- frontend и backend могут идти из разных рабочих деревьев или разных runtime-контуров;
- меняется registry источников данных и есть риск silent-loss при сохранении policy;
- browser acceptance нестабилен, но backend/API уже живы.

## 1. Сначала доказать, что frontend и backend действительно из одного канонического контура

Не принимать admin UI, пока не проверено:
- какой frontend реально слушает product-port;
- какой backend реально слушает API-port;
- из какого cwd/дерева поднят backend-процесс;
- совпадает ли это с редактируемым репозиторием.

Практический сигнал риска:
- UI уже показывает новые элементы,
- а backend всё ещё обслуживается из старого дерева,
- из-за чего live acceptance становится ложноположительной или ложноотрицательной.

Минимальная проверка:
- PID backend-процесса;
- `cmdline` процесса;
- `cwd` процесса;
- `service-info`/health route с нужного порта.

## 2. Для policy/sources обязателен backend round-trip, а не только визуальный осмотр

Даже если UI выглядит корректно, acceptance должна включать:
1. login;
2. `GET /api/admin/dashboard-policy`;
3. `PATCH /api/admin/dashboard-policy` с реальным изменением;
4. повторный `GET`;
5. rollback;
6. финальный `GET`.

Нужно проверять не просто status=200, а сохранение фактического множества `allowed_sources` и `default_global_source`.

## 3. При переходе от частных датасетов к registry-классам источников проверять legacy-key compatibility

Типовой риск:
- старая policy хранит ключ вроде `telegram_digest`;
- новый registry уже живёт на уровне более общих source classes;
- при `PATCH` старый ключ silently выпадает из `allowed_sources`, потому что его нет среди активных canonical items.

Это не UI-баг, а data-compatibility defect.

Что делать:
- ввести явную canonicalization/alias-layer для legacy source keys;
- прогонять round-trip тест, который доказывает, что legacy key либо сохраняется канонически, либо предсказуемо маппится, но не теряется молча.

Хороший паттерн:
- `telegram_digest -> local_dataset_registry`
- `telegram -> telegram_api_connector`
- `google -> google_api_connector`
- `public_procurement -> public_procurement_connector`

Смысл не в конкретных названиях, а в том, что migration должна быть явной и тестируемой.

## 4. Если browser/runtime path нестабилен, не бросать приёмку — перейти на backend-first acceptance

Когда headless browser:
- стартует нестабильно,
- закрывает page после login/admin render,
- блокируется на fontconfig/skia/runtime слоях,

не останавливать проверку на уровне «UI не получилось открыть». Сначала добить:
- live API login;
- admin policy round-trip;
- registry sync routes (`/admin/user-sources` и связанные payload);
- request-level override path (`explicit_source_ids`).

Это даёт реальное доказательство рабочей модели даже до финальной визуальной приёмки.

## 5. Для dashboard-policy отдельно проверять request-level override

Если в модели появился request-level source override, acceptance должна подтверждать:
- payload принимает `explicit_source_ids`;
- legacy `allowed_source_ids` не ломает обратную совместимость;
- meta/policy в результате показывает фактически применённый override, а не только дефолт policy.

Минимальный позитивный сценарий:
- `source_mode=global_only`
- `explicit_source_ids=["web_research"]`
- ответ возвращает dashboard/meta с `allowed_sources=["web_research"]` и тем же `explicit_source_ids`.

## 6. Что считать хорошим итогом

Хорошая приёмка для этого класса задач — это не только «экран открылся», а связка:
- contour sync доказан;
- registry inventory соответствует реальным platform-level connector classes;
- policy round-trip проходит без silent-loss;
- legacy keys канонизируются предсказуемо;
- request-level override подтверждён live API/test path;
- browser/UI acceptance либо пройдена, либо честно отделена как оставшийся визуальный слой, а не смешана с backend-моделью.