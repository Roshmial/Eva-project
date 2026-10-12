# Chat pending refresh vs backend completion

## Когда использовать

Когда пользователь жалуется, что в Hermes Web ответ от модели уже фактически готов, но чат продолжает висеть в состоянии `Готовлю ответ…` / `ожидаю ответа` до ручного refresh.

## Проверенный diagnostic path

1. Сначала проверить frontend-код отправки сообщения и life-cycle pending assistant message.
2. Найти, как именно UI ждёт завершение задачи:
   - bounded polling после submit;
   - background polling по active thread;
   - SSE/WebSocket/push.
3. Отдельно проверить прод-данные по `chat_tasks` и связанным assistant messages:
   - `status`
   - `created_at`
   - `started_at`
   - `finished_at`
   - `assistant_message_id`
   - `messages.meta_json`
4. Сравнить фактическую длительность backend task с лимитом фронтового polling.

## Живой паттерн, найденный в этой сессии

Во frontend React был путь:
- optimistic assistant placeholder `Готовлю ответ…`
- затем `refreshThreadUntilSettled(...)`
- внутри него only bounded polling: `20` попыток × `1500 ms` ≈ `30 секунд`

В проде backend реально завершал задачи дольше этого окна:
- один task завершился примерно за `86 секунд`
- другой — примерно за `149 секунд`

Следствие:
- backend уже записал финальный assistant message с `pending=false` и `processing_status=completed`
- но frontend уже перестал опрашивать thread
- пользователь видел зависшее состояние до ручного обновления

## Устойчивый repair pattern

Не полагаться только на submit-scoped bounded polling.

Нужен второй слой:
- background refresh активного thread, пока в `appState.messages` есть assistant message с `meta.pending=true`
- защита от параллельных overlapping fetch (`inFlight` guard)
- автоостановка polling, когда pending-сообщений больше нет
- cleanup timer при unmount / смене active thread

Минимальный рабочий подход для React:
- `useRef` для `{ inFlight, timer }`
- `useEffect`, завязанный на `authenticated`, `activeThreadId`, `messages`
- `setInterval` с умеренным шагом, например `5000 ms`
- каждый тик обновляет `threads`, `thread`, `files`
- после получения thread проверяет, остался ли `pending assistant`

## Что важно не перепутать

- Это не тот же класс проблемы, что backend timeout.
- Если в БД `chat_tasks.status=completed`, а UI всё ещё pending, это frontend state-refresh defect.
- Если в БД `status=error` и `last_error='timed out'`, это уже backend/downstream problem, не лечится одним polling-фиксoм.

## Acceptance

После фикса нужно подтвердить три вещи:
1. Новый production bundle реально выкачен на live frontend.
2. В прод-БД есть задачи дольше первоначального submit-window.
3. При длинной задаче active chat сам снимает pending-state без ручного refresh страницы.
