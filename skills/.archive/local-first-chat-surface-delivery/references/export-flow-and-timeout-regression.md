# Export flow and timeout regression notes

## Когда открывать эту памятку

Когда chat-first backend начал:
- экспортировать не тот assistant response в `docx/pdf/xlsx/...`;
- строить file-of-file цепочки после `file_response`;
- падать по `timed out` подозрительно ровно через 60 секунд;
- путать кодовый фикс и реальный runtime после выкладки.

## Устойчивый паттерн для export bugs

Проверяй source selection, а не только сам attachment builder.

Минимальные правила отбора export source:
- role = `assistant`;
- исключить `message_kind in {file_response, processing_status}`;
- исключить `meta.error = true` и error/fallback replies;
- исключить пустые/служебные тексты вроде `Готовлю ответ…`;
- исключить fallback `Не удалось получить ответ...`.

Минимальная regression-проверка должна подтверждать:
- `meta.message_kind == file_response`;
- `meta.source == message_export`;
- `meta.exported_message_id` указывает на последний содержательный assistant answer;
- `attachments[0].preview_excerpt` содержит нормальный ответ, а не ошибку/предыдущий export.

## Устойчивый паттерн для timeout bugs

Если пользователь говорит, что timeout «явно ровно 1 минута», сначала проверяй не сеть и не модель, а слои timeout configuration.

Порядок проверки:
1. основной timeout в backend;
2. retry/fallback timeout;
3. env в живом процессе;
4. service wrapper / systemd unit / startup script;
5. реальные `model_attempts[*].timeout_seconds` в probe или тесте.

Типовой запах:
- основной timeout выставлен в 180 секунд;
- retry timeout по умолчанию скрыто режется до 60;
- первая попытка падает ровно через минуту, хотя кажется, что backend ждёт 180.

## Живая проверка после фикса

После деплоя подтверждай все три слоя:
- `py_compile` / smoke tests;
- рестарт сервиса и health-check;
- отдельный probe, который печатает фактические `timeout_seconds` и проверяет export path на изолированном сценарии.

Если локальные тесты и серверный runtime расходятся, доверяй live probe и проверяй env/service chain, а не только код в репозитории.
