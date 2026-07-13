# Token optimization mediation patterns

This reference captures a durable execution pattern for practical token optimization work in an agent loop.

## Situation pattern

The user wanted token savings quickly and pushed back against spending tokens on architecture notes and framework design.

The durable lesson is not the exact codebase state. The durable lesson is the implementation order.

## Proven implementation order

1. Exact reuse for repeated heavy outputs within the same task scope.
2. Extend reuse to aggregate budget paths, not only the primary happy path.
3. Add telemetry immediately so wins are measurable.
4. Add cheap delta for append-only log-like outputs.
5. Add cheap delta for structured JSON top-level changes.
6. Add request-side short inclusion for persisted or reference-style results.
7. Add a minimal selector over existing `full / compact / reference / delta` behaviors.
8. Add a small shared policy contract.
9. Add a mediation descriptor that carries policy plus artifact and delta or reuse state.
10. Add a shared reducer that uses the descriptor to compact what actually reaches prompt history.

## Why this order works

- It starts with the safest and highest-confidence wins.
- Each step reuses existing code paths instead of introducing a second architecture.
- Measurement exists early, so later abstraction is justified by evidence.
- The eventual common layer emerges from repeated working cases instead of speculation.

## Safe abstraction ladder

When generalization becomes justified, prefer this ladder:

1. selector
2. contract
3. descriptor
4. reducer
5. only then a broader mediation framework if still needed

This order keeps abstraction thin and grounded in verified behavior.

## Measurement patterns worth preserving

Use real executed probes whenever possible. Good evidence includes:

- raw chars before and after
- live prompt-surface chars before and after
- chars saved by reuse
- chars saved by delta
- chars saved by prompt-side compaction
- count of policy selections by type
- regression tests covering both targeted behavior and adjacent paths

## Pitfalls

### Mistaking a successful branch optimization for a general solution

A strong local win is not yet a universal architecture. Report it honestly as a proven pattern in one or more paths.

### Extracting a framework before multiple real wins exist

Do not jump from one path directly to a universal layer. Use repeated wins to discover the real common contract.

### Reporting only implementation, not effect

A token optimization change without measured effect is incomplete for this user.

## Suggested reporting format for similar work

- what concrete code path changed
- what tests passed
- what real probe was run
- what numeric effect was observed
- what the next smallest adjacent step is
