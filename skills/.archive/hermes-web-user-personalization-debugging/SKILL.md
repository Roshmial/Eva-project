---
name: hermes-web-user-personalization-debugging
description: Verify and debug per-user memory/personalization in Hermes Web by checking DB persistence, prompt injection, runtime message metadata, and route-specific bypasses.
---

# When to use

Use this skill when a user says Hermes Web forgot user memory, claims memory is disabled, mixes up users, or gives inconsistent answers about profile-aware behavior.

Typical triggers:
- "память у меня отключена"
- "мы же храним memory по users"
- suspicion that prod/local runtime is not using `pinned_json` / `assistant_profile_json`
- need to verify whether a specific route bypasses personalization

# Core principle

In Hermes Web, "memory" is usually not a global agent memory feature. It is per-user personalization assembled from the `users` table and injected into the system prompt for model-backed routes. Debug it as a data-flow problem:

1. persisted in DB
2. loaded into profile object
3. inserted into prompt
4. reflected in message metadata
5. possibly bypassed by special routes

Do not stop at code inspection alone. For prod issues, verify the live contour directly.

# What counts as memory in this contour

Check these user-level fields first:
- `goals`
- `constraints_text`
- `pinned_json`
- `assistant_profile_json`
- supporting profile fields that also affect prompt shape: `name`, `title`, `team`, `timezone`, `language`

Important interpretation:
- presence in DB != guaranteed use on every route
- ordinary model-backed chat can use personalization while dashboard / research / attachment routes may mark it differently or skip it entirely

# Investigation workflow

## 1. Confirm the write path in backend code

Find the read and prompt-build chain:
- `user_to_dict(...)`
- `build_personalization_block(...)`
- `build_hermes_system_prompt(...)`
- `build_hermes_messages(...)`

Confirm the write/update path:
- `INSERT/UPDATE users`
- `pinned_json`
- `assistant_profile_json`
- any `/api/me` or admin-user update endpoints

Goal: prove which fields should persist and where they enter prompt assembly.

## 2. Check the live DB for the target user

For the target user (for example `admin@demo.local`), inspect the actual row in the live DB and decode JSON fields.

Verify:
- values are present
- values are not empty unexpectedly
- the user is the expected one
- timezone/title/team/goals match what the UI should show

If the server uses an in-project venv/service interpreter, prefer that exact Python when opening DuckDB/SQLite. This avoids false negatives from missing modules in the system interpreter.

## 3. Check live runtime evidence in messages

Inspect recent assistant messages for that user and read `meta_json`.

Key fields:
- `personalization_used`
- `personalization_preview`
- `downstream`
- `processing_status`
- model identifiers if present

Interpretation:
- `personalization_used=true` + populated preview => memory is actively injected
- `personalization_used=false` + `personalization_preview=dashboard-route` (or equivalent) => the request likely went through a special route that bypasses ordinary prompt personalization
- missing metadata on old messages does not prove current failure; prefer recent messages

## 4. Distinguish route problems from memory problems

Do not conclude "memory is off" until you separate:
- ordinary chat / model-backed route
- dashboard route
- web research route
- attachment / file route
- mock or test route
- scheduled job delivery route

A common false alarm is: memory exists and works in normal chat, but the inspected response came from a dashboard-style path where personalization is not applied or not surfaced the same way.

## 5. Verify prod directly when the issue is prod-specific

If the user names a prod server, inspect that server directly instead of inferring from local code.

Preferred order:
1. service status / exact interpreter path
2. actual DB path used by the service
3. target user's DB row
4. recent assistant message metadata for that user
5. only then login/API probes if credentials are known and current

If old smoke credentials fail, do not over-interpret that as a memory issue. Fall back to direct DB + runtime metadata inspection.

# Memory hygiene: what should and should not live here

In this contour, `interaction_memory_json` should hold only **stable interaction rules** that improve future conversations, for example:
- language preference;
- desired tone or depth;
- preferred brevity / structure of answers;
- stable communication constraints;
- explicit roles the user assigns to the agent.

It should **not** accumulate subject-matter content such as:
- KPI trees or metric taxonomies;
- CSV / Excel fragments, field lists, or reporting layouts;
- channels, media sources, monitoring topics, market/vendor interests;
- dashboard or export preferences that really belong to one current workflow;
- long factual summaries from prior requests;
- ad hoc work context that belongs to the current thread, not to the user's long-term interaction style.

Practical contract for Hermes Web:
- keep interaction logic and user-assigned agent roles;
- drop task/domain noise, output templates, and subject-matter preferences;
- prefer empty memory over weak or broad memories that can hijack routing or interpretation.

Why this matters: overloaded personalization can cause wrong task interpretation. A concrete failure class is URL requests like "что по ссылке" being hijacked by unrelated memory about BI, TCO, metrics, dashboards, or prior file-analysis work. Treat that as a personalization hygiene bug, not just a bad answer.

When auditing a bad response, inspect whether the user memory contains noisy domain content before assuming the model or browser layer is the root cause.

## Stronger writeback rule for user-facing products

If the product is a user-facing Hermes Web contour, do not let auto-writeback store "templates of what to output" as if they were stable user preferences. In particular, be suspicious of memories about:
- dashboard shapes;
- export/file formats;
- recurring monitoring topics;
- domain or industry interests;
- exact report columns/fields.

Those often look like preferences in isolation but are really instructions from one specific task. They belong in the current thread or job configuration, not in long-lived per-user personalization.

## Heuristic writeback guardrails

If Hermes Web auto-extracts interaction memory from chat history, broad lexical triggers are dangerous. Be suspicious of heuristics keyed on generic words like:
- `важно`
- `лучше`
- `нужно`
- `работаю`
- `роль`

These often capture ordinary task content instead of durable interaction preferences.

Safer auto-writeback patterns:
- bias toward explicit preference language such as `предпочитаю`, `по умолчанию`, `не люблю`, `зови меня`;
- reject long fragments, numeric/tabular snippets, CSV-like lines, and list-like business content;
- prefer an empty result over storing weak or domain-heavy memories.

# Pitfalls

- Do not confuse global agent memory with Hermes Web per-user personalization.
- Do not treat a stale login password as evidence that memory is broken.
- Do not use only `/api/me`; a correct profile payload still does not prove prompt injection happened.
- Do not use only prompt-building code; correct code still does not prove the live server is using it.
- Do not diagnose from dashboard responses alone; special routes often behave differently.
- Do not claim memory is disabled unless DB, prompt path, and message metadata all support that conclusion.
- Do not keep rich subject-matter context in `interaction_memory_json`; that can silently poison later answers on unrelated requests.
- Do not debug bad URL answers only at the browser layer; first rule out noisy personalization causing source-irrelevant completions.

# Good evidence to report back

Report in four layers:
1. what is stored in the user's DB row
2. what the code injects into the prompt
3. what recent live message metadata says (`personalization_used`, `personalization_preview`, `downstream`)
4. whether the failure is global or route-specific

This lets you answer precisely:
- memory is stored but not used
- memory is used in normal chat but skipped in dashboard route
- memory is neither stored nor injected
- memory claim from the agent text was incorrect

# Minimal conclusion patterns

Use conclusions like:
- "Да, память в базе есть и в обычном agent-path используется."
- "Фраза про отключённую память не подтверждается как глобальное состояние; проблема похожа на route-specific bypass."
- "В этом контуре память — это per-user personalization из `users`, а не единая общая память для всех."

Avoid overclaiming beyond the evidence.

# References

- See `references/runtime-verification-checklist.md` for a compact live-check checklist and evidence interpretation template.
- See `references/interaction-memory-hygiene-and-url-misrouting.md` for a concrete live incident where overgrown user memory polluted URL interpretation and required DB cleanup plus heuristic tightening.
