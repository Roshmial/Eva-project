# Harness teardown vs product regression

Use this note when a backend/chat test prints green assertions but the Python process dies afterward with errors like:
- `terminate called without an active exception`
- `Aborted`
- exit `134`

## Decision rule

Do not collapse these into one bucket.

Separate:
1. product logic outcome;
2. scenario-specific test race;
3. post-test harness / runtime-integration crash.

## Minimal triage sequence

1. Check whether the assertions themselves passed.
   - If the test body is green and the process dies only afterward, the failing layer is already suspiciously outside business logic.

2. Reproduce the same user scenario through a deterministic direct path.
   - Seed the thread state directly.
   - Create the `chat_tasks` row explicitly.
   - Run the backend processor once.
   - Inspect final message metadata and artifact output.

3. Inspect whether the HTTP test is double-executing the same task.
   - Common pattern: endpoint already calls `dispatch_chat_task_now(task_id)` and the test then also calls `process_chat_task(task_id)` manually.
   - If so, patch the test harness first: stub/patch immediate dispatch for that scenario so the smoke checks only one execution path.

4. Re-run a narrow targeted bundle.
   - If the scenario now passes cleanly, classify the original failure as harness race, not product regression.

5. If assertions still pass but the process aborts after completion even in direct `unittest`, keep that as a separate open defect.
   - Correct label: legacy teardown/runtime-integration crash.
   - Incorrect label: product route regression.

## What to report

Safe wording:
- product assertions passed;
- scenario-specific race was removed from the smoke path;
- legacy post-test abort remains and is not yet fixed.

Unsafe wording:
- `fixed the harness` when only one duplicate-execution race was removed;
- `product still broken` when the only remaining evidence is post-test abort after green assertions.

## Good verification bundle

For this class of issue, capture all three:
- narrow pytest bundle for the exact regressions;
- deterministic direct-path reproduction;
- note whether the remaining abort happens only after success output.
