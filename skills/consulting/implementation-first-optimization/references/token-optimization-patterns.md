# Token optimization patterns from the 2026-07-11 Hermes session

Use this note as a concrete pattern bank when reducing token consumption in an existing agent loop without drifting into framework work too early.

## User workflow correction captured here

For this class of task, the user explicitly redirected the work away from architecture documents and toward immediate implementation.

Durable lesson:
- do not spend tokens on plans, framework notes, or broad architecture writeups when the ask is practical optimization
- deliver code, tests, telemetry, and measured effect first
- only generalize after several real wins exist

## Practical optimization sequence that worked

Recommended order for similar work:

1. inspect existing code paths and tests
2. identify the cheapest measurable win already supported by current mechanisms
3. add a focused failing or missing-behavior test when practical
4. implement the smallest safe patch
5. run targeted tests
6. run relevant regression
7. measure effect on the real path
8. only then extract a shared selector / contract / descriptor

## Concrete low-risk wins that proved valuable

### 1. Exact reuse for identical heavy outputs

Pattern:
- scope reuse by `task_id`
- match only exact content identity / digest
- reuse the same persisted artifact instead of rewriting or reinlining the payload
- emit a short reused-reference message instead of the full heavy output

Why this is a good first move:
- high savings
- very low correctness risk
- reversible
- no semantic diffing required

Measurement pattern:
- `persisted_total`
- `reused_total`
- `artifact_writes_total`
- `reuse_chars_saved_total`
- `live_chars_saved_total`

### 2. Aggregate turn-budget reuse

Do not stop at the ordinary persistence path.

If there is a later budget-enforcement pass that can also persist or compact tool outputs, propagate the same reuse logic there, including `task_id`.

Otherwise the system saves tokens in one branch but leaks them in another.

### 3. Append-only log delta

Pattern:
- maintain task-scoped cache keyed by task plus command family
- if the new log output is a strict append of the old one, emit only the appended portion plus minimal context
- keep the path cheap and deterministic

Good target cases:
- `tail`
- log readers
- repeated terminal inspection commands

Avoid overcomplicated diffing at first. Exact append detection is safer and cheaper.

Measurement pattern:
- `delta_reused_total`
- `delta_chars_saved_total`

### 4. Structured JSON top-level delta

Pattern:
- for repeated structured JSON outputs, diff only top-level keys first
- emit added / removed / changed key summary
- keep scope limited to the same `task_id` and command family

Why this works well:
- cheap implementation
- understandable output
- useful savings without semantic merge complexity

### 5. Request-side compact inclusion for persisted/reference results

Optimization is incomplete if large results are persisted but their prompt-side reference wrappers stay verbose.

Pattern:
- when a result is already `persisted-output` or reused reference, replace the prompt-side form with a short surface containing only:
  - what it is
  - whether it was reused
  - size
  - artifact path
  - `read_file` hint

This removes wasted prompt budget from the reference shell itself.

### 6. Minimal policy selector after repeated wins

Only after several repeated wins exist, add a tiny shared selector.

Useful first policy set:
- `full`
- `compact`
- `reference`
- `delta`

This is the right moment to start generalization, because there is already repeated behavior to unify.

### 7. Shared contract before shared framework

A good low-risk generalization step is a tiny shared contract describing:
- selected policy
- source
- raw chars
- surface chars
- chars saved
- whether the surface changed

This supports observability and future refactors without forcing a large architectural rewrite.

### 8. Mediation descriptor after contract

Next safe generalization step:
- wrap the policy contract in a small mediation descriptor
- include artifact path, raw-content availability, reuse flag, delta flag, and source
- propagate it through tool-result message construction

That lets later inclusion decisions use structured metadata instead of guessing from strings.

## Extraction rule

When moving from point fixes toward a broader design, prefer this ladder:

1. concrete win
2. telemetry
3. second win in a neighboring path
4. tiny selector
5. tiny contract
6. tiny descriptor
7. only then a broader mediation framework if still justified

## Pitfalls to avoid

### Don’t confuse terminal-branch improvement with a global solution

A terminal-specific optimization is still useful, but do not pretend it already solved the whole agent loop.

State clearly:
- what path is improved now
- what neighboring paths remain
- what evidence exists

### Don’t add architecture before evidence

If the user asks for optimization and you answer with plans and framework docs, that is negative value for this task class.

### Don’t skip telemetry

Without counters and measured before/after surfaces, optimization claims are weak and easy to overstate.

### Don’t use cross-task fuzzy reuse early

For early versions, keep reuse task-scoped and exact. Similarity-based reuse is a later step with higher correctness risk.

## Reporting pattern that worked well

Good report shape:
- what was implemented
- files changed
- tests run and actual outcome
- measured savings with concrete counts
- one next quick win

Bad report shape:
- broad framework narrative without shipped code
- roadmap-first explanation
- unmeasured claims of efficiency
