# OpenRouter routing reference for Hermes Web backend

## Live configuration shape used successfully

Gateway/Hermes side:
- provider: `openrouter`
- primary model: `openrouter/owl-alpha`
- global output cap lowered to `model.max_tokens = 4000`

Backend/runtime side:
- `HERMES_WEB_HERMES_API_MODEL=openrouter/owl-alpha`
- `HERMES_WEB_REASONING_MODEL=deepseek/deepseek-r1-0528`
- routing enabled
- reasoning enabled
- manual-only disabled
- limits:
  - global requests/day: 60
  - per-user requests/day: 6
  - global cost/day: 2.5 USD

## Durable rollout sequence

1. Configure OpenRouter key in Hermes secrets.
2. Configure Hermes provider/model to OpenRouter.
3. If direct model calls fail with provider credit or oversized-output errors, verify the effective output-token cap and reduce it before debugging backend routing.
4. Add backend route-task logic and limit checks.
5. Add route metadata to assistant-message meta.
6. Restart gateway and backend.
7. Verify in this order:
   - direct gateway call with default model;
   - direct gateway call with reasoning model;
   - backend simple chat request;
   - backend explicit reasoning chat request;
   - backend health routing summary.

## Signals that routing is really working

Default path:
- saved assistant message has route meta with:
  - `route_mode=default`
  - `route_reason=default`
  - model = default model

Reasoning path:
- saved assistant message has route meta with:
  - `route_mode=reasoning`
  - `route_reason=explicit_reasoning` or another reasoning reason
  - model = reasoning model
- user-visible answer can mention that deep reasoning mode was enabled and is limited/costlier

## Practical note on cost tracking

Request-count limits are the most reliable hard stop.
Cost limits are useful too, but provider usage may not always include an exact dollar figure in the returned payload. Use actual cost when available; otherwise use a conservative fallback estimate per reasoning request.

## Practical note on DB schema portability

If backend can run against Postgres-compatible SQL, avoid `DOUBLE` in DDL; prefer `DOUBLE PRECISION` for portable numeric columns used in usage/cost tracking.
