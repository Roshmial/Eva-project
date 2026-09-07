---
name: execution-finalization-discipline
description: Use when a task requires real actions or fixes. Verify against completion rules before any final status.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [finalization, verification, discipline, completion, execution]
    related_skills: [brief-response-delivery, implementation-first-delivery, hermes-agent]
---

# Execution Finalization Discipline

## Overview

Use this skill when the user asks not just for analysis, but for real work: fix, update, install, verify, investigate, clean up, or "finish all tails". The purpose is to prevent premature closure and force a final verification pass before reporting completion.

## When to Use

- The task requires changing files, config, packages, services, data, or runtime state.
- The user asks to "доделай", "под ключ", "проверь окончательно", "исправь", "обнови", or similar.
- There are explicit success criteria, warnings, blockers, or post-change checks.

Do not use for:
- Pure brainstorming or opinion-only answers.
- Cases where no system/tool action is required.

## Core Rule

If work was performed, do not treat the task as complete until the result is checked against the completion rules below.

Interpret the user's completion bar literally. If the user says "доделай", "под ключ", "все хвосты", or an equivalent hard-close request, do not silently downgrade the target to "critical items only" or "good enough to work".

Execution persistence rule:
- Do not stop at a correct diagnosis or an honest partial-status report if the next remaining work is still local, obvious, and low-risk.
- Keep working until one of these stop conditions is true:
  1. the requested scope is actually closed;
  2. the remaining step would require a material architecture change;
  3. the remaining step would create a destructive or high-risk side effect;
  4. the remaining step needs an explicit user decision, secret, access, or policy choice.
- If none of these stop conditions applies, continue the task instead of reporting "not done yet" as if that were the deliverable.

## Gateway restart continuation rule

When a live task requires restarting a gateway/service, a restart is an implementation step, not a handoff or completion point.

- Do not send a status-only reply such as “gateway restarted; дальше продолжу” and stop while the original task remains actionable.
- Before restarting, preserve the task's exact next operation and acceptance criterion.
- After the service is healthy, immediately resume that operation in the same execution cycle; report the user-facing result, not merely service liveness.
- For a gateway restart, do not infer recovery from systemd alone: after restart, verify that the chat platform is connected and send an explicit recovery/continuation message into the affected chat before treating the restart as complete. Use a delivery path independent of the restarted gateway when necessary.
- Treat service liveness as a prerequisite check. It never substitutes for completion of the user’s original request.
- Restart only once per coherent change set unless a later verified failure requires another change.

## Completion Rules

Before any final answer, explicitly verify:

1. Requested action actually happened.
- Check the real artifact, runtime, command output, file, service, version, or UI state.
- Do not infer success from a likely command path.

2. Remaining tails are enumerated.
- Ask: is anything still open that the user would reasonably count as part of this task?
- If yes, do not present the state as final.

3. Warnings are classified correctly.
- Distinguish:
  - closed;
  - open but non-blocking;
  - blocked by external constraint.
- Never hide an open item behind wording like "almost done" or "basically works".

4. "Done everything" requests use zero-tail discipline.
- If the user asked for "доделай", "все хвосты", or "под ключ", treat every actionable warning/advisory as in scope unless clearly out of scope or externally blocked.
- If something remains, state it as an unfinished item, not as background color.

5. Final status must match evidence.
- "Done" is allowed only when the requested scope is actually closed.
- "Partially done" is required when residual work remains.

6. Do not convert an actionable tail into background commentary.
- If a warning, advisory, or follow-up can realistically be fixed in the current task, keep it in the active scope.
- Only move it out of scope when it is explicitly blocked, irrelevant to the user's ask, or requires a separate approved side effect.

7. Do not issue a premature near-final report.
- Avoid phrases like "почти всё готово", "в целом всё готово", or similar when open actionable work remains.
- Intermediate progress reports are allowed only when they are explicitly framed as non-final.

## Required Final Check Format

Before finalizing, run this internal checklist:

- What exactly did the user ask to finish?
- What is the literal completion bar implied by that wording?
- What actions were actually performed?
- What evidence confirms each action worked?
- What remains open?
- Is each remaining item actionable now?
- Would the user see any remaining item as a tail?

If the answer to the last question is yes, do not give a final-complete framing.

## Reporting Rules

Good final phrasing:
- "Сделано: X, Y, Z. Остался незакрытый пункт: N."
- "Основная часть сделана, но задача не закрыта полностью из-за N."
- "Полностью закрыто; проверка показала A, B, C."

Bad final phrasing:
- "В целом всё готово", if actionable residuals remain.
- "Некритично", if the user explicitly asked to finish all tails.
- "Должно работать", when verification was still possible but not yet done.

## Common Pitfalls

1. Early victory report.
- Symptom: reporting completion after the main fix while warnings/advisories still remain.
- Correction: inspect all residual warnings before final framing.

2. Reframing user scope downward.
- Symptom: user asked for full cleanup, but the answer quietly narrows scope to "critical only".
- Correction: keep the user's stronger completion standard.

3. Treating policy checks as irrelevant by default.
- Symptom: doctor/audit/advisory warning left unresolved without checking whether it is actionable.
- Correction: first test whether it can be removed safely; only then classify it as blocked or out of scope.

4. Reporting a milestone as the finish line.
- Symptom: the main fix is done, but cleanup, audit, advisory, or final verification is still pending.
- Correction: keep milestones labeled as intermediate until the closure checklist is fully green.

## Verification Checklist

- [ ] Real actions were performed, not just described.
- [ ] Outcome was verified by tool output or artifact inspection.
- [ ] All remaining warnings/advisories were reviewed.
- [ ] Any residual item is clearly labeled open or blocked.
- [ ] Final wording does not overstate completion.
- [ ] For "finish all tails" tasks, no actionable tail is left unnamed.
