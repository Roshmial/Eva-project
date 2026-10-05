---
name: execution-mode-response-control
description: "Use when user wants execution, not analysis."
---

# Purpose

Use this skill when the user has already decided on the direction and is no longer asking for analysis, framing, or diagnosis. The job is to execute, verify, and report only grounded outcomes.

Typical triggers:
- the user says things like `делай`, `под ключ`, `исправь все`, `не объясняй`, `зачем сейчас объясняла?`, `сразу нельзя жестко?`
- the user reacts negatively to explanation-heavy turns during an implementation or debugging task
- the user is validating concrete defects and expects repeated patch → rerun → verify loops

## Core rule

Once the user flips into execution mode, stop spending turns on commentary about what is wrong. Apply the fix, run the check, and report the verified delta.

## Response contract in execution mode

Default output should be short and operational:
- what was changed
- what was run
- what the latest verified result is
- what still remains, only if a real blocker remains

Avoid reflective narration unless the user explicitly asks for it.

## Workflow

1. Translate the latest user complaint into explicit acceptance checks and preserve the requested delivery surface.
   - Example: `где ссылка?`, `бытовые хвосты`, `еще одна точка` becomes a hard verification checklist.
   - If the requested outcome is an interactive workbook, deployed UI, or runnable module, a CSV, static result file, README, copied template, or architecture note does not satisfy any part of that acceptance check unless the user explicitly changes the deliverable.
   - Treat a calculation engine, a one-off result, and a user-recalculable module as three different deliverables. State which one can actually be produced before writing supporting artifacts.
2. Validate the delivery path before building internals: confirm that the target environment can host, execute, and verify the requested mechanism. Surface a hard platform limitation before investing in substitute prototypes. Do not spend turns on architecture alternatives once the user asked to build; either execute the agreed path or name the blocker in one sentence.
3. Patch the governing artifact or runtime rule immediately.
4. Rerun the real path on the requested delivery surface.
5. Inspect the produced artifact or output and verify that the user can perform the requested action themselves (for example, recalculate rather than merely view results).
6. If the defect remains, patch again without pausing for a meta-explanation.
7. Finish only after the latest live run passes the stated checks.

## When the user corrects the mode of work

If the user says a reply should have been action instead of explanation:
- do not defend the earlier choice
- acknowledge once, in one sentence at most
- switch straight into substantive tool-using execution on the same turn
- do not label scaffolding, a copied file, a README, a plan, or a syntax check as work started; begin the governing calculation, edit, build, or live verification itself
- report only after there is observable output from that substantive operation

If the user calls out inactivity or says that nothing is being done, stop sending further acknowledgements. Start the highest-value executable step immediately and keep working until it produces a meaningful artifact or a concrete blocker.

When reporting that work is in progress, first establish observable execution: run the governing calculation/build/repair, preferably as a tracked background process if it is long-running, or complete a foreground step with material output. Do not describe a README, a copied file, a scaffolding edit, a delegated audit, or a completed short command as ongoing work. If no live process exists, say so plainly and start the actual workload in the same turn.

Delegation is a support step, not delivery. Do not end an execution turn solely to wait for a reviewer or subagent while the parent can still edit, build, run, or verify independently. Never promise that the finished artifact will arrive “in the next message”: either attach the verified artifact in the current final response or report the concrete external blocker that prevents producing it. After the user repeats that the requested deliverable is still missing, the next user-facing response must contain the deliverable or a proven blocker, not another status update.

## Pitfalls

- Explaining the defect class after the user already asked for a fix.
- Reporting intention instead of a verified rerun.
- Declaring success based on prompt edits or code edits without live output.
- Treating repeated user corrections as mere tone feedback instead of workflow correction.
- Letting a "better than before" result pass when the user asked for `под ключ`.

## Quality bar

For iterative quality-sensitive tasks, the acceptance bar is set by the latest user complaint, not by relative improvement over the previous run.

## Reference

- `references/execution-mode-corrections.md` — concrete examples of switching from analysis to hard execution after user pushback.
