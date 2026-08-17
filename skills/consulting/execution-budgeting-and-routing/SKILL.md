---
name: execution-budgeting-and-routing
description: Use when tasks drift into over-verification or slow routing.
version: 1.0.0
tags: [execution, routing, verification, latency, quality]
category: consulting
---

# Execution Budgeting and Routing

## When to use

Use this skill when:
- the user says a simple question took too long;
- a bounded question turned into a research loop;
- the agent failed to answer because it kept verifying instead of concluding;
- the user asks to analyze systemic causes of slow or overcomplicated execution;
- you need to design or tune agent behavior around speed vs certainty.

## Core idea

Do not classify tasks only by hardcoded phrasing patterns.

Instead, evaluate the task along three dimensions:
1. cheapest valid path — can the answer be produced by a short local calculation, direct read, or single-source check;
2. price of error — how costly is a wrong or weakly supported answer;
3. required certainty — does the user need an exact verified answer or a fast practical answer.

This produces an execution budget, not a brittle if/else route table.

## Recommended analysis frame

When diagnosing a failure, separate:
- facts from the actual execution trace;
- local stopers in the tool path;
- the deeper control-point failure;
- the policy change that would prevent recurrence.

Preferred causal ladder:
1. Was the task classified correctly?
2. Did the agent choose the cheapest valid first step?
3. Was there a bounded escalation budget?
4. Did the agent know when to stop and answer with bounded confidence?
5. Did later steps materially improve the answer, or only marginally increase confidence?

## Execution policy to recommend

### 1. Cheapest valid path first
Start with the lowest-cost action that could reasonably answer the request.

Examples:
- arithmetic/date/day counts -> compute first;
- question about a supplied page or file -> read that source first;
- single exact fact from a named source -> inspect that source first.

Do not start with broad search when a direct or local path already exists.

### 2. Bounded escalation
After the first step, ask whether there is still a material uncertainty.

If yes:
- allow one additional meaningful verification step.

If no:
- answer.

If the next step would only marginally improve confidence, stop instead of continuing the loop.

### 3. Bounded-confidence answer
When the cheap path produced a strong but not perfect answer, prefer:
- answer + one explicit assumption;
- or answer + one explicit limitation;

instead of open-ended digging.

### 4. Clear blocker rule
If the answer still cannot be supported after the allowed budget:
- say exactly what remains uncertain;
- say why the next step is blocked or low-value;
- stop.

## What to avoid

- Turning a one-number question into a multi-source research branch.
- Using the same verification intensity for a simple operational question and a high-stakes analytical claim.
- Treating "perfectly confirmed" as the only acceptable end state.
- Expanding to monthly, per-source, or per-document decomposition when the user asked only for a bounded result.
- Continuing search because another step is available, not because it is decision-relevant.

## User-specific note for Misha

When Misha points out that a simple question took too long, treat it as a systemic execution critique, not as a request for apology polish.

The useful response shape is:
- what exactly misrouted;
- what the real stopper was;
- which control point should change;
- what policy-level fix prevents recurrence.

Do not fall back to re-answering the original question unless he asks for that.

## Pitfalls

- Pitfall: diagnosing the problem as "one bad search" or "one slow tool".
  Fix: look for routing failure, missing escalation budget, and missing stop rule.

- Pitfall: proposing hardcoded phrase routing as the main fix.
  Fix: recommend adaptive execution policy based on cheapest valid path, price of error, and required certainty.

- Pitfall: saying "be faster" or "verify less" as the remedy.
  Fix: translate the issue into explicit policy controls: first-step choice, escalation cap, bounded-confidence answer, and blocker rule.

## Optional support files

- Add `references/` notes when a session yields a durable example of over-verification, latency caused by unnecessary search, or a concrete prompt/policy correction worth reusing.
