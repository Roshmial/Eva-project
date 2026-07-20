# GigaChat prod adapter rollout notes

Use this reference when wiring GigaChat into a real production contour through an OpenAI-compatible adapter.

## Proven rollout sequence

1. Verify access to the named target host first.
2. Back up remote files before overwriting runtime code or env.
3. Deploy adapter code, launch script, env wiring, and service unit together.
4. Verify certificate handling from the target host before troubleshooting auth.
5. Verify OAuth/token acquisition path.
6. Run one real `/v1/chat/completions` request through the deployed adapter.
7. Only then report production status.

## GigaChat-specific transport/auth requirements

- GigaChat uses OAuth token acquisition via `POST /api/v2/oauth`.
- OAuth request requires `Authorization: Basic <base64(client_id:secret)>`.
- OAuth request also requires `RqUID`.
- Chat generation uses `POST /api/v1/chat/completions` with `Authorization: Bearer <access_token>`.
- For Linux runtimes without system trust-store changes, a per-service CA bundle is a practical fallback.

## Certificate handling pattern that worked

When `sudo` access for system trust-store changes is unavailable:
- store the Russian trusted certificates under a service-owned path such as `$HOME/.hermes/certs/gigachat/`;
- build a bundle file such as `russian-trusted-ca-bundle.crt`;
- point the adapter to it via an env like `GIGACHAT_ADAPTER_CA_CERT_FILE`;
- prove the TLS handshake from the target host with Python `ssl.create_default_context(cafile=...)` before moving on.

## Runtime variables used by the adapter

- `GIGACHAT_ADAPTER_CREDENTIALS`
- `GIGACHAT_ADAPTER_SCOPE`
- `GIGACHAT_ADAPTER_CA_CERT_FILE`
- `GIGACHAT_ADAPTER_OAUTH_URL`
- `GIGACHAT_ADAPTER_API_BASE_URL`
- `GIGACHAT_ADAPTER_VERIFY_SSL`
- `GIGACHAT_ADAPTER_TIMEOUT_SECONDS`
- `GIGACHAT_ADAPTER_TOKEN_SKEW_SECONDS`
- `HERMES_WEB_HERMES_API_BASE_URL`
- `HERMES_WEB_HERMES_API_AUTH_MODE=none`
- `HERMES_WEB_HERMES_API_MODEL`

## Model/access lessons from this session

- `GigaChat-3-Ultra` is the documented model identifier for Ultra on the public model-selection page.
- In the tested B2B contour, `GigaChat-3-Ultra` returned `404 No such model`.
- In the same contour, plain `GigaChat` reached the upstream but returned `402 Payment Required`.

Interpretation:
- do not assume a model name from docs is enabled in the current business contour;
- separate three failure classes clearly:
  - TLS / certificate failure;
  - token/auth failure;
  - upstream business access / tariff / model-availability failure.

## Reporting rule

When the named prod target is involved, final status should be one of:
- deployed and verified on target;
- deployed on target, blocked by exact upstream response `<code> <message>`;
- blocked before deployment by a concrete missing prerequisite.

Do not call it turnkey if the target host was not touched or if a real target-side round-trip was not attempted.