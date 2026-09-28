# B2B model access and tools: live notes

Use this note when two GigaChat B2B credential sets both mint OAuth tokens but expose different models or different agent behavior.

## Proven comparison pattern

For each credential set:
1. mint OAuth token with `scope=GIGACHAT_API_B2B`
2. call `GET https://api.giga.chat/v1/models`
3. call `GET https://gigachat.devices.sberbank.ru/api/v1/models`
4. probe direct generation on both endpoints
5. if tools matter, test both:
   - OpenAI-style `tools` + `tool_choice`
   - GigaChat-native `functions` + `function_call`

## Interpreting outcomes

### Case A: `/models` on `api.giga.chat/v1` includes `GigaChat-3-Ultra`
Meaning:
- this client/project has model visibility for Ultra in the B2B contour
- direct chat should be tested on `https://api.giga.chat/v1/chat/completions`

### Case B: `/models` excludes `GigaChat-3-Ultra`
Meaning:
- current token does not have Ultra access in this project/client context
- adapter changes will not make the model appear

### Case C: model visible, generation returns `402 Payment Required`
Meaning:
- visibility exists
- generation is blocked by billing/tariff/entitlement

### Case D: model absent, generation returns `404 No such model`
Meaning:
- no model access for this token in this contour

## Endpoint-specific lesson

Observed live pattern:
- `https://api.giga.chat/v1/models` may expose modern B2B models such as `GigaChat-3-Ultra`
- `https://gigachat.devices.sberbank.ru/api/v1/models` may expose a wider list of older/consumer-style models and previews
- these catalogs are not interchangeable; compare both only to diagnose contour differences, but prefer `api.giga.chat/v1` for modern B2B model checks

## Tool-calling lesson

Direct upstream behavior can differ sharply by payload shape.

### What failed agentically
Sending OpenAI-style payload directly upstream:
- `tools`
- `tool_choice`

Observed behavior:
- model returned a normal explanatory text answer
- no structured tool call was triggered

### What worked
Sending GigaChat-native payload directly upstream:
- `functions`
- `function_call="auto"`

Observed behavior:
- first turn returned structured `function_call`
- second turn with `role=function`, `name=<function name>`, and valid JSON string result returned the final assistant answer

## Practical conclusion

If GigaChat looks weak as an agent while another model works in the same product:
- first check whether the client is talking through an adapter that translates OpenAI tool contract into GigaChat function contract
- without that translation, the model may be judged unfairly because the payload shape itself suppresses tool behavior
