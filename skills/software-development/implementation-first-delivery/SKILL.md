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

### Pitfall: ignoring prior implemented logic
Symptom:
- assistant proposes a fresh framework while similar logic already exists in `tools`, executor flow, persistence, or tests.

Correction:
- treat existing code as the primary source material;
- extend or generalize it in place first.

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
