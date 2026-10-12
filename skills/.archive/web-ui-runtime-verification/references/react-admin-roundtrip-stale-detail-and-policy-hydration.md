# React admin round-trip: stale jobs detail vs hydrated admin policy

Когда использовать:
- live runtime уже выровнен и базовый `quick_triage` зелёный;
- chat/profile/jobs/admin smoke доходит до рабочих экранов, но валится на одном-двух stateful местах;
- нужно отличить acceptance drift от реального UI-багa.

## Сигналы, которые оказались полезными

### 1. Policy/admin overview
Если live admin overview показывает:
- `Источники пока не настроены`;
- `0` внутренних коннекторов;
- `0` внешних коннекторов;

это ещё не доказывает пустой backend.

Сначала сделай прямой live `GET /api/admin/dashboard-policy` на том же contour.

Если API в тот же момент возвращает непустой `data_sources` (в сессии было `data_sources_len = 5`), это сильный сигнал frontend hydration defect:
- backend canonical inventory жив;
- policy route жив;
- проблема в admin overview render/hydration, а не в самом PATCH/GET policy path.

### 2. Jobs detail после pause
В этой сессии backend переводил job в `paused`, но detail-панель оставалась stale:
- список задач уже показывал `на паузе`;
- backend status был `paused`;
- detail всё ещё держал кнопку `Приостановить задачу` вместо `Возобновить задачу`.

Это важный признак: list и detail живут в разных state-path, и refresh выбранной сущности не происходит автоматически.

Такой кейс не надо описывать как `resume не работает`.
Правильнее: `pause backend-path жив, но detail UI не перерисовывается после write-action`.

## Практический приём диагностики

1. Сначала докажи backend-path отдельно.
- Для policy: `GET/PATCH/GET/restore`.
- Для jobs: create -> pause -> проверить status по API.

2. Потом сравни два UI-слоя, а не один.
- list summary;
- detail panel.

3. Если list и backend уже изменились, а detail нет — это UI refresh defect.

4. Не лечи такой кейс только увеличением таймаутов.
Сначала зафиксируй, какая конкретно кнопка/плашка осталась stale, и только потом правь refresh path.

## Приёмка smoke-сценария

Не держи в одном проходе sequence вида:
- create job;
- rename/display_name;
- reload;
- reopen detail;
- pause;
- resume;
- дальше admin.

Это слишком чувствительно к versioning, stale detail и optimistic-concurrency.

Надёжнее разнести на слои:
- jobs create/open detail;
- jobs pause/resume;
- jobs rename/display_name;
- admin overview/users/operations/references.

Если длинный smoke падает, а targeted probe уже доказал backend write-path, сначала фиксируй продуктовый stale-state bug, а не пытайся бесконечно стабилизировать весь monolith.
