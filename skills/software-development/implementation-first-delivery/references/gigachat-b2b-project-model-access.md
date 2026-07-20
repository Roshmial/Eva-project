# GigaChat B2B adapter: project-scoped model access and verification

Use this note when a GigaChat adapter appears healthy but a target model is intermittently unavailable.

## Durable lessons from live verification

1. Separate four checks strictly:
   - OAuth token exchange works
   - `/models` returns the tenant-visible model list
   - plain generation succeeds for the requested model
   - tool-calling round-trip works

2. Do not treat OAuth success as evidence that a specific chat model is available.
   - A B2B key can mint a valid `access_token`
   - `/models` can still omit the expected model
   - `POST /chat/completions` can return `404 No such model`

3. In GigaChat B2B work, model visibility behaves like project/client-scoped access.
   - `Authorization key` is derived from `client_id:client_secret`
   - the resulting token reflects that client/project context
   - two different client IDs can plausibly see different model sets

4. For B2B defaults, prefer:
   - API base URL: `https://api.giga.chat/v1`
   - OAuth scope: `GIGACHAT_API_B2B`

5. Eliminate stale consumer defaults from runtime templates.
   - A live process may be correct because `.env` overrides the old value
   - but future restarts or fresh deployments can regress if templates still default to the consumer endpoint

## Fast live verification ladder

1. OAuth:
   - `POST https://ngw.devices.sberbank.ru:9443/api/v2/oauth`
   - confirm `200` and `access_token`

2. Models:
   - `GET https://api.giga.chat/v1/models`
   - inspect the actual returned `id` list
   - choose the chat model from that live list, not from stale notes or yesterday's config

3. Generation:
   - `POST https://api.giga.chat/v1/chat/completions`
   - start with a minimal single-user-message payload

4. Tool calling:
   - only after step 3 succeeds
   - verify request-side `tools -> functions` mapping
   - verify response-side `function_call/XML fallback -> tool_calls`

## Interpretation guide

- `401` on OAuth: bad credentials, wrong client context, or wrong scope
- `/models` succeeds but target model missing: likely project/client entitlement issue
- `404 No such model`: requested model unavailable to that token
- `402 Payment Required`: commercial/billing blocker after auth and routing are already correct

## Config hygiene rule

When fixing a GigaChat contour, patch all three layers in the same pass:
- runtime defaults/script
- env example/template
- adapter code defaults

Then add a regression test that sources the runtime script in a clean environment and asserts the canonical B2B defaults.