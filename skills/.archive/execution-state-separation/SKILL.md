---
name: execution-state-separation
description: Use when job/tool states are being conflated.
---

# Purpose

This skill prevents a recurring class of confusion in operational and debugging conversations: mixing up different execution states and speaking as if they prove each other.

The core lesson: a stop in the agent loop, a completed request-processing task, a created cron job, a successful runtime execution, and a delivered user-visible result are different states. Do not collapse them.

## When to use

Use this skill when:
- diagnosing scheduled jobs, delivery incidents, or runtime failures;
- interpreting tool failures, guardrail halts, retries, or blocked calls;
- investigating whether a user-facing result actually happened;
- the user is frustrated because the agent described a technical event as business success.

## Core rule

Never describe a tool-loop stop, guardrail halt, request-processing completion, or setup completion as if it proves end-to-end task success.

Treat these as separate layers:
1. agent/tool execution state;
2. request-processing state;
3. job creation/scheduling state;
4. job run state;
5. delivery state;
6. user-visible content/result state.

## Required reporting pattern

When discussing incidents or execution state, always say which layer is confirmed.

Preferred wording:
- "Это stop на стороне агента, а не подтверждение, что задача выполнена."
- "Запрос обработан, но это не доказывает, что job исполнился."
- "Job исполнился, но это ещё не доказывает, что delivery состоялась."
- "Delivery состоялась, но нужно ещё проверить, что ушёл правильный контент."

Avoid wording like:
- "отработало", если подтверждён только tool stop;
- "выполнено", если подтверждено только создание job;
- "доставлено", если подтверждён только successful run без проверки delivery.

## Workflow

1. Identify the exact complaint.
- Missing run?
- Missing delivery?
- Empty or wrong content?
- Agent/tool failure during diagnosis?

2. Classify the observed evidence by layer.
- Tool halt / guardrail / repeated failure
- Request handled
- Job exists
- Job ran
- Delivery happened
- Correct payload reached the user

3. Report only the strongest proved layer.
- If the only evidence is a guardrail halt, say that plainly.
- If the only evidence is "job created", stop there.
- Do not jump across layers.

4. State the next missing verification step explicitly.
- "Нужно проверить output."
- "Нужно проверить delivery."
- "Нужно проверить, что сообщение попало в нужный тред."

## Pitfalls

### Pitfall: treating guardrail text as runtime success

A message like "I stopped retrying ... because it hit the tool-call guardrail" is only evidence that the agent stopped a bad tool loop. It says nothing about whether the user's real task, job, or delivery succeeded.

### Pitfall: reading cron/job UI optimism as end-to-end success

Statuses like completed/ok may belong to request handling or execution only. Keep delivery and final artifact verification separate.

### Pitfall: answering the previous topic instead of the current incident

If the user pivots from product/design discussion into runtime incident review, re-anchor immediately. Do not continue the old topic and accidentally answer a different question.

## User-specific note

This user reacts badly when state is overstated. In incident work, prefer blunt separation of states over smooth narrative wording.

## Support files

- See `references/tool-guardrail-vs-job-success.md` for a concrete incident pattern where a guardrail halt was mistaken for successful job execution.
