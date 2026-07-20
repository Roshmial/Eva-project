# GigaChat + Hermes runtime triage

Session lessons distilled into a reusable check order.

## Proven runtime signals

1. OAuth can succeed while the target model is still unavailable.
2. `/models` is the fastest truth source for what the current token can see.
3. `404 No such model` on generation usually means entitlement or wrong model for this token, not adapter breakage.
4. `402 Payment Required` means the upstream route is reachable but billing/tariff blocks generation.
5. A restart can change observed behavior because the process begins using a newly minted token instead of an old still-valid one.

## Practical sequence

1. Decode Basic key once to verify the client id part matches the expected project id.
2. Request OAuth token with the exact scope used in production.
3. Call `GET /models` with that fresh token.
4. Test direct upstream generation for the intended model.
5. Only after that, test the local adapter endpoint.

## Why this matters for Hermes

Hermes may look broken when tool-calling or chat fails after a restart, but the true fault domain may be upstream model visibility or billing. The adapter should be debugged only after auth and model availability are proven.
