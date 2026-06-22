# Telegram singleflight runtime notes

Когда использовать:
- запросы `source_kind=telegram` идут не напрямую в локальную библиотеку, а через внешний TG API /export;
- TG API фактически однопоточный и следующий export может падать, если предыдущий ещё не завершился;
- в user-path наблюдаются timeout/error после корректного clarification flow.

Устойчивый паттерн:
1. Не считать проблему purely-LLM. Сначала проверить operational constraint внешнего collector-а.
2. На backend-стороне держать singleflight lock для Telegram export execution.
3. Второй запрос не должен запускать параллельный `/export`; он должен ждать освобождения lock в пределах контролируемого timeout.
4. В публичном результате сохранять observability:
   - `execution_lock.kind`
   - `execution_lock.wait_seconds`
   - `execution_lock.timeout_seconds`
5. Для timeout ожидания отдавать отдельный человеческий public error text, а не сырой transport/runtime текст.

Что проверять после фикса:
- прямой Telegram collection request с полным контрактом проходит до `collection_execution_result`;
- two-step flow `общий запрос -> clarification -> конкретизация` больше не срывается на overlap export-вызовов;
- в meta видно, что singleflight реально участвовал в execution path;
- server-side тесты покрывают:
  - ожидание lock;
  - public error text для busy-timeout.

Что не делать:
- не отправлять несколько backend `/export` параллельно в single-threaded TG API;
- не списывать timeout такого класса на weak LLM без runtime-проверки;
- не считать корректный clarification достаточным доказательством, если downstream export execution path всё ещё может конфликтовать сам с собой.
