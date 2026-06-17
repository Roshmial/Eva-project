---
name: multi-user-agent-platform-design
description: Design and scope multi-user web platforms around Hermes or similar agents with per-user personalization, app-layer identity, and local-first architecture.
version: 1.0.0
---

# Multi-user agent platform design

Use this skill when the user asks to:
- deploy Hermes or a similar agent for multiple users;
- design a separate server for a web interface around an agent;
- define how personalization should work per user account;
- prepare architecture, infra checklist, web-app requirements, or MVP UI for an agent platform.

## Core rule

In multi-user setups, identity and personalization belong to the web application layer, not to a shared agent memory.

The app layer should own:
- users;
- auth sessions;
- roles;
- chat threads;
- message metadata;
- feedback;
- user profile and preferences;
- audit trail.

The agent layer should own:
- response generation;
- tool execution;
- agent session runtime.

## Default architecture

Prefer this baseline unless the user explicitly wants something else:
- reverse proxy exposed publicly;
- frontend UI;
- backend API as orchestration layer;
- Hermes API Server on localhost only;
- PostgreSQL as transactional app DB;
- DuckDB as local analytics/data-hub layer;
- Docker Compose or similarly simple local-first deployment.

## Why this split

Use PostgreSQL for:
- accounts;
- threads;
- chat history;
- preferences;
- feedback;
- admin data.

Use DuckDB for:
- Telegram analytics;
- tenders and similar collected datasets;
- derived views;
- internal analytical slices used by the agent.

Do not make DuckDB the primary multi-user web app database.
Do not make shared Hermes memory the canonical source of user identity.

## Personalization pattern

Per request, backend should:
1. authenticate the user;
2. resolve `user_id`, `thread_id`, and role;
3. fetch compact user profile and preferences;
4. build a bounded personalization block;
5. pass that block to Hermes together with thread context;
6. store resulting metadata separately from analytics.

Good personalization fields:
- display name;
- timezone;
- language;
- role/title;
- team;
- goals;
- response style preference;
- constraints;
- pinned notes.

Keep the personalization block compact and inspectable.

## Persona separation rule

In a multi-user product, separate the agent core from the user-facing persona.

Recommended split:
- the agent core = shared consultant runtime / capability layer;
- the persona = name, tone, style, role emphasis, and user-facing presentation.

This allows:
- one common agent architecture with several personas;
- "Eva" for one user, "Liza" for another, or a neutral assistant mode;
- easier product evolution without tying the whole system to one character.

Do not model the persona as a hard-coded property of the whole product. Store it as part of the user profile or onboarding configuration.

## Onboarding UX pattern

Do not show a full persona-onboarding flow every time the user creates a new chat.

Prefer two layers:
1. first product entry: a short onboarding wizard for assistant setup;
2. new chat creation: a small reminder that the assistant already uses the saved profile, with a link to adjust it.

Good first-run onboarding fields:
- assistant name;
- assistant role;
- tone;
- short vs detailed answer preference;
- optional goals and constraints.

Help/FAQ should explain:
- what settings affect all chats;
- what belongs to a single thread;
- how persona differs from the underlying agent role.

This reduces repeated friction while still making personalization visible and controllable.

## Scheduled jobs in multi-user web products

First decide whether jobs are a true product-layer entity or just an administrative projection of Hermes cron.

Two valid models exist:

1. Hermes-first model
- Hermes cron is the single source of truth;
- web backend reads and projects Hermes jobs;
- analytics mirrors Hermes job state downstream;
- UI may start as admin-only and read-only except for safe operations like run/pause/resume.

Use this when:
- the real operational picture already lives in Hermes;
- the existing UI job model is synthetic or MVP-only;
- separate app-side jobs would create drift.

2. Product-managed model
- Hermes cron is still the execution engine;
- backend/web app owns the product-layer metadata and safe editable surface;
- a mapping layer binds app job records to Hermes cron job ids.

Use this only when the product genuinely needs concepts that Hermes cron does not own directly, for example:
- end-user subscriptions;
- business visibility rules;
- recipient groups;
- curated presets and guarded forms.

Hard rule:
- never keep two independent operational job lists for the same real tasks.
- if Hermes already contains the canonical operational state, do not keep a second app.jobs truth beside it.
- if the app must add metadata, store only projection/mapping data around the Hermes job id, not a duplicate scheduler reality.

Recommended split in the Hermes-first model:
- Hermes cron = execution engine and canonical job state;
- backend/web app = projection, admin visibility, optional safe actions;
- analytics = downstream mirror only.

Why this is necessary:
- multi-user jobs need a clear owner of truth;
- visibility must be enforced at the app layer when exposed to users;
- synthetic MVP job rows become stale quickly and create false operational reporting;
- direct exposure of raw cron configuration still creates permission and safety problems.

Recommended visibility model:
- by default Hermes jobs are admin-only when first exposed in a web MVP;
- broaden visibility only after the app has a deliberate permissions model around Hermes job ids;
- if later needed, use `private`, `shared`, `public` as projection fields, not as a second scheduler source.

Recommended defaults:
- if the app is still immature, expose jobs only to admin;
- if the product later supports self-service jobs, owner must always be set;
- self-delivery may be on by default;
- adding other recipients should require explicit rights.

Allow users to edit only safe fields from the UI, for example:
- title;
- description;
- schedule;
- prompt/config parameters;
- pause/resume;
- delivery options allowed by the product.

Do not expose unrestricted editing of:
- arbitrary scripts;
- broad toolsets;
- raw delivery targets;
- unrestricted `no_agent` mode.

Important migration rule:
- when replacing synthetic MVP job data with Hermes-first sync, disable old create/edit/subscribe flows until a Hermes-compatible form exists.
- read-only plus safe run actions is better than preserving a UI that writes incompatible state.

Prefer a product-level form for managed scheduled workflows over a raw cron editor.

Reference: `references/hermes-jobs-source-of-truth-migration.md` for a concrete migration pattern from synthetic app jobs to Hermes-first projection.
## Delivery expectations for this user

When working this class of task for Misha:
- do not stop at abstract recommendations;
- produce a real architecture description, not just a component list;
- add a visual architecture diagram when useful;
- if feasible, build a quick MVP frontend or mockup;
- if local test deployment is possible, launch a minimal test environment and verify it;
- if Misha asks to "show how the frontend looks now" and a live browser screenshot is blocked, reconstruct the current UI from the actual frontend files and label it explicitly as a code-grounded mockup rather than a live capture.

Reference: `references/frontend-state-visual-reconstruction.md` for the fallback pattern.

## Chat-first copilot and analytics pattern

When the product's broad audience primarily lives in chat, do not force the first Copilot experience into admin/jobs just because those screens are structurally easier.

Prefer this staged model:
- chat remains the primary entry point and conversation record;
- Copilot is a secondary module (panel, overlay, or separate analytics screen), not a silent replacement for the core chat;
- the bridge from chat to Copilot is explicit: the user chooses `build dashboard`, `open assistant`, or a similar action;
- the system passes a compact structured context, not the raw full thread by default.

### Important separation rule
Do not treat every chat message as an instruction to mutate UI or build analytics.

Use three layers:
1. conversation in chat;
2. structured intermediate context extracted from the conversation;
3. explicit user-triggered action that opens Copilot / dashboard rendering.

For analytics, the intermediate object should be something like `dashboard_context`, containing only the bounded material needed for visualisation:
- topic / analytical question;
- period;
- entities / slices;
- metrics and values already confirmed;
- sources of truth;
- computed fields;
- assumptions / hypotheses;
- gaps / missing data;
- suggested widgets.

### Data provenance rule
For any dashboard generated from chat-derived context, keep a visible separation between:
- confirmed data from backend/files;
- computed values derived from confirmed data;
- hypotheses or inferred interpretations.

Never let the LLM layer become the implicit source of numeric truth.

### UX pattern: build dashboard from discussion
A strong product pattern is:
- the user discusses the problem in chat;
- the agent accumulates structured analytical context in the background;
- the user can click `Build dashboard` at any time;
- before rendering, show a short preview of what was understood, what data is confirmed, and what is missing;
- only then render the dashboard or ask for clarification.

This preserves chat as the natural interface while giving the user an explicit and trustworthy transition into visual analytics.

Reference: `references/chat-first-dashboard-context.md` for the concrete pattern, object shape, and product guardrails.

## MVP scope

A good first MVP usually includes:
- login/logout;
- thread list;
- chat screen;
- profile screen;
- feedback capture;
- admin health screen;
- backend proxy to Hermes API Server;
- per-user personalization from app DB.

Avoid in the first MVP unless explicitly needed:
- SSO;
- complex RBAC;
- public exposure of Hermes API Server;
- overbuilt orchestration;
- replacing app DB with analytics DB.

## Infra sizing baseline

If no better sizing data exists, use this baseline for production without local LLM inference on the same host:
- 8 vCPU;
- 16 GiB RAM;
- 120–160 GiB NVMe;
- 4–8 GiB swap.

State clearly that local LLM inference on the same host changes sizing materially and is better split to a separate inference node.

## Recommended deliverables

For planning/design requests, try to leave behind these artifacts:
1. architecture decision write-up;
2. visual diagram;
3. deployment checklist;
4. web-interface requirements/TZ;
5. MVP frontend prototype if requested;
6. optional compose skeleton / DB schema next.

## References

- See `references/hermes-web-mvp-session.md` for a concrete session pattern: separate server, per-user personalization through web account, architecture artifact + interactive MVP.
