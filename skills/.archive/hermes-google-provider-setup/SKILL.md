---
name: hermes-google-provider-setup
description: Configure Hermes Agent to use Google AI Studio / Gemini API directly for Gemini or Gemma models, verify model availability, and avoid common slug/auth mistakes.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Hermes Google provider setup

Use this skill when the user wants Hermes itself to call Google AI Studio / Gemini API directly instead of OpenRouter or a local custom endpoint.

This skill covers:
- configuring Hermes with the native Google provider;
- switching Hermes to Gemini or Gemma models served by Google;
- verifying the exact model slug before claiming support;
- avoiding common failures around wrong model IDs and auth headers.

## Why this skill exists

Google-hosted Gemma and Gemini models often have exact model IDs that differ from the obvious guess. A common failure is assuming a slug like `gemma-4-31b` exists when the live API only exposes `models/gemma-4-31b-it`.

Hermes already has first-class support for the Google provider and prefers the native Gemini API path. Do not default to an OpenAI-compatible shim when the native path is available.

## Default approach

Prefer this order:
1. Save the Google API key into `~/.hermes/.env` as `GOOGLE_API_KEY` or `GEMINI_API_KEY`.
2. Set Hermes main model config to provider `gemini`.
3. Use the native Google base URL: `https://generativelanguage.googleapis.com/v1beta`.
4. Discover the live model list from Google before finalizing the exact model slug.
5. Verify with a minimal `hermes chat -q ...` call.
6. Only after the main path works, decide whether to move auxiliary models or Hermes Web backend routing to the same provider.

## Required config shape

Typical Hermes config values:
- `model.provider: gemini`
- `model.default: <exact live model slug>`
- `model.base_url: https://generativelanguage.googleapis.com/v1beta`

Typical secrets:
- `GOOGLE_API_KEY=...`
- or `GEMINI_API_KEY=...`

## Verification workflow

### 1. Configure Hermes

Use Hermes config commands rather than hand-editing YAML when possible:
- `hermes config set model.provider gemini`
- `hermes config set model.default <model>`
- `hermes config set model.base_url https://generativelanguage.googleapis.com/v1beta`

### 2. Discover available models first

Before promising that a Google-hosted Gemma variant exists, query the live API model list.

Reason: exact slugs matter, and Google may expose `...-it`, preview, or family-specific names that differ from documentation summaries or intuition.

### 3. Verify with a minimal Hermes call

Run a short `hermes chat -q` prompt against the exact chosen model. Prefer a tiny Russian or English prompt and confirm a real response arrives.

## Durable pitfalls

### Pitfall: guessed Gemma slug

Do not assume `gemma-4-31b` works just because the family exists. The live API may expose `models/gemma-4-31b-it` instead.

Rule: always confirm the live slug via the Google models endpoint.

### Pitfall: wrong API style

For Hermes, prefer the native Google provider path (`provider: gemini` with the native base URL) instead of routing Google through a generic OpenAI-compatible custom provider.

Reason: Hermes has a native Gemini adapter and handles Google-specific request details there.

### Pitfall: mixing a provider switch with a full stack cutover

When migrating to Google API, first make the main Hermes model work. Keep auxiliary models or Hermes Web routing unchanged until the base path is verified.

Reason: this isolates provider problems from unrelated runtime changes.

## Good operating pattern for Gemma on Google

For direct Google-hosted Gemma:
- use `provider: gemini`;
- keep `model.base_url` on `https://generativelanguage.googleapis.com/v1beta`;
- verify the exact slug from the live `/models` listing;
- test with Hermes immediately after switching.

## Session-proven notes

A proven working pattern in this environment was:
- key stored in `~/.hermes/.env`;
- provider set to `gemini`;
- native base URL set to `https://generativelanguage.googleapis.com/v1beta`;
- guessed slug `gemma-4-31b` failed with `404 NOT_FOUND`;
- live models listing showed `models/gemma-4-31b-it`;
- switching Hermes to `gemma-4-31b-it` succeeded.

See `references/google-gemma-model-discovery.md` for a concise reproducible checklist.

## When to update this skill

Update this skill when:
- Google changes the preferred base URL or auth pattern;
- Hermes changes how the native Gemini provider is configured;
- new stable naming patterns for hosted Gemma models emerge;
- repeated migration work shows a better verification sequence.
