# Implementation-first delivery for token-optimization and runtime efficiency tasks

When the user asks to reduce token usage, optimize runtime/tooling behavior, or continue implementation after an initial framing pass, do not keep producing new architecture documents, plans, contracts, or backlogs unless the user explicitly asks for documentation.

## Trigger signals
- User asks for quick wins, minimal-risk optimization, or fastest practical implementation.
- User says variants of:
  - "давай делать"
  - "сразу реализовывать"
  - "не макулатуру"
  - "хватит архитектурных документов"
  - "учти уже существующие и ранее реализованные логики"

## Required behavior
1. Treat existing code paths and already-implemented logic as the primary foundation.
2. Before proposing new abstractions, identify the smallest directly shippable change inside the current execution path.
3. After one planning pass at most, switch to code changes, tests, and verification.
4. Report only real implementation results: files changed, behavior added, tests run, metrics collected.
5. Prefer short progress summaries over new documents.

## Pitfall to avoid
A common failure mode is drifting from a practical optimization request into repeated plan/architecture writing. This burns user patience and tokens while not improving the product. Once the user redirects toward execution, stop generating additional planning artifacts and move immediately to implementation.

## Specific lesson from this session
For token-optimization work, the right sequence was:
- account for existing terminal normalization, persistence, budgets, file reread dedup, web head+tail, and browser compact/full behavior;
- implement immediate quick wins in the current code path;
- add telemetry so savings can be measured;
- postpone broader framework work until after concrete savings land.

## Practical quick-win ladder for existing-codebase token optimization
Use this order when the user wants the fastest low-risk wins with measurable effect:
1. exact reuse/reference for repeated heavy outputs;
2. reuse inside aggregate turn-budget enforcement;
3. telemetry for persistence/reuse savings;
4. cheap delta for append-only logs;
5. cheap delta for structured JSON top-level changes;
6. request-side short inclusion for persisted/reference results;
7. minimal policy selector (`full` / `compact` / `reference` / `delta`);
8. only then a small unified policy contract if the first wins are already proven.

## Reporting rule
In each step report three things separately:
- what exact mechanism was added;
- what tests or verifications passed;
- what measured or at least directly observed token/char saving it produced.
