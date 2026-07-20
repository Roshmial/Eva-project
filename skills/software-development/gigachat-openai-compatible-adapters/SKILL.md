---
name: gigachat-openai-compatible-adapters
description: Dovodit local adapter/proxy between Hermes or other OpenAI-style clients and GigaChat, including OAuth token lifecycle, model availability checks, and tool-calling normalization.
---

# Purpose

This skill covers the class of tasks where an existing system expects an OpenAI-style chat endpoint, but the real upstream is GigaChat with its own OAuth flow, model catalog, and function-calling contract.

Use it for:
- Hermes routed through a custom OpenAI-compatible GigaChat adapter
- local proxies exposing `/v1/chat/completions`
- incidents where chat works inconsistently across restarts or token refreshes
- debugging `No such model`, `Payment Required`, or tool-calling mismatches

# Core rule

Separate three layers before changing code:
1. auth works or not;
2. model is actually available to the issued token or not;
3. adapter contract is correct or not.

Do not collapse these into one vague "GigaChat integration is broken" diagnosis.

# Minimal architecture

Preferred contour:
- client side keeps OpenAI-style `POST /v1/chat/completions`
- local adapter fetches OAuth token from GigaChat
- adapter caches token until near expiry
- adapter forwards generation requests to GigaChat
- adapter normalizes function/tool traffic both directions

This keeps the main app unchanged and local-first.

# Required verification order

## 1. Verify OAuth independently

Before touching model names or prompting, prove token issuance with the exact Basic credentials and scope used by the runtime.

Expected shape:
- `POST https://ngw.devices.sberbank.ru:9443/api/v2/oauth`
- `Authorization: Basic <base64(client_id:secret)>`
- `RqUID: <uuid>`
- `scope=<scope>`

Interpretation:
- `401 credentials doesn't match db data` -> Basic credentials are invalid for OAuth; this is not a token-refresh problem
- `200` with `access_token` -> auth layer is healthy enough to continue

## 2. Verify `/models` with the newly issued token

Always call the model-list endpoint with the fresh token before blaming the adapter.

Why this matters:
- a model can disappear for the currently issued token even when yesterday's long-lived process seemed to work
- a restart can expose that the old process had a previously issued token with different effective entitlements or timing
- this distinguishes "adapter bug" from upstream entitlement or billing issues

Interpretation:
- model absent from `/models` -> treat as access/entitlement issue first
- model present in `/models` but generation fails -> then inspect payload shape or adapter routing

## 3. Verify generation directly against upstream

Probe upstream directly with the same token and model before debugging the adapter.

Typical meanings:
- `404 No such model` -> the token does not see that model in this contour
- `402 Payment Required` -> model family is reachable but blocked by billing/tariff
- `400 invalid JSON syntax` -> request shape mismatch for that API version

## 4. Only then debug the adapter contract

If auth, `/models`, and direct generation are healthy, inspect the adapter:
- OpenAI `tools` -> GigaChat `functions`
- OpenAI `tool_choice` -> GigaChat `function_call`
- assistant `tool_calls` -> assistant `function_call`
- tool result message -> GigaChat `function` role message
- upstream function response or XML tool-call block -> OpenAI `tool_calls`

# B2B endpoint and model-access rules

## Canonical B2B endpoint for modern model access

For B2B checks, prefer:
- `https://api.giga.chat/v1`

Do not assume the older consumer-style endpoint is equivalent for model visibility.
In a validated live case:
- `api.giga.chat/v1/models` exposed `GigaChat-3-Ultra`
- `gigachat.devices.sberbank.ru/api/v1/models` did not expose `GigaChat-3-Ultra`
- direct generation of `GigaChat-3-Ultra` succeeded only through `https://api.giga.chat/v1/chat/completions`

Operational rule:
- if the target is a B2B project and the desired model is `GigaChat-3-Ultra` or newer families, test `api.giga.chat/v1` first and treat it as the default contour unless proven otherwise

## Distinguish model visibility from generation entitlement

A useful split from live checks:
- model absent from `/models` + `404 No such model` -> missing model access for this client/project
- model present in `/models` + `402 Payment Required` -> model is visible but generation is blocked by billing/tariff

This distinction is stronger than generic "credentials work / do not work" thinking and should shape the escalation message.

## Compare credentials by client/project context, not just by secret validity

When two valid B2B credential sets behave differently, treat them as different access contexts.
A durable debugging pattern is:
1. prove both keys can mint OAuth tokens;
2. compare `/models` on `api.giga.chat/v1` for each key;
3. compare direct generation for the same model;
4. only then conclude whether the difference is endpoint-related or entitlement-related.

If one key sees `GigaChat-3-Ultra` in `/models` and another does not, the decisive factor is client/project access context.

# Tool-calling contract rules

## Do not expect direct OpenAI `tools` payloads to behave agentically upstream

A live GigaChat `GigaChat-3-Ultra` check showed:
- sending OpenAI-style `tools` + `tool_choice` directly to upstream returned a normal text answer and did not trigger tool execution
- sending GigaChat-native `functions` + `function_call="auto"` triggered a real `function_call` response
- sending the second turn with `role=function` and valid JSON function result produced the final assistant answer

Operational rule:
- if you are talking to upstream GigaChat directly, test tool calling with `functions` / `function_call`, not with OpenAI `tools` / `tool_choice`
- if your client speaks OpenAI tools, the adapter must perform this translation layer; otherwise the model may look worse at agent work than it actually is

## Verify the second turn explicitly

Tool-calling is not proven by the first `function_call` alone.
Always send a second request with:
- assistant message containing the returned `function_call`
- `role=function`
- `name=<function name>`
- `content=<valid JSON string result>`

If the function result is malformed JSON, upstream can reject it with `422 INVALID_PARAMS`.
So the second-turn validation must include strict JSON serialization, not hand-written pseudo-JSON.

# Durable pitfalls

## Pitfall: treating token refresh as the root cause when Basic credentials are wrong

If OAuth itself returns `401`, the issue is upstream credentials, not the 30-minute token TTL.
A correct adapter should already refresh tokens automatically based on expiry.

## Pitfall: assuming yesterday's working model remains available after restart

When a service was alive yesterday and fails today after restart, do not assume the adapter regressed.
First check whether the newly minted token sees the same model in `/models`.

## Pitfall: trusting a configured model name without verifying current availability

A model string in `.env` or old tests is not proof of availability.
Treat `/models` plus a direct generation probe as source of truth.

## Pitfall: mixing auth success with model entitlement success

OAuth `200` only proves token issuance.
It does not prove access to a specific chat model.

# Implementation checklist

1. Add token cache with expiry skew.
2. Keep adapter-facing endpoint OpenAI-compatible.
3. Normalize tool/function traffic both directions.
4. Add targeted tests for:
   - token fetch and cache reuse
   - tool/function request mapping
   - tool result round-trip mapping
   - XML or non-standard tool-call fallback if provider emits it
5. Verify on the target runtime in this order:
   - OAuth
   - `/models`
   - direct upstream generation
   - adapter health
   - adapter chat
   - adapter tool-calling

# References

- `references/gigachat-hermes-runtime-triage.md` — compact runtime triage notes: OAuth vs `/models` vs model access vs billing vs adapter contract.
- `references/b2b-model-access-and-tools.md` — live comparison pattern for multiple B2B credential sets, endpoint-specific model visibility, and direct upstream tool-calling behavior.
