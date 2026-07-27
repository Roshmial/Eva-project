---
name: implementation-first-delivery
description: Deliver implementation and optimization tasks by changing code and verifying results immediately; avoid drifting into architecture docs, plans, or 'maculature' when the user asked to build or optimize now.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Implementation-First Delivery

Use this skill when the user asks to:
- optimize an existing system now;
- implement a fix or feature immediately;
- reduce cost/performance problems in a running codebase;
- continue an already-discussed technical direction where the user expects code, tests, and real output rather than more planning.

Especially trigger this skill when the user shows frustration with planning drift, for example:
- "давай делать уже"
- "не макулатуру"
- "давай реализовывать сразу"
- "вместо этого ты жжешь токены на архитектурные документы"

Also trigger it when the conversation has just produced a plan/backlog/spec and the user then switches from analysis to execution. In that state, treat the planning phase as closed and do not create another `.hermes/plans/*` document unless the user explicitly re-asks for a plan.

## Core rule

If the user asked for implementation, do not spend the turn producing new architecture documents, plans, frameworks, or broad conceptual writeups unless the user explicitly asked for them.

Default output should be:
1. identify the smallest high-ROI code change;
2. implement it;
3. run targeted tests;
4. add or update metrics/telemetry when the task is about optimization, token usage, performance, or routing cost;
5. measure the practical effect with real execution or a synthetic-but-real code path;
6. report what changed, what passed, and what effect was observed;
7. only then suggest the next code step.

## User-specific delivery lessons

For this user, planning drift is a real failure mode.

When the user asks to optimize token usage or improve runtime behavior:
- start from already implemented logic in the codebase;
- inventory existing mechanisms briefly in your own head or with tool reads, not in long user-facing prose;
- choose the smallest implementation that produces immediate savings;
- avoid converting an implementation request into architecture paperwork.

Do not respond with large documents such as:
- architecture framework descriptions;
- generalized mediation concepts;
- multi-page backlogs;
- contract/spec documents;
when the user is clearly asking to ship the next working increment.

## Preferred workflow

### 1. Re-anchor on the runtime
Ask: what can be changed in code today with minimal risk and measurable benefit?

### 2. Reuse existing logic first
Prefer extending existing modules, tests, and runtime hooks over introducing a new layer.

### 2.1. When evaluating a new external engine or document format, prefer a separate microservice spike first
If the user asks to try a new rendering engine, presentation format, or standalone tool, do not immediately weave it deep into the main runtime.

Default delivery for this class of task:
- create a minimal separate local-first microservice or adapter in its own directory;
- keep the contract narrow and explicit, for example `/health`, `/render`, and artifact download;
- download or vendor the external shell/template locally when feasible;
- prove the contour by generating one real artifact end-to-end;
- only after that discuss deeper integration into Hermes or the main app.

Why this is preferred:
- lower blast radius;
- reversible architecture;
- easier acceptance because the user can inspect a working service and a real output file;
- avoids turning a tool evaluation into premature platform coupling.

Examples:
- extend an existing persistence/truncation path before inventing a new mediation subsystem;
- lift an existing dedup/reuse mechanism into a broader path before creating a framework;
- reuse current budgets/threshold registries instead of introducing parallel policy stores.

### 3. Pick the cheapest meaningful win
For optimization work, prefer:
- exact dedup/reuse;
- compact/reference modes;
- request-side inclusion controls;
- cheap delta for append-only or unchanged cases;
before large structural refactors.

### 4. Verify with real execution
Minimum bar:
- a failing or newly-added targeted test when behavior changes;
- implementation;
- targeted test pass;
- nearby regression suite pass when feasible.

For optimization tasks, verification is not complete until effect is measured.
Preferred evidence, in order:
- live telemetry/counters from the changed path;
- before/after char or token surface comparisons from real runs;
- synthetic-but-real executable scenarios when live production traces are unavailable.

Do not stop at "tests passed" if the user asked to reduce token use, runtime cost, or prompt surface size — also show what actually shrank.

### 5. Keep the report short
Default final structure:
- what was implemented;
- which files changed;
- what tests passed;
- what the practical effect is;
- the single best next code step.

## What 'под ключ' means for this user in integration and deployment tasks

When the user asks to "сделать под ключ", do not stop at a code artifact plus optional next steps.

For this user, the minimum acceptable bar is:
- implement the code change itself;
- wire the runtime entrypoint or adapter launch path;
- wire deployment artifacts when the project already uses them, for example systemd units, env examples, bootstrap scripts, or docker-compose entries;
- add or update targeted tests;
- run the tests and a live local probe through the real entrypoint;
- provide the exact env block and restart commands required to activate the change in the target contour;
- clearly separate "done in code" from "not executed on the remote server because no access".

If remote access is unavailable, still finish the local delivery package. That means the user should leave with a ready-to-apply artifact set, not with "adapter written, I can also prepare deploy bits if you want".

## User-specific pitfall: optional follow-up after the user asked for turnkey delivery

Bad pattern:
- implement the core code;
- verify it locally;
- stop with an offer like "if you want, I can also prepare env, unit files, and rollout commands".

Why this fails for this user:
- they already signaled that they want the full bounded deliverable in one pass;
- leaving rollout wiring as an optional extra reads like incomplete delivery, even when the code itself is correct.

Correction:
- treat runtime wiring, env changes, and deployment instructions as part of the same bounded task whenever the request is about integrating a real provider or production contour;
- only stop early if a real blocker exists, and name that blocker explicitly.

## References
- `references/gigachat-openai-compatible-adapter.md` — minimal OpenAI-compatible adapter pattern for providers like GigaChat that require OAuth token exchange before `/chat/completions`.
- `references/gigachat-prod-adapter-rollout.md` — rollout order, CA-bundle handling, OAuth checks, and model/access pitfalls for deploying a GigaChat adapter to a named production target.
- `references/gigachat-live-verification-ladder.md` — live verification ladder for GigaChat-like providers: validate OAuth, then `/models`, then paid generation, then tool-calling behavior.

## Pitfalls

### Pitfall: turning execution into planning
Symptom:
- user asks to implement or optimize now;
- assistant generates plans, backlog docs, architecture contracts, or other 'paper' artifacts.

Correction:
- stop writing docs;
- do not load `software-development:plan` or create a new `.hermes/plans/*` artifact just to feel productive;
- do not update `decision-log.md` as a substitute for implementation progress;
- move to the smallest code change with immediate ROI;
- speak in terms of changed files and test output.

### Pitfall: stopping at a local artifact when the user named a real target
Symptom:
- the user names a concrete runtime such as prod, staging, or a specific host like `178.104.207.89`;
- the assistant implements code locally, runs local tests, and reports success before touching the named target.

Why this fails for this user:
- when the target is named explicitly, they expect delivery on that target, not only a ready local package;
- a local artifact plus rollout instructions still reads as incomplete.

Correction:
- treat the named runtime as part of the bounded deliverable;
- if access exists, move immediately from local implementation to target execution;
- for server work, the minimum completion bar is:
  1. verify access to the target;
  2. identify the real project path and service names there;
  3. back up touched remote files before overwriting;
  4. deploy the changed artifacts to the target;
  5. restart or reload the target services;
  6. run target-side health checks and at least one real round-trip probe;
  7. if credentials or another true blocker are missing, report that exact blocker instead of presenting the local artifact as the finished result.

Rule of thumb:
- local code, tests, and docs are only intermediate evidence when the user asked about a real environment;
- the final answer should describe the state of the actual target, or the exact blocker that prevented reaching it.

### Pitfall: treating regulated/external API integration as only an adapter-coding task
Symptom:
- the assistant implements the proxy or adapter logic;
- assumes the remaining work is just a secret value;
- overlooks transport and auth prerequisites such as custom CA bundles, trust-store requirements, or an OAuth/token exchange step that must be proven from the target server.

Why this fails:
- many enterprise APIs are blocked by TLS trust-chain issues before auth is even exercised;
- "works in code" is not the same as "can obtain a token and serve requests from prod".

Correction:
- when integrating a regulated or enterprise API, verify in this order:
  1. transport trust: system store or explicit CA bundle;
  2. target-side TLS handshake from the real server;
  3. token or session acquisition flow from the real server;
  4. actual business request through the deployed runtime path.
- if `sudo` or system trust-store access is unavailable, prefer an explicit CA bundle path in the runtime over claiming the certificate step is done.
- do not present the integration as production-ready until the target server has passed both the TLS and token-flow checks.

### Pitfall: stopping after OAuth success in provider cutovers

Symptom:
- token exchange starts working;
- the assistant treats this as near-complete integration success;
- later live probes fail on model availability or provider billing state.

Why this fails:
- OAuth success proves only that credentials and trust-chain are valid;
- it does not prove the requested chat model exists for that tenant or that generation is actually enabled under the current billing/account state.

Correction:
- for provider cutovers, verify in this stricter live order:
  1. OAuth/token exchange works;
  2. `/models` returns the tenant-visible model list;
  3. requested chat model is chosen from that live list, not from stale tests or old notes;
  4. a plain generation call succeeds;
  5. only then validate tool-calling and multi-turn tool-result round-trips.
- if step 4 fails with a provider-side commercial status such as `402 Payment Required`, report it as the active blocker and stop calling the integration production-ready.

### Pitfall: trusting repo defaults instead of the live process environment

Symptom:
- the repo still contains an old provider endpoint, scope, or launch default;
- `.env` temporarily overrides it, so the current process looks healthy;
- after a restart, deploy, or clean launch, the contour silently falls back to the stale default and reproduces yesterday's incident.

Why this fails:
- reading files alone is insufficient in multi-script runtimes;
- the real contour is defined by the launched process environment, not by one guessed config source;
- a temporary `.env` override can mask dangerous defaults in `runtime_env.sh`, env examples, or adapter code.

Correction:
- when debugging provider routing on a named live host, verify three layers explicitly:
  1. search the repo for stale endpoint/scope defaults and env examples;
  2. inspect `/proc/<pid>/environ` for the live backend and adapter processes to prove what they actually use now;
  3. remove or update stale defaults in launch scripts, templates, and code constants so a future restart cannot regress.
- after changing defaults, add a regression test that sources the runtime script in a clean HOME/env and asserts the canonical provider endpoint and scope.
- for GigaChat B2B specifically, the canonical defaults are `GIGACHAT_ADAPTER_API_BASE_URL=https://api.giga.chat/v1` and `GIGACHAT_ADAPTER_SCOPE=GIGACHAT_API_B2B`.

### Pitfall: fixing the live `.env` but forgetting code-level and template defaults

Symptom:
- production is repaired by editing `~/.hermes/.env`;
- the assistant stops there;
- later a fresh machine, env-example-based deploy, or fallback code path reintroduces the old provider behavior.

Correction:
- for provider/runtime fixes, treat these as one bounded set and update all of them in the same pass:
  1. live `.env` or process environment;
  2. runtime launch defaults such as `scripts/runtime_env.sh`;
  3. shipped examples such as `deploy/package/env/*.env.example`;
  4. adapter/code constants used when env is absent;
  5. regression tests that assert the clean-default behavior.
- this is especially important for local-first stacks where deploys are often recreated from repo scripts rather than from a centralized secret manager.

### Pitfall: over-scoping optimization
Symptom:
- assistant tries to solve the entire architecture before landing the first savings.

Correction:
- land one token-saving mechanism at a time;
- prioritize immediacy, reversibility, and measured effect.

## Decision rule

When torn between:
- producing another explanatory artifact, or
- implementing a bounded improvement and verifying it,
choose the implementation path unless the user explicitly asked for a document.

## Output style

Use concise Russian.
Lead with concrete implementation status, not theory.
Prefer "сделала / изменила / прогнала тесты" over broad architectural exposition.
