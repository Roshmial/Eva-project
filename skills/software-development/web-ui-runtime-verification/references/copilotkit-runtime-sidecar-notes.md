# CopilotKit runtime sidecar: local-first verification notes

Короткая памятка для случаев, когда нужно честно подтвердить, что isolated CopilotKit runtime уже отвечает, даже если browser/CDP-проверка недоступна.

## Что подтвердилось в рабочем сценарии

- `GET /copilotkit/info` отвечает `200`.
- `POST /copilotkit` в single-route режиме принимает `method: 'agent/run'` и возвращает `text/event-stream`.
- Живой runtime-ответ можно считать подтверждённым, если пришли события уровня:
  - `RUN_STARTED`
  - `TEXT_MESSAGE_START`
  - `TEXT_MESSAGE_CONTENT`
  - `TEXT_MESSAGE_END`
  - `RUN_FINISHED`

## Критичный mount-паттерн

Если используется `copilotRuntimeNodeExpressEndpoint({ endpoint: '/copilotkit', ... })`, не стоит дополнительно монтировать handler как `app.use('/copilotkit', handler)`.

Надёжный вариант:
- `app.use(handler)`

Причина: endpoint уже знает base path, а повторное mount-prefix повлияло на `req.url` и давало ложные `404` на `agent/run`.

## Минимальный рабочий single-route payload

`method: 'agent/run'` ожидает не произвольный `body`, а структуру, совместимую с `RunAgentInputSchema`.

Минимально рабочий payload:

```json
{
  "method": "agent/run",
  "params": { "agentId": "default" },
  "body": {
    "threadId": "alt-check-thread-ok",
    "runId": "run-ok-3",
    "tools": [],
    "context": [],
    "messages": [
      {
        "id": "m1",
        "role": "user",
        "content": [
          { "type": "text", "text": "Привет. Ответь одним словом: ок." }
        ]
      }
    ]
  }
}
```

## Быстрый локальный schema-probe

Если runtime ругается непонятно, сначала прогнать payload локально через Node:

```js
const { RunAgentInputSchema } = require('@ag-ui/client');
RunAgentInputSchema.parse(payload);
```

Это быстро показывает, что именно отсутствует. В живом кейсе схема требовала обязательные `tools` и `context`, и без них runtime падал ещё до реальной run-логики.

## Telemetry pitfall

Если sidecar падает с ошибкой вида:

- `_copilotkit_shared.lambdaClient.send is not a function`

это telemetry-path, а не бизнес-логика чата.

Практический обход для local-first проверки:

```bash
COPILOTKIT_TELEMETRY_DISABLED=true DO_NOT_TRACK=1 node scripts/copilotkit_runtime_8794.cjs
```

После этого `agent/run` может заработать без изменения продуктовой логики.

## Что считать честной альтернативной приёмкой

Если popup-проверка в браузере недоступна из-за CDP/browser runtime, альтернативная приёмка допустима, только если подтверждены все три слоя:

1. discovery-path жив (`/copilotkit/info`)
2. `POST /copilotkit` принимает реальный `agent/run`
3. получен живой SSE-ответ с текстовым delta/content, а не только `200` без данных
