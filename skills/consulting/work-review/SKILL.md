---
name: work-review
description: Structured review of IT, architecture, product, stakeholder, process, and execution questions.
version: 1.0.0
user_locked: true
tags: [consulting, work, it]
category: consulting
priority: 90
---

# Work Review

## When to Use
Use this skill for:
- architecture decisions;
- product and roadmap questions;
- prioritization;
- stakeholder conflicts;
- process or governance questions;
- communication strategy in complex work situations.

## Procedure
1. Define the actual problem:
   - what is happening,
   - why it matters,
   - what decision or action is needed.
2. Clarify context:
   - business goal,
   - technical constraints,
   - stakeholders,
   - timeline,
   - dependencies.
3. Analyze from several perspectives:
   - business impact,
   - technical feasibility,
   - implementation cost,
   - operational risk,
   - organizational consequences,
   - communication complexity.
4. Generate realistic options.
5. For each option describe:
   - benefits,
   - drawbacks,
   - dependencies,
   - failure modes.
6. Produce the answer in this structure:
   - short conclusion,
   - diagnosis,
   - options,
   - trade-offs,
   - recommended next step.

## Delivery rules for Misha in audit/review mode
- If the request is an audit, review, or maturity assessment, deliver the full assessment package in one response by default.
- Do not end with an unsolicited "if you want, I can also ..." expansion when the missing item is already an obvious part of the audit package.
- If the user explicitly points to a concern area (for example files, UX, delivery, or operations), include it as its own section in the same review instead of leaving it as an optional follow-up.
- Separate clearly:
  - what is confirmed and working;
  - what is weak or immature;
  - what must be improved first.
- Treat this as a done-style consulting deliverable: complete the baseline review, then mention optional deeper follow-up only if it is truly a separate phase rather than an omitted part of the current answer.
- Special stop rule for architecture/program structuring requests: when Misha asks for the final shape itself (`итоговый перечень`, `слои`, `этапы`, `работы`, `собери каркас`, `дай по шагам`), that requested structure is the deliverable. Do not append `если хочешь, следующим сообщением...` with a table, MVP split, blueprint, or another formatting pass unless he explicitly asked for an extra artifact beyond that structure.
- If the answer already contains the requested final list/table/frame, stop on that artifact. A follow-up offer in the same area usually means the answer is still internally treated as draft; finish the shape now instead.

## Evidence-Bound Vendor / Market Research
Use this pattern when the work question is a vendor landscape, platform selection, regulatory scan, or technology-market research.

1. Split large research into durable parts instead of one giant document:
   - scope and market map;
   - vendor landscape by class;
   - jurisdiction / regulatory barriers;
   - requirements and scoring matrix;
   - recommendations and pilot plan.
2. For each vendor or option, use a repeatable evidence template:
   - what the platform is;
   - confirmed use cases;
   - document/workflow capabilities;
   - jurisdiction or domain applicability;
   - security/privacy claims;
   - deployment/data residency;
   - pricing;
   - limitations and RFI questions;
   - sources.
3. Do not fill gaps with plausible-sounding claims. If public sources do not confirm a point, write "publicly not disclosed", "requires RFI", or "hypothesis to validate with the vendor".
4. Separate:
   - vendor claims;
   - independently verifiable facts;
   - interpretation;
   - recommendation.
5. When public claims include metrics, label them as vendor-stated unless independently validated.
6. Update the index/status file as parts are created so the user can see what exists and what remains.
7. If official sources are partially inaccessible, blocked, dynamic, or redirected after rebranding, record that limitation in the output and downgrade the confidence level rather than filling the gap.

Reference: see `references/legalai-vendor-research.md` for a compact example of the LegalAI vendor-research pattern, blocked-source handling, and RFI discipline.

## Architecture pattern: shared internal AI agent on Hermes

Use this pattern when the user wants to scale Hermes beyond one personal chat into a small shared internal service with:
- separate web UI;
- several simultaneous users;
- one common agent approach instead of per-user personalization;
- feedback and backlog capture.

Default recommendation inside the existing local-first stack:
- Hermes API Server as backend;
- a separate lightweight custom web frontend, not a heavy generic chat platform by default;
- one dedicated Hermes profile for the shared agent, separate from the user's personal/default profile;
- local SQLite for conversations, feedback, and backlog;
- Hermes cron for periodic triage/summaries if needed.

Why this pattern is usually better:
- isolates the shared service from the user's personal memory, sessions, cron jobs, and gateway routines;
- keeps infrastructure small and understandable;
- makes it easy to enforce one common behavior through fixed instructions instead of drifting per-user memory;
- avoids introducing SaaS or extra orchestration before the local stack is exhausted.

Recommended checks and decisions:
1. Verify current host capacity before recommending the topology: CPU, RAM, swap, disk, running services, and occupied ports.
2. Do not reuse the personal/default Hermes profile for multi-user web access. Create a dedicated profile for the shared agent.
3. In the shared profile, prefer disabling built-in memory and user-profile memory when the requirement is one common agent with limited personalization.
4. Treat API-server tool exposure as a first-class security decision. Start with a narrow allowlist of toolsets and expand only after testing.
5. Prefer a thin frontend when the user needs custom feedback/backlog workflow, moderation, or a fixed operating model. Use Open WebUI only when a generic chat UI is truly enough.
6. If feedback and backlog are required, recommend capturing them in the local app database first, then optionally summarizing/triaging through Hermes cron.
7. Keep the API server bound to localhost unless there is a clear reason to expose it. Put the public surface on the web frontend / reverse proxy layer.
8. When the shared web UI may later move off the current Hermes host, split frontend and backend early: frontend as a static service with an external API endpoint config, backend as a separate API service with its own data volume and env-config. This avoids coupling the product UI to the Hermes runtime host.
9. For MVP portability, prefer this boundary: frontend -> backend API -> Hermes API Server. Do not let the frontend depend on Hermes-local paths, shared process state, or backend-served HTML if migration flexibility matters.

Reference: `references/hermes-web-mvp-microservice-split.md` for a compact portability pattern.

Practical starting defaults for the shared profile:
- separate profile, e.g. shared-web;
- API server enabled on 127.0.0.1;
- dedicated API_SERVER_KEY;
- memory.memory_enabled: false;
- memory.user_profile_enabled: false;
- privacy.redact_pii: true when multiple people use the service;
- platform_toolsets.api_server reduced to the minimum needed for the workflow.

Conservative first-wave toolsets for a shared non-admin chat agent:
- web
- file
- vision
- skills
- session_search
- todo

## Architecture pattern: local unified data hub for agent interactions and parsings

Use this pattern when the user wants one local store for:
- Hermes interaction history;
- Telegram/news/channel parsings;
- tender or market parsings;
- lightweight analytics and ad-hoc SQL without adding a full DB service.

Default recommendation inside the existing local-first stack:
- DuckDB as the primary local analytical hub;
- keep Hermes core storage untouched;
- load external artifacts into separate analytical tables/views;
- refresh the hub from existing Hermes sessions/logs and parsing outputs after each pipeline run.

Why this pattern is usually better:
- one file, no daemon, no root, no extra ops tail;
- excellent fit for CSV, JSON, SQLite exports, and mixed semi-structured data;
- simpler than Postgres when the main need is accumulation + querying, not concurrent OLTP;
- easy to query from Python and use in Hermes-side scripts.

Recommended starting domains/tables:
- Hermes sessions/messages;
- Telegram raw/archive messages and summary inputs;
- tenders and tender-source statuses;
- source_files/import_runs for traceability.

When the user also has a live web/backend application, do not automatically make that app write into the same DuckDB file as the analytical hub.

Decision rule for separation:
- if the database primarily serves frontend/runtime CRUD, auth, jobs, feedback, or operational state, treat it as an application DB;
- if the database primarily serves accumulated Hermes history, parsed artifacts, decision support, and ad-hoc querying, treat it as an analytical hub;
- if both roles start to mix, prefer two explicit databases over one file with overlapping schemas.

Preferred boundary in that situation:
- operational backend DB: separate file, owned by the app, with its own schema and lifecycle;
- analytical DuckDB hub: separate file, owned by refresh/ETL scripts;
- any transfer from app DB into the hub should happen through explicit refresh/export logic, not backend runtime coupling.

High-value additions once the hub becomes the assistant’s working memory layer:
- ingest stable working documents such as `interaction-notes.md` and `decision-log.md` as first-class datasets;
- expose lightweight views for them so the agent can query them directly instead of reparsing files every time;
- add formal status markers for Hermes history, for example message-level `done/not_done` and session-level completion flags, plus a ready-made unresolved-requests view.

Prefer Postgres only when there is a real need for:
- concurrent writes from several services at once;
- application-grade transactions and row-level updates;
- external BI/app integrations that assume a server DB.

Pitfall:
- do not introduce a separate database service just to "have a database" when DuckDB already covers the local analytical use case with less infrastructure.

### Operationalization step after the hub is live

After the first successful local data-hub rollout, do not stop at raw tables plus one or two generic views. The next highest-value step is to add task-specific operational views so the agent can answer faster from the existing stack instead of repeatedly reconstructing ad-hoc SQL.

Preferred sequence:
1. keep one canonical analytical table/view per domain;
2. add a small set of action-oriented views for the recurring workflows;
3. verify each new view against real data immediately after refresh;
4. update the local README with copy-paste queries the user can run without rediscovering the schema.

Good examples of action-oriented views:
- Telegram digest candidate queue: filters out low-signal categories and ranks posts for client-facing shortlists;
- tender priority queue: normalizes dates, removes visible duplicates, adds deadline proximity and budget-based priority scoring;
- recent Hermes user questions / threads: accelerates context recall and recurring-topic detection.
- decision-log / operator-notes views: makes durable working context queryable inside the same local analytical layer.

Reference: `references/operational-vs-analytical-duckdb.md` for the boundary between operational backend storage and analytical DuckDB hub, plus status/view patterns.

Decision rule:
- prefer a few high-utility ready-made views over asking the user or the future agent to remember complex query logic;
- stay inside the current local-first stack and existing refresh pipeline;
- optimize for fast operational use, not for schema elegance alone.

Avoid enabling on day 1 unless the use case explicitly requires them and the risk is accepted:
- terminal
- process
- browser
- cronjob
- delegation
- memory
- messaging

## Architecture pattern: adaptive dashboard systems in Hermes/local-first products

Use this pattern when the product needs to answer many open-ended analytics or research questions through dashboards, but there is no honest way to define one universal "canonical dashboard" up front.

Default recommendation:
- do **not** force a single rigid dashboard template as the main abstraction;
- define a small stable outer container instead;
- let the inside of the dashboard be composed from reusable typed blocks chosen by the task and the shape of the data.

Preferred decomposition:
1. Stable outer container
   - Keep only low-dispute top-level fields stable, for example:
     - `kind`
     - `title`
     - optional `subtitle`
     - `summary`
     - `sections`
     - `sources`
     - `notes` / `limitations`
   - Treat this as a transport and rendering contract, not as the business meaning of the whole dashboard.

2. Extensible section grammar
   - Model dashboards as compositions of reusable section types instead of pre-baked screen templates.
   - Good section classes include:
     - KPI / summary cards;
     - ranking / top list;
     - category comparison;
     - trend / timeline;
     - distribution;
     - composition;
     - relationship / correlation;
     - geography;
     - matrix / segmentation;
     - text insight;
     - evidence / examples;
     - anomalies / exceptions;
     - source coverage / confidence.
   - The grammar should be able to grow over time without breaking the outer contract.

3. Selection policy
   - Put the intelligence into rules for choosing sections, not into a giant catalog of fixed dashboard templates.
   - Select by:
     - user intent;
     - data shape;
     - data completeness;
     - whether the task is comparison, trend, composition, segmentation, explanation, or evidence review;
     - whether the available data actually supports quantitative visualization.
   - The system should also decide when a dashboard is the wrong output and a normal analytical reply or clarification is better.

Why this pattern is usually better:
- covers more request shapes than a narrow library of handcrafted templates;
- avoids fake certainty about a "canonical" schema where the domain is inherently open-ended;
- keeps frontend and backend aligned through a small contract plus a growing grammar;
- fits local-first Hermes products where backend policy and frontend renderer can evolve incrementally.

Recommended implementation posture:
- keep the backend responsible for output routing and payload normalization;
- keep the frontend responsible for rendering known section types clearly;
- treat prompt/skill guidance as advisory selection logic, not as the only source of structure guarantees;
- accumulate new section types and routing heuristics from real requests rather than trying to predict all cases up front.

Pitfall:
- do not confuse "we need consistency" with "we need one universal dashboard template". In open-ended analytics products, consistency should usually live in the outer container, section grammar, and selection policy — not in a single fixed dashboard layout.

## Architecture pattern: adding a non-native tool-calling LLM without breaking the existing agent runtime

Use this pattern when the user wants to plug a provider like GigaChat into an already working Hermes-style product that currently behaves correctly with other LLMs.

Default recommendation:
- do not splice provider-specific logic into the main executor path;
- keep the product contract stable at the top;
- isolate the provider-specific execution/runtime layer behind an explicit routing boundary.

Preferred decomposition:
1. Stable outer product contract
   - frontend and backend API stay provider-agnostic;
   - do not leak provider-native fields like `functions_state_id` into the public product contract as required frontend state.

2. Explicit execution routing
   - keep a `standard executor` for already compatible LLMs;
   - add a separate `provider-specific executor` for the non-native provider;
   - choose the path in one routing layer instead of scattering provider conditionals throughout the codebase.

3. Protocol adapter as a narrow layer
   - adapter translates OpenAI-style `tools/tool_calls` to the provider-native function-calling protocol and back;
   - adapter handles provider-specific retry/timeout/error normalization;
   - adapter should not own product workflow or tool-policy logic.

4. Separate agent loop controller when the provider is not Hermes-native
   - if the provider cannot run the normal Hermes tool loop reliably, build a dedicated loop controller for that route;
   - own `model -> tool -> model` iteration, tool-call replay, and provider-specific continuation state there.

5. Shared tool registry, separate runtime heart
   - it is fine to reuse tool handlers, storage, auth, chat state, logging, and frontend surfaces;
   - but if the provider needs its own tool orchestration, treat that as a second execution heart under the same product shell.

Decision rule:
- if the user only needs the provider as a plain LLM, a protocol adapter is enough;
- if the user needs a full Hermes-like agent with browser/tools/stateful loops, plan for a near-parallel agent runtime core, even if the outer product layers are shared.

Why this matters:
- trying to force a provider like GigaChat into the existing standard executor usually creates hidden regressions for the already working LLM path;
- the highest-value architecture move is route isolation, not heroic normalization inside one shared loop.

## Pitfalls
- Do not focus only on technical elegance.
- Do not ignore political and organizational realities.
- Do not suggest a solution without an adoption path.
- Do not confuse symptoms with root cause.
- Do not invent vendor capabilities, pricing, deployment models, data residency, legal coverage, or security controls just because they are common in the market.
- Do not turn an unverified applicability hypothesis into a recommendation.
- Do not recommend multi-user sharing through the user's personal Hermes profile when isolation and predictable behavior matter.
- Do not leave API-server toolsets broad by default in a shared web deployment.
- Do not rely on per-user memory when the stated requirement is one common agent behavior.
- In this user's local-first web/product discussions, when the request is phrased as "add it on the frontend", interpret that as a backend-backed feature by default: UI on the frontend, logic/state/validation/execution via backend. Do not waste answer space repeatedly warning that a pure frontend-only implementation would be unreliable unless the user explicitly asks about a frontend-only variant.
- When integrating a provider with non-native tool calling, do not contaminate the standard executor with provider-specific continuation fields, retries, or state handling if a separate route can isolate the risk.

## Verification
Check that:
- the decision point is explicit;
- business and technical dimensions are covered;
- trade-offs are clear;
- the answer can be acted upon.