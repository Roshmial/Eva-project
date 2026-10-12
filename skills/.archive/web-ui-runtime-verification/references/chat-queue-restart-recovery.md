# Chat queue restart recovery

Когда использовать:
- после reboot/restart пользователь говорит, что задача в веб-чате пропала;
- в UI остался fallback-текст `Не удалось получить ответ. Проверьте отправку сообщения и повторите попытку.`;
- есть подозрение, что background queue была сделана, но после рестарта часть задач зависает.

## Что сначала разделить

Не путай два разных класса проблемы:

1. Downstream timeout
- `chat_tasks.status = error`
- `last_error` содержит что-то вроде `timed out`
- assistant message уже переведено в error-state
- это не потеря очереди, а сбой/таймаут downstream-вызова

2. Broken restart recovery
- задача была в `running` во время остановки backend
- после запуска worker подбирает только `pending`
- `running`-задача не возвращается в обработку и визуально выглядит как «пропала»
- это lifecycle-дефект очереди, а не обязательно проблема Hermes/gateway

## Минимальная живая проверка

1. Посмотреть последние записи в `chat_tasks`.
2. Сравнить `status`, `started_at`, `finished_at`, `last_error`.
3. Проверить последнее assistant-message в этой ветке:
- `pending`
- `processing_status`
- `error`
- `task_id`
- `status_label`
4. Сверить это с логами backend после reboot.

## Durable fix

На старте backend нужен recovery-step до запуска chat worker:
- найти все `chat_tasks`, где `status = running` и `finished_at IS NULL`;
- перевести их обратно в `pending`;
- очистить `started_at`;
- очистить `last_error`;
- вернуть assistant placeholder в ожидающее состояние вроде `Готовлю ответ…`;
- только потом запускать обычный processor, который подбирает `pending`.

## Почему это важно

Без такого шага очередь формально существует, но restart-safe поведение не доказано. Пользователь будет видеть задачу как потерянную, хотя причина в том, что worker умеет продолжать только `pending`, а не восстанавливать прерванные `running`.

## Что говорить пользователю

Формулировка должна разделять:
- что было фактом в конкретном инциденте: timeout или queue-loss;
- что было structural gap в архитектуре очереди;
- что уже исправлено: startup recovery для `running`-задач;
- что ещё может оставаться отдельным follow-up: downstream timeout Hermes/gateway.
