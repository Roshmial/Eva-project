---
name: implementation-first-optimization
description: Use for token, context, output-surface, and similar optimization work when the user wants immediate measurable wins instead of architectural paperwork.
---

# When to use

Use this skill when the task is about reducing token usage, context bloat, noisy tool output, or similar agent/runtime inefficiency, especially when the user asks for quick wins, minimal risk, or fast implementation.

Typical triggers:
- the user asks for quick wins
- the user asks to optimize token consumption
- the user pushes back on architecture documents, concept papers, or speculative framework design
- the user wants code, tests, and measurable effect now
- the work sits inside an existing local stack and should extend current mechanisms first

# Core operating rule

Default to implementation-first.

Do not spend the first pass on architecture notes, broad redesigns, or abstract framework docs if the user is asking for immediate optimization. Start from the narrowest high-ROI change that can be implemented safely inside the current code path.

# Preferred sequence

1. Restate the waste source precisely.
   Examples: repeated heavy tool outputs, oversized prompt-side references, append-only logs being resent in full, slightly changed JSON/state payloads, per-turn budget overflow.

2. Find the smallest safe intervention.
   Prefer:
   - exact reuse before fuzzy reuse
   - task-scoped caching before cross-session/global caching
   - output-side reduction before deeper architectural rewrites
   - request-side shortening after output-side persistence/reuse exists

3. Reuse the existing local branch.
   Extend the user's current local implementation first instead of building a parallel subsystem. If one path is already mature, attach the new behavior there and prove value before extracting a general layer.

4. Add telemetry in the same change.
   Optimization work is incomplete if the effect cannot be measured. Add counters or reports for:
   - how often the optimization fires
   - chars/tokens saved when feasible
   - policy distribution when multiple output policies exist

5. Add focused tests.
   Prefer one of these patterns:
   - failing targeted test before implementation
   - targeted regression test for the new path
   - follow-up smoke/regression slice on the affected area

6. Measure the effect after implementation.
   Validate with both:
   - tests
   - a small synthetic or real-path scenario showing concrete before/after size reduction

7. Generalize only after multiple concrete wins exist.
   Once several optimizations are in place, extract a minimal shared selector/contract rather than inventing a framework up front.

8. Standardize the output contract before building a framework.
   Use this progression:
   - land concrete quick wins first;
   - introduce a tiny shared policy selector such as `full / compact / reference / delta`;
   - add a small policy contract with fields like `policy`, `source`, `raw_chars`, `surface_chars`, `chars_saved`, `changed`;
   - only then wrap it in a lightweight mediation descriptor carrying `artifact_path`, `delta_applied`, `reuse_applied`, and raw-content availability.
   - after that, if the user asks to stop the endless loop and do it "под ключ", switch to a bounded closeout pass: finish the remaining obvious integration, reducer/reporting, regression, and decision-log boundary work as one v1 package.

   Keep this descriptor thin and implementation-driven. It should describe already-working behavior, not speculate about future framework layers.

9. Close the stream explicitly when the user asks for a turnkey result.
   In bounded closeout mode:
   - define what is in v1 and what is intentionally out of scope;
   - stop proposing the next micro-improvement by default;
   - if a remaining improvement or cleanup is low-risk, local, and materially improves completeness, include it yourself before delivery instead of surfacing it as a follow-up;
   - ask the user only for changes that are high-risk, scope-changing, destructive, or architecturally consequential;
   - make the remaining pass about integration completeness, telemetry completeness, regression, and measured verification;
   - before handing off, do one explicit completeness check: what is still unfinished, is it critical, and if not critical, finish it now rather than mentioning it as optional future work;
   - update `decision-log.md` so future work does not reopen the same loop without new data.

# Good optimization order

Start with the highest confidence and lowest blast radius:

1. exact reference reuse for identical large outputs
2. aggregate turn-budget reuse/persistence
3. prompt-side compaction of already-persisted references
4. append-only log delta
5. top-level JSON delta for small structured changes
6. only then a shared policy selector such as full / compact / reference / delta

# Policy model

When several output surfaces already exist, route them through a minimal common policy vocabulary:
- full: keep direct output when already small
- compact: keep a summarized or head/tail form
- reference: keep a short persisted-artifact reference
- delta: keep only the change versus prior state/output

Use this vocabulary as a light selector layer over existing implementations. Avoid building an abstract framework before the concrete policies already exist in code.

# Pitfalls

- Do not burn tokens on architecture documents when the user asked for implementation.
- Do not claim optimization success without telemetry or at least a measured before/after surface reduction.
- Do not jump to fuzzy matching or cross-task/global reuse before proving exact, task-scoped behavior.
- Do not introduce new infrastructure when the current local code path can absorb the change.
- Do not stop at "the tests pass" if a tiny runtime measurement can show real savings.

# Reporting back to the user

Keep the report operational:
- what was implemented
- where it was wired in
- what tests were run
- what the telemetry or measurement showed
- what the next low-risk win is

Avoid drifting back into large design prose unless the user explicitly asks for the next abstraction step.

# References

- `references/token-optimization-quick-wins.md` — concrete quick-win patterns and measurement ideas for token-surface reduction.
- `references/policy-contract-and-mediation-descriptor-v1.md` — when several quick wins already exist, use this note to extract the smallest shared selector, policy contract, and mediation descriptor without jumping to framework-first design.
- `references/bounded-closeout-mode.md` — use this when the user says `под ключ` or wants the optimization stream closed as a finite v1 package instead of continued micro-improvements.

Add session-specific notes, measured scenarios, or reusable examples under `references/` when a future optimization pass would benefit from exact telemetry patterns or sample probes.
