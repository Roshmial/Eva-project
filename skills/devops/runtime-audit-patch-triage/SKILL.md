---
name: runtime-audit-patch-triage
description: Use when Hermes must read Hermes Web runtime audit events, separate systemic failures from one-off noise, and prepare minimal grounded patches with regression tests.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [runtime-audit, hermes-web, triage, patching, logs]
    related_skills: [scheduled-hermes-monitoring, systematic-debugging, subagent-driven-development]
---

# Runtime Audit Patch Triage

## Overview

Use this skill for the Hermes Web runtime audit contour built around:
- `services/backend/data/runtime_audit.jsonl`
- `services/backend/daily_runtime_audit.py`
- backend app logic in `services/backend/app.py`
- regression coverage in `services/backend/test_smoke.py`

The goal is not to produce a noisy log summary. The goal is to convert recurring runtime audit signals into grounded patch candidates with the smallest safe fix surface.

## When to Use

Use when:
- daily runtime audit shows repeated error classes;
- the same degraded result appears across several users;
- a user asks for log triage plus likely patch directions;
- an internal cron/subagent should inspect recent runtime failures and prepare patch candidates.

Do not use when:
- there are zero audit signals;
- the issue is clearly external infrastructure and there is no code path to patch locally yet;
- the task is only to forward the raw audit report.

## Inputs to inspect first

1. Audit events:
   - `services/backend/data/runtime_audit.jsonl`
2. Daily report artifact if present:
   - `~/.hermes/cron/output/f000ef2be83c/`
3. Relevant backend paths:
   - `services/backend/app.py`
   - `services/backend/test_smoke.py`
4. Decision context:
   - `/home/hermes/workspace/decision-log.md`
5. Severity reference:
   - `references/severity-policy.md`

## Required workflow

1. Establish the real cluster.
   - Count repeated classes over the last 24h/72h.
   - Separate:
     - `chat_task_error`
     - `chat_task_degraded_result`
   - Use severity and priority metadata from `daily_runtime_audit.py` when available.
   - If the mapping looks questionable, check `references/severity-policy.md` before inventing an ad-hoc reinterpretation.
   - Prefer recurring multi-user classes over one-off noise.
   - Do not let a high-frequency low-severity class outrank a smaller but clearly high-severity cluster without saying so explicitly.

2. Inspect representative examples.
   - Read `request_preview`, `public_error_text`, `fallback_result_kind`, `status_note`.
   - Group by user intent, not just by raw string.

3. Find the exact code path.
   - Map the class to the narrowest handler in `app.py`.
   - Do not jump straight to patching broad helpers if the issue is route-specific.

4. Propose only grounded patch candidates.
   For each candidate include:
   - suspected root cause;
   - smallest file/function to change;
   - expected benefit;
   - risk of side effects;
   - what regression test must prove the fix.

5. If implementing, patch and verify.
   - Add or tighten the regression test first when practical.
   - Run targeted pytest for the touched path.
   - If the path is known to live inside noisy harness/teardown behavior, distinguish green assertions from harness-only aborts.

## Preferred output shape

Use this structure:

1. Main recurring classes
2. Severity and priority ranking
3. Likely root causes
4. Patch candidates
5. Required regression tests
6. What is still not proven

## Patch discipline

- Prefer local-first fixes in the existing backend/runtime.
- Do not introduce new databases, queues, or external observability services for a logic bug.
- Prefer tightening existing metadata, routing, fallback logic, or postguards before adding new moving parts.
- If a class looks like infrastructure noise, say so explicitly instead of disguising it as a code bug.
- When a repeated class is a missing precondition or misconfiguration (for example `hermes_api_key_missing`), separate three layers explicitly:
  1. proven code path where the error is raised;
  2. likely operational/config root cause;
  3. smallest local product patch that improves UX or reduces noisy task churn even before the environment is fixed.
- For configuration-induced classes, prefer narrow candidates such as clearer public error normalization, request-time preflight guards, or audit classification tweaks before proposing broader routing changes.
- Do not overfit to the user request text when the failure happens earlier in the stack. Example: a DOCX/export-flavoured prompt that fails on the first generic LLM call is not yet evidence of a DOCX route bug.

Reference note: see `references/config-induced-runtime-classes.md` for a compact pattern note on repeated configuration-driven audit classes.

## Subagent pattern

If using a subagent, give it:
- exact workdir: `/home/hermes/workspace/hermes-web-mvp-react-8793/services/backend`
- exact files to inspect;
- exact time window if relevant;
- instruction to return patch candidates, not generic advice;
- instruction to distinguish proven failures from hypotheses.

Good subagent goal:
"Read runtime_audit.jsonl for the last 72h, group repeated multi-user classes, map them to app.py code paths, and return at most 3 minimal patch candidates plus exact regression tests."

## Common pitfalls

Also see `references/severity-policy.md` for baseline class mapping, overrides, and exception handling.


1. Treating a single error string as a root cause.
2. Mixing product bugs with test harness noise.
3. Proposing a large refactor before a narrow deterministic fix is ruled out.
4. Counting every event equally instead of prioritizing repeated multi-user clusters.
5. Claiming a fix is complete without a regression test or real runtime proof.

## Verification checklist

- [ ] Repeated classes counted over a real recent window
- [ ] Multi-user repeats separated from one-off events
- [ ] Code path identified in `app.py`
- [ ] Minimal patch candidate stated with risks
- [ ] Regression test path identified or added
- [ ] Any unproven assumption explicitly labeled as hypothesis
