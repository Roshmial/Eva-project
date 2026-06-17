# Runtime error fallback, HTML-safe public errors, and remote user-systemd control

Когда local-first web backend проксирует LLM/runtime-ошибки в пользовательский chat/UI, отдельно проверяй три слоя.

## 1. Fallback по модели должен быть узким и наблюдаемым

Если задача звучит как `переключаться на следующую модель при runtime error`, не делай бесконтрольный retry по любому исключению.

Надёжный инвариант:
- первая модель пробуется штатно;
- только первый retryable `runtime error` даёт один автопереход на следующую модель-кандидат;
- другие ошибки (`auth`, `validation`, произвольные backend defects) не маскируются цепочкой retries.

Для audit/debug сохраняй в message/task meta минимум:
- `requested_model`;
- `fallback_used`;
- `model_attempts`;
- фактическую модель ответа (`hermes_model` или эквивалент).

Это позволяет потом доказать не только `работает`, но и какой именно маршрут реально сработал.

## 2. Публичный error path отделяй от диагностического

Если upstream иногда возвращает HTML вместо JSON/API-ответа, не пиши сырой `str(exc)` в user-visible `error_text`.

Устойчивый паттерн:
- оригинальную ошибку сохранять в diagnostic path (`raw_error_text`, task `last_error`, logs);
- user-facing текст нормализовать до короткой продуктовой формулировки.

Минимально полезные правила нормализации:
- если виден HTML (`<html`, `<!doctype html`, `<body`, `<head`) -> `Ошибка runtime: вместо API-ответа вернулась HTML-страница.`;
- если техническая ошибка чрезмерно длинная -> вернуть короткий нейтральный текст, а не полотно;
- пустой/непонятный случай -> нейтральная product error без сырых фрагментов ответа.

Это особенно важно, если ошибка потом уходит не только в web UI, но и дальше в Telegram/внешний клиент.

## 3. Для remote Hermes Web через systemd --user не управляй сервисом как root-session по инерции

Если backend/frontend на удалённом хосте живут как `systemd --user` units пользователя `hermes`, команды вида `systemctl --user restart ...` из root-shell могут дать ложный вывод:
- `Unit ... not found`;
- `Failed to connect to bus: No medium found`.

Надёжный remote-path:
- найти uid пользователя сервиса;
- выставить `XDG_RUNTIME_DIR=/run/user/<uid>`;
- выставить `DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/<uid>/bus`;
- запускать `runuser -u hermes -- systemctl --user ...`.

Практически это нужно для:
- `restart`/`stop`/`disable --now`;
- `is-active`/`list-units`;
- проверки, что после отключения runtime-порта действительно не слушаются.

## 4. После runtime-правки проверяй не только health

`/api/service-info` полезен, но недостаточен.

Минимальный acceptance после таких изменений:
- regression test на fallback/path нормализации ошибок;
- compile/syntax pass;
- restart именно целевого user-unit;
- `service-info`/health;
- при необходимости live task/message round-trip или log/meta proof, что в ответе сохранились `model_attempts` и не утёк raw HTML.
