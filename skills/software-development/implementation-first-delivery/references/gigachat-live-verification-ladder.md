# GigaChat live verification ladder

Use this after adapter code and unit tests are already in place.

## Why this matters

In live GigaChat rollouts, three different layers can fail independently:
1. transport trust and CA bundle;
2. OAuth credentials and token issuance;
3. model availability and commercial access for generation.

A green result at one layer does not imply the next layer is ready.

## Recommended live order

1. Health endpoint
- confirm the local adapter process is up;
- verify it exposes the intended OAuth URL, API base URL, and CA bundle path.

2. OAuth token exchange
- call the OAuth endpoint directly from the target server;
- require a real `200` plus `access_token` in the response;
- if this fails, the blocker is still credentials or trust, not the adapter logic.

3. Live model discovery
- use the freshly issued bearer token to call `GET /models` on the provider;
- treat that returned list as the source of truth for model names;
- do not trust stale examples or previous test fixtures.

4. Plain generation
- run a minimal non-tool chat completion against one of the live-listed chat models;
- only a successful generation proves the tenant can actually use chat models.

5. Tool-calling probe
- send a request with `tools` / `tool_choice`;
- verify the adapter emits OpenAI-style `tool_calls` back to the caller.

6. Multi-turn tool-result probe
- send assistant `tool_calls` followed by a `tool` result message;
- verify the adapter maps that round-trip back into the provider format and gets a final assistant answer.

## Important blocker interpretation

- `401 credentials doesn't match db data`
  - OAuth credentials are wrong or no longer valid.
- `404 No such model`
  - requested model name is not available to this tenant; re-check `/models`.
- `402 Payment Required`
  - technical integration may be fine, but generation is blocked by provider billing/commercial state.

## Durable lesson from this session

Do not stop at "token refresh works".
For GigaChat-like providers, normal production-readiness means:
- token refresh works;
- live model name is valid for this tenant;
- generation is commercially enabled;
- tool-calling round-trip is verified end-to-end.
