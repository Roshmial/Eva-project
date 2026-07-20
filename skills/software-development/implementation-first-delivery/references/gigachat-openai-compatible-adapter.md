# GigaChat adapter pattern for OpenAI-compatible downstreams

Use this when the existing app expects an OpenAI-style `POST /chat/completions` downstream with optional Bearer auth, but the target provider requires a separate OAuth token exchange first.

## Problem shape

Existing backend shape:
- sends `model`, `messages`, `stream=false` to `/chat/completions`
- may expect a static `Authorization: Bearer <api_key>`

Provider shape:
- requires OAuth token fetch first
- token fetch uses separate credentials and request headers
- actual generation call then uses a short-lived Bearer token

This mismatch means URL substitution alone is insufficient.

## Minimal safe solution

Insert a thin local adapter/proxy that:
1. exposes `POST /v1/chat/completions`
2. accepts the same request body the current app already sends
3. fetches provider access token on demand
4. caches token until near expiry
5. forwards the request to provider `/chat/completions`
6. returns provider response in the same OpenAI-compatible shape

## GigaChat-specific details confirmed in session

OAuth:
- token endpoint: `https://ngw.devices.sberbank.ru:9443/api/v2/oauth`
- method: `POST`
- auth: `Authorization: Basic <credentials>`
- required header: `RqUID: <uuid4>`
- body: `scope=GIGACHAT_API_PERS`

Chat:
- API base: `https://gigachat.devices.sberbank.ru/api/v1`
- generation endpoint: `POST /chat/completions`
- auth: `Authorization: Bearer <access_token>`

## Delivery pattern that worked

1. Build adapter as a separate runtime unit, not as an invasive backend rewrite.
2. Keep app-facing endpoint OpenAI-compatible: `/v1/chat/completions`.
3. Add token cache with expiry skew.
4. Add a health endpoint.
5. If the existing backend injects Bearer auth unconditionally, add an auth mode like `none|bearer` so it can talk to the adapter without fake credentials.
6. Wire launch script, env example, and systemd unit in the same pass.

## Verification checklist

- targeted tests for token fetch and cache reuse
- targeted test that adapter forwards OpenAI-style payload to provider chat endpoint
- targeted test that backend `auth_mode=none` omits Authorization header
- local probe through real Flask entrypoint:
  - `GET /healthz` returns 200
  - `POST /v1/chat/completions` returns assistant content

## Files produced in the session

Project-local artifact set used as concrete example:
- `services/backend/gigachat_adapter.py`
- `services/backend/test_gigachat_adapter.py`
- `services/backend/test_hermes_api_auth_mode.py`
- `run_gigachat_adapter_service.sh`
- `deploy/package/systemd/hermes-web-gigachat-adapter-8795.service`

Use this as a reference pattern, not as a universal provider abstraction.
