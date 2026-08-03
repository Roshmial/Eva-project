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

1. Translate the latest user complaint into explicit acceptance checks.
   - Example: `где ссылка?`, `бытовые хвосты`, `еще одна точка` becomes a hard verification checklist.
2. Patch the governing artifact or runtime rule immediately.
3. Rerun the real path.
4. Inspect the produced artifact or output.
5. If the defect remains, patch again without pausing for a meta-explanation.
6. Finish only after the latest live run passes the stated checks.

## When the user corrects the mode of work

If the user says a reply should have been action instead of explanation:
- do not defend the earlier choice
- acknowledge briefly
- switch straight into tool-using execution on the same turn

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
