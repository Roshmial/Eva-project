---
name: implementation-first-engineering-iterations
description: Use for iterative engineering and architecture work with this user when the goal is a practical improvement, especially token/cost/performance optimization. Prioritize the smallest measurable code change over architecture writeups.
---

# Purpose

This skill governs how to execute iterative engineering improvements for this user when the discussion sits between architecture and implementation.

The main lesson: do not drift into architecture documents, generalized frameworks, or broad redesigns when the user asked for quick wins. Start with the smallest safe implementation that produces measurable effect, verify it, and only then generalize one layer upward.

# When to use

Use this skill when:

1. The user asks for quick wins, practical improvements, or minimal-risk optimization.
2. The topic is architecture-adjacent, but the user wants code, tests, and measured results rather than design prose.
3. The work can be advanced by extending an existing local mechanism instead of introducing a new framework.
4. The user is frustrated by too much planning, documentation, or theoretical redesign.

Typical examples:

- token or context optimization in an agent loop
- incremental refactors around an existing implementation
- practical performance, cost, or payload reduction work
- extracting a small common layer only after multiple concrete wins already exist

# Core operating rule

Treat this class of work as an implementation-first investment loop:

1. Find the smallest existing mechanism that already works.
2. Extend it locally for one additional measurable win.
3. Add or update tests first or immediately alongside the change.
4. Verify with real execution, not only reasoning.
5. Measure the effect in chars, tokens, latency, payload size, or another concrete proxy.
6. Only after that, decide whether a thin shared abstraction is justified.

# Workflow

## 1. Re-anchor on the real ask

Before proposing anything bigger, restate the real objective in operational terms:

- what must get smaller, cheaper, faster, or safer
- what existing path already handles part of it
- what the smallest next extension could be

If the user asked for quick wins, the next question is usually not:

- what architecture should exist in theory

but:

- what is the next smallest low-risk implementation that reuses existing code and produces a measurable effect

## 2. Prefer local extension over new architecture

Default order:

1. reuse an existing mechanism
2. extend it to a nearby path
3. add telemetry or counters if measurement is missing
4. only then extract a shared selector/contract/reducer layer

Good pattern:

- exact reuse first
- then adjacent reuse in another path
- then telemetry
- then compact/delta/reference policy
- then shared contract
- then shared reducer
- only later a broader mediation framework if repeated wins prove the need

## 3. Keep every step thin and reversible

Each iteration should usually be one of these:

- one helper
- one dispatch layer
- one extra parameter threaded through existing call sites
- one new telemetry field set
- one prompt/content compaction rule
- one regression test block

Avoid multi-part rewrites unless a smaller route was actually tried and failed.

## 4. Verification is mandatory

For every implementation step:

1. run targeted tests that prove the missing behavior first when possible
2. implement the change
3. rerun targeted tests
4. run relevant regression suites
5. run a real or synthetic execution probe through production code paths
6. report measured effect with actual numbers

Do not stop at "implemented". Finish at "implemented, tested, executed, measured".

## 5. Summarize like an engineering decision note, not a pitch

Default response shape:

- short outcome
- what changed in code
- what was verified
- measured effect
- what this means structurally
- next smallest step

Keep it concrete. Avoid long architecture narratives unless explicitly requested.

# User-specific preferences embedded in this workflow

## The user dislikes token-heavy architecture detours

When the user asks for optimization or practical progress:

- do not spend turns on architecture documents, frameworks, or "v1 vision" prose unless explicitly requested
- do not treat writing plans as progress when code changes are possible now
- do not inflate a local fix into a broad architecture initiative prematurely

## The user prefers measurable quick wins

Always bias toward steps that can be reported with concrete evidence such as:

- chars saved
- prompt surface reduced
- payload reduced
- tests passed
- one more path covered by an existing optimization

## The user wants reuse of existing local mechanisms

Before adding anything new, explicitly check:

- what existing path already solves part of the problem
- whether the next step can be a thin adapter, selector, contract, or reducer on top of that path

# Pitfalls

## Pitfall: replacing the user's request with architecture ambition

Bad pattern:

- the user asked for token optimization
- the work drifts into general mediation design documents
- no immediate measured improvement is delivered

Correction:

- return to the nearest existing code path
- implement the next measurable win there
- generalize only after repeated working cases exist

## Pitfall: counting motion as progress

Do not present these as primary progress when implementation is feasible:

- long backlogs
- architecture notes
- framework naming
- future-state abstractions without code

## Pitfall: extracting a universal layer too early

Do not build a "solution for everything" first.

Instead:

- accumulate 2 to 4 concrete working cases
- identify the real common contract
- extract only the thin common surface those cases already prove

# Good next-step heuristic

After each successful iteration, ask:

1. What adjacent path can reuse the same trick?
2. What telemetry is missing to prove the effect?
3. Is there now enough repeated shape to justify a tiny shared abstraction?

If the answer to 3 is no, do another practical extension instead of abstracting.

# Deliverables checklist

Before closing the task, ensure you have:

- changed real code
- added or updated tests
- run the tests
- executed a real probe or measurement
- reported actual observed effect
- proposed the next smallest logical step

# References

- See `references/token-optimization-mediation-patterns.md` for a condensed pattern bank from a session that evolved from quick wins into selector, contract, descriptor, and reducer layers without a full rewrite.
