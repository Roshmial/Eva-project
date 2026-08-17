---
name: adaptive-execution-budgeting
description: Use when a task may be answerable cheaply. Bound escalation.
triggers:
  - User asks a short factual, counting, date, or bounded verification question.
  - There is a risk of turning a simple request into an unnecessary research loop.
  - The task could be solved by a local calculation, direct read, or single-source check.
---

# Purpose

This skill prevents a simple task from expanding into a long verification chain. It applies an adaptive execution policy based on cost of the next step, material uncertainty, and the user's need for speed versus exhaustiveness.

# Core rule

Start with the cheapest valid path that could answer the request.

Escalate only when that path leaves a material uncertainty that actually matters to the user-facing answer.

# When to use

Use for classes of tasks like:
- counting days / working days / intervals;
- date arithmetic;
- bounded factual questions with one expected answer;
- direct source checks where the source is already known;
- short operational questions where the user wants the answer, not a research memo.

Do not use this as an excuse to skip necessary verification on high-risk tasks, ambiguous questions, or multi-source research.

# Execution policy

## 1. Classify by execution shape, not keyword alone
Assess the task on three axes:
- Is there a cheap local path?
- What is the cost of a wrong answer?
- Does the user need an exact answer, or a fast practical answer with bounded uncertainty?

Examples:
- `Сколько рабочих дней до конца мая 2027?` -> cheap local path exists; answer is bounded; user expects a number.
- `Какие часы работы у этого места сегодня?` -> direct-source check first.
- `Сравни 10 поставщиков` -> not this skill; that is research.

## 2. Use cheapest valid path first
Preferred order:
1. local calculation;
2. direct read of the exact source already in hand;
3. one lightweight external verification step;
4. broader research only if the cheaper path failed to resolve a material uncertainty.

## 3. Use bounded escalation
After one or two meaningful steps, force a decision:
- answer with the evidence in hand;
- answer with a clearly labeled assumption or uncertainty;
- or state the blocker plainly.

Do not keep digging when the next step is unlikely to change the answer materially.

## 4. Match output shape to the user's ask
If the user asked for one number, one date, one yes/no judgment, or one short fact, return that shape first.

Do not spontaneously expand into:
- month-by-month breakdowns;
- long legal/source audits;
- parallel search branches;
- explanatory detours about your process.

## 5. Separate sufficient confidence from maximal confidence
For bounded questions, prefer sufficient confidence over maximal confidence.

A correct, timely answer with one explicit caveat is often better than a 15-minute verification chain that never returns a result.

# Decision rule for escalation

Escalate only if at least one is true:
- the cheap path conflicts with the direct source;
- the answer materially changes based on missing evidence;
- the cost of error is high enough that a bounded answer is not acceptable;
- the user explicitly asked for strict verification or source-grade proof.

Otherwise stop early and answer.

# Reporting pattern

Default reporting shape:
- direct answer;
- one short evidence line if needed;
- one caveat only if it materially affects trust.

Examples:
- `По пятидневному производственному календарю это X рабочих дней.`
- `Точно по live-источнику сейчас не добила; по расчёту и найденному календарю выходит X.`

# Pitfalls

- Treating a simple counting question as open-ended research.
- Starting with web search when a local calculation or direct source read could answer the question.
- Expanding a one-number question into a month-by-month or source-by-source audit without being asked.
- Continuing verification after the answer is already unlikely to change.
- Optimizing for maximal certainty when the user primarily needs a fast bounded answer.
- Confusing `can verify more` with `must verify more`.

# For Misha

- He strongly dislikes long delays on simple bounded questions.
- He prefers a short correct answer, or an honest bounded answer with a clearly stated blocker.
- A simple question that drifts into a research loop counts as a workflow failure, not as carefulness.

# References

- Add session-specific examples and failure patterns under `references/` when this skill is exercised in real incidents.
