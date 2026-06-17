# Admin overview timeseries + admin-only cleanup

Короткие lessons learned для local-first Hermes Web MVP.

## 1. Time-series overview проверяй в два слоя

Сначала backend truth:
- новый endpoint вида `/api/admin/overview-timeseries?granularity=day|week|month` должен отдельно проверяться authenticated HTTP-вызовами;
- для каждого режима ожидай `200` и непустой/осмысленный `buckets` payload;
- примеры bucket-labels:
  - day -> `23.05`
  - week -> `16.03–22.03`
  - month -> `07.2025`

Только потом browser/UI:
- открытие `Управление -> Обзор`;
- проверка SVG/chart-card рендера;
- переключение selector `день/неделя/месяц`;
- проверка отсутствия JS-ошибок.

## 2. Если endpoint внезапно 404

Не делай вывод, что route не добавлен.

Сначала проверь:
- не висит ли stale backend process на том же порту;
- точно ли live runtime перезапущен после патча;
- совпадает ли runtime origin / backend process truth с тем, который проверяешь.

Для local-first web MVP это типовая причина ложной диагностики.

## 3. Если endpoint 500 после успешного reload

Сначала смотри live log процесса.

Типовой класс причин:
- новый route вызвал helper в несовместимой сигнатуре;
- проблема в backend payload builder, а не во frontend.

Идея: сначала восстановить корректный JSON contract, потом уже дебажить UI.

## 4. Cleanup пользователей: сначала soft-delete, потом optional hard cleanup

Если пользователь говорит «оставь только admin», безопасный порядок такой:
1. получить список через admin API;
2. оставить admin;
3. остальных перевести через поддержанный admin update path в `status=deleted`;
4. проверить, что UI/API уже показывает их как deleted/inactive;
5. только если действительно нужен физический cleanup, идти в прямой SQL.

Это уменьшает риск сломать runtime-контур раньше времени.

## 5. Для прямого SQL не предполагай default schema

В этом контуре live DuckDB может хранить operational tables не в default schema, а под `app.*`.

Проверка:
- сначала `SHOW ALL TABLES`;
- затем обращение как `app.users`, `app.sessions`, `app.jobs`, и т.д., если таблицы не видны без schema prefix.

Сигнал ошибки диагностики:
- `Table with name users does not exist! Did you mean "app.users"?`

Это не означает пустую или не ту БД; это может быть просто schema-qualified layout.

## 6. Runtime DB path надо подтверждать, а не угадывать

Перед hard cleanup полезно подтвердить live DB path из самого backend-модуля/конфига, а не предполагать по имени файла.

Только после этого:
- делать backup;
- удалять non-admin users и связанные sessions/history/files/jobs-записи;
- повторно прогонять admin/users + overview + operations UI.
