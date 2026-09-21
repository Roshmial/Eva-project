---
name: hermes-web-llm-routing
description: Configure and verify Hermes Web backend routing between a default OpenRouter model and a limited reasoning model, with per-user/global limits, fallback behavior, and live runtime checks.
---

# When to use

Use this skill when Hermes Web backend must:
- call Hermes API Server through a primary model plus a separate reasoning model;
- route most requests to a cheap/default model and reserve the reasoning model for high-value analysis;
- enforce daily limits globally and per user;
- expose route choice and fallback behavior in backend-visible metadata;
- be verified end-to-end through the real backend and gateway runtime, not just by editing config.

# Outcome

A working backend where:
- default requests go to the default model;
- explicit or high-complexity reasoning requests can go to the reasoning model;
- reasoning requests fall back to the default model when limits are hit or reasoning is disabled;
- backend health exposes routing config and usage summary;
- live chat requests complete through the deployed stack.

# Core design

## Routing policy

Implement routing at Hermes Web backend level, not by trying to teach the gateway implicit business logic.

Keep two model names in backend/runtime config:
- default model: used for ordinary chat, summaries, simple analytics, document transformations;
- reasoning model: used only for architecture, strategy, trade-off, multi-source synthesis, high-stakes analysis, or explicit user request.

Expose a routing function with this shape:
- `route_task(task_description, user_id, usage_stats, request_policy) -> route_decision`

Recommended decision order:
1. If reasoning routing is disabled -> default model.
2. If manual-only mode is enabled and user did not explicitly ask for reasoning -> default model.
3. If explicit reasoning trigger is present -> reasoning model, subject to limits.
4. Else if task matches durable complexity heuristics (architecture, strategy, trade-offs, conflicting multi-document analysis, high-stakes decision) -> reasoning model, subject to limits.
5. Else -> default model.
6. If reasoning was selected but any limit is exhausted -> fall back to default model and surface the reason.

Return structured route metadata, not just the model string. Example fields:
- `model`
- `route_mode` (`default` or `reasoning`)
- `route_reason` (`default`, `explicit_reasoning`, `complex_architecture`, `multi_source_analysis`, `high_stakes`, etc.)
- `limit_reason` when fallback happened

## Context preparation for reasoning model

Do not send raw long thread history or raw documents to the reasoning model by default.

Before invoking the reasoning model:
1. Build a compact context package from the thread/documents.
2. Summarize with the default model or backend summarization helpers.
3. Extract only:
   - user objective,
   - key facts,
   - conflicts/unknowns,
   - questions requiring judgment,
   - constraints.
4. Send that compact context plus the final reasoning prompt to the reasoning model.

This keeps R1 spend bounded and makes behavior reproducible.

# Configuration pattern

Prefer backend env/config knobs so routing can be changed without code edits.

Recommended env variables:
- `HERMES_WEB_HERMES_API_MODEL` — default model
- `HERMES_WEB_REASONING_MODEL` — reasoning model
- `HERMES_WEB_REASONING_ENABLED=1|0`
- `HERMES_WEB_REASONING_ROUTING_ENABLED=1|0`
- `HERMES_WEB_REASONING_MANUAL_ONLY=1|0`
- `HERMES_WEB_REASONING_DAILY_MAX_REQUESTS`
- `HERMES_WEB_REASONING_DAILY_MAX_PER_USER`
- `HERMES_WEB_REASONING_DAILY_MAX_COST_USD`
- `HERMES_WEB_REASONING_COST_FALLBACK_USD`

Keep the gateway/provider itself configured normally through Hermes `config.yaml` and `~/.hermes/.env`, while the backend owns routing policy and limits.

# Storage pattern for limits and audit

Persist reasoning usage in backend DB, not only in process memory.

Minimum event record:
- date bucket
- user id
- model key
- route mode
- route reason
- estimated cost
- actual cost if available
- excerpt or request fingerprint
- created_at

Use this table to compute:
- global reasoning requests today;
- per-user reasoning requests today;
- global reasoning spend today.

If provider usage does not return cost reliably, use a conservative fallback estimate per reasoning request and document that it is an estimate.

# Implementation steps

1. Add routing config loaders near other backend env/config constants.
2. Add durable heuristics for explicit reasoning triggers and complexity triggers.
3. Add DB table + helper functions for usage events.
4. Add `route_task(...)` and a helper that checks daily limits.
5. Add context compaction before reasoning-model calls.
6. Store route metadata on assistant message meta so UI/backend can explain the choice.
7. Expose current routing config and usage summary in health/admin-visible response.
8. Restart backend and verify with live requests.

# Verification checklist

## Backend-level verification
- syntax/compile check passes;
- smoke tests pass;
- health endpoint returns routing settings and daily usage summary;
- jobs/admin/bootstrap/auth endpoints still work after the change.

## Provider/runtime verification
- gateway can answer a direct request through default model;
- gateway can answer a direct request through reasoning model;
- default model no longer fails due to oversized output-token request;
- backend thread message completes through normal route;
- explicit reasoning request completes through reasoning route;
- route metadata on the saved assistant message reflects actual selection.

## Limit verification
Simulate or seed usage so that:
- per-user cap triggers fallback;
- global request cap triggers fallback;
- cost cap triggers fallback.

When a limit is hit, verify both:
- no reasoning model call is made;
- user-facing response explains that reasoning limit is exhausted and the task is being handled in simplified/default mode.

# Pitfalls

## 1. Treating provider setup as sufficient
Configuring OpenRouter at Hermes gateway level is necessary but not sufficient. Hermes Web backend still needs explicit routing policy, limit enforcement, and route metadata if you want controllable multi-model behavior.

## 2. Letting the gateway use huge default output budgets
A provider may reject requests or require more credits if Hermes sends an oversized `max_tokens`/output budget. In this project, lowering the configured global output cap restored successful OpenRouter calls. Verify direct `/v1/chat/completions` before blaming backend routing.

## 3. Making reasoning routing opaque
If the backend silently switches models, future debugging becomes expensive. Always attach route metadata (`route_mode`, `route_reason`, selected `model`, fallback cause).

## 4. Using raw documents for reasoning by default
This quickly turns R1 into an expensive summarizer. Compress first; reason second.

## 5. Relying only on local tests
Local unit/smoke coverage is not enough. Always verify the real gateway plus real web-backend path after restart.

# Runbook

## Change limits
Edit backend env/config values, then restart backend service.

## Disable reasoning completely
Set `HERMES_WEB_REASONING_ENABLED=0` and restart backend.

## Keep R1 only for manual invocation
Set `HERMES_WEB_REASONING_MANUAL_ONLY=1` and restart backend.

## Disable auto-routing logic while keeping reasoning code available
Set `HERMES_WEB_REASONING_ROUTING_ENABLED=0` and restart backend.

## Check live state
Use backend health/admin diagnostics to confirm:
- current default model;
- current reasoning model;
- whether routing is enabled;
- whether manual-only mode is enabled;
- today's global usage and remaining allowance.

# Files and references

See `references/openrouter-routing-reference.md` for a compact reference of env knobs, verification flow, and project-specific pitfalls discovered during live rollout.
