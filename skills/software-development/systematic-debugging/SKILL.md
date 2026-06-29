---
name: systematic-debugging
description: "4-phase root cause debugging: understand bugs before fixing."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, troubleshooting, problem-solving, root-cause, investigation]
    related_skills: [test-driven-development, plan, subagent-driven-development]
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Someone wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next.

---

## Phase 1: Root Cause Investigation

For web/chat backends, do not stop at green health endpoints. Add one real user-path probe: authenticate, create or open a thread, submit a message/task, and poll until the background job finishes. This separates API/queue health from downstream inference-runtime failures.

For chat/dashboard incidents, explicitly separate three layers before fixing anything: (1) backend state/derived fields such as `freshness_at`, `message_kind`, structured payloads, (2) parser/contract integrity such as wrapped JSON or shape drift, and (3) last-mile UI rendering or timestamp selection. A frequent production mistake is to keep patching backend data when the API already emits the right field and the only bug is that the frontend still reads `updated_at` or ignores structured metadata.

When the user says the issue is about prod, or names a specific live host/contour, treat local code and test environments as secondary evidence only. Verify and fix the named live contour directly, and do not claim prod is fixed until an authenticated live probe against that contour succeeds.

Before changing code in multi-user or multi-contour chat products, freeze the exact failing tuple: user/account, thread/job, host/port, and layer (DB/API/UI). Do not carry over assumptions from a previous incident just because the symptom text sounds similar. A common failure pattern is fixing a real backend bug for one user/thread, then misreading a later complaint that actually belongs to a different user, a different job-thread, or a different UI host. Reconstruct the tuple first, then verify where the fresh symptom lives.

In split or local-first runtimes, do not assume a visible host/port implies a separate machine or a separate deploy path. Before saying "no access" or planning a remote-only fix, verify where that surface is actually served from: current host, local systemd unit, reverse proxy, tunnel, or a different box. This avoids the common false branch where the real defect is already fixable in the current contour, but the investigation stalls on an imagined access boundary.

If the user says "it still isn't fixed" after a valid repair, do not defend the earlier diagnosis. Treat the new report as a fresh observation and immediately re-split the problem into: (1) data missing in storage, (2) API/serializer returning the wrong thing, (3) UI showing the wrong segment or scroll position, or (4) you patched the wrong live contour. In long chat threads, explicitly test whether the latest messages exist but are simply off-screen because initial positioning/auto-scroll is broken.

For chat products with specialized routes (dashboards, recurring jobs, exports, structured replies), inspect whether the failing turn actually used the intended route. Reproduce the exact follow-up turn, then compare the previous assistant message meta (`message_kind`, `downstream`, route-specific payloads such as dashboard metadata) with the failing task's `last_error`, timeout timing, and the actual messages sent to the generic LLM path. A short follow-up like “где диаграмма?” can fail not because of prompt size, but because it bypassed the earlier specialized route and fell back to the generic chat path, where a 180-second timeout surfaces as a misleading content/volume suspicion.

When a runtime/parser fix makes the task complete but the user still says the dashboard/report is “непонятно что отдал”, do not close the incident. Treat route correctness and content quality as separate checkpoints. Inspect the saved `assistant_message.content`, the persisted structured payload (`dashboard`, `web_sources`, route-specific meta), and the exact task history in storage. A live rerun that changes `status=error` to `status=completed` may still reveal a second defect in follow-up routing or retrieval quality.

For live chat-rendering incidents, explicitly compare three fields for the same affected message: raw stored `content`, persisted `meta.display_text`, and the final API serializer output returned to the UI. A common false branch is fixing only the frontend or only the write-time sanitizer while old assistant messages still leak stale `meta.display_text` on read. For recurring/job-delivery outputs, also inspect whether the saved text contains internal planning followed later by the real user-facing digest/report; in that case the fix is usually a read-time extractor anchored to the final artifact section, not a markdown/CSS tweak.

For retrieval/search-quality incidents, treat domain-specific hardcode as a red flag, not a fix. If one topic (for example BI) works only after special query branches or subject-specific boosts, assume the root cause is in generic subject extraction, intent inference, candidate-set scoring, or post-fetch relevance validation. Validate the repair on at least one unrelated topic class (for example consumer or market-overview queries) before declaring success; otherwise you may have solved one subject by contaminating the planner for every other subject.

If the bad retrieval is driven by acronym-heavy subjects or hybrid tokens (for example `BI-инструментов`, `BI-практик`), inspect the generated search profile before changing ranking logic. Check four things explicitly: extracted `subject`, expanded acronym forms, ordered `subject_phrases`, and the first several generated search queries. The root cause is often that the planner anchors on malformed hybrid phrases while the real broad query (`business intelligence`) appears only as a weak tail or not at all. Fix the generic subject/query normalization first, then rerun the same live task and verify the stored selected sources are now topically sane.

When retrieval quality still looks irrational after local planner fixes, compare candidate sets on the named live contour before touching post-fetch ranking again. Run the planner functions server-side and inspect, per early query family, both returned URLs and `score_web_candidate_set()`. Search backends can diverge sharply between local and live environments; if the live contour returns non-topical but non-empty sets, harden broad-first query ordering and weak-set penalties instead of adding subject-specific branches.

When fixing generic web-retrieval planners, do not over-correct into early exact-match / quoted-phrase search. For ordinary "find what exists on the web" requests, prefer a broad subject-first first pass, then use quoted or narrower variants only as later fallbacks. Also check whether the source-count cap is itself suppressing quality: if top-N is too small, the planner can appear "relevant" only because it never had enough room to surface a diverse candidate set. Verify both relevance and breadth by testing at least one unrelated topic and by inspecting the final selected-source count, not just the first 5 preview rows. See `references/generic-web-retrieval-planner.md`.

For auth/session incidents, do not stop at the configured TTL or the login success path. Inspect live session state in storage: `created_at`, `last_seen_at`, `revoked_at`, and any computed expiry. Distinguish three different questions: (1) what TTL is configured, (2) which requests actually touch/refresh the session, and (3) whether writes are throttled by a touch interval. A common false conclusion is "TTL is one hour from last activity" when the real bug is that ordinary authenticated requests validate the token but never advance `last_seen_at`, so the session still dies one hour after login. When validating a fix, use a live probe that ages `last_seen_at` past the touch interval but not past TTL; an immediate request right after login may correctly show no timestamp change and is not proof that refresh is broken.

If the flow produces files/attachments, extend the probe past `message_kind=file_response`: verify whether the attachment was built from the correct source. Inspect backend state (for example `source`, `exported_message_id`, `generated_from_request`, `preview_excerpt`) and then fetch the attachment over HTTP to confirm content type and bytes. Otherwise a system can look “green” while silently exporting a stale previous answer instead of generating a new one.

For multi-turn file-generation flows, inspect whether the backend preserves the original export intent across clarification turns. A common production failure is: user explicitly asks for `pptx`/`docx`, assistant asks a clarification question, user answers briefly without repeating the format, and the route silently falls back to generic chat or the wrong export path. Verify the exact route decision on the failing turn, add a regression test at that decision point, and confirm with a live probe that the final artifact still has the requested format.

When a generated-file path builds a synthetic message row for reuse by export helpers, preserve the same minimum schema shape as a real stored assistant message. In practice that often means including fields like `role`, `content`, `created_at`, and `meta_json`; otherwise the file route can pass unit-level route checks yet fail in live runtime with key/shape errors only when attachment creation begins. See `references/generated-file-clarification-and-row-shape.md`.

If an HTTP-created chat task appears stuck in `running` during smoke tests, do not assume the product route regressed. First check whether the endpoint already triggered immediate dispatch and the test is now racing a second manual `process_chat_task(...)` call. In that case, verify the same scenario through a deterministic direct-path reproduction (seed the thread state, create the task row explicitly, run the backend processor once) and compare message metadata / artifact output before calling it a real regression.

If targeted assertions pass but the test process aborts only after completion (`terminate called without an active exception`, `Aborted`, exit 134, similar teardown-only crashes), classify that separately from product logic. First answer three questions explicitly: (1) did the assertions themselves pass, (2) does the same scenario pass in a deterministic direct-path reproduction, and (3) is the abort tied to the harness lifecycle rather than the business route. If yes, record the product behavior as confirmed-but-harness-noisy instead of claiming a regression fix or a full harness repair. Where possible, stabilize the specific smoke by removing duplicate execution paths (for example patching immediate dispatch in HTTP tests that also call the processor manually), but keep the remaining post-test abort as an open harness/runtime-integration defect until it is isolated on its own. See `references/harness-teardown-vs-product-regression.md`.

For generated-document/export incidents, distinguish product regressions from regression-drift caused by an intentional upgrade in document structure. If the new `DOCX/PPTX` layout deliberately moves the same content into better native structures (for example label/value rows, additional title metadata tables, separate table slides/cards), do not treat old assertions like exact paragraph linearization, exact table count, or one-line string joins as source-of-truth. First verify the artifact semantically: content is present, formatting markers survive, apology/tool transcript does not leak, and the live file opens with the intended structure. Then update the regression to assert semantic guarantees instead of the previous incidental serialization shape. See `references/generated-document-artifact-vs-regression-drift.md`.

For presentation-generation incidents that pass through `draft -> markup -> export`, force an early split between route-context bugs and export-segmentation bugs. Verify separately whether the follow-up rebuilt the whole deck or only the tail after clarification, and whether the exporter understands explicit slide markers like `Слайд 1: ...` without promoting inner bold headings into new slides. In this class of bug, a live improvement is only believable when both checkpoints move together: the follow-up reply restarts from the beginning of the deck, and the exported slide titles align with real slide headings rather than subsection labels. See `references/presentation-followup-and-explicit-slide-export.md`.

For recurring audits or cron scripts that read a live runtime `duckdb`, treat lock contention as a coexistence problem, not automatically as an application failure. If an auxiliary read (for example user-label enrichment) hits a lock while the runtime owns the DB, prefer a lock-tolerant path that degrades that optional enrichment and still delivers the main audit result. Otherwise the monitoring job turns healthy runtime activity into false-red cron noise.

For `generate-and-attach` flows, do one extra check: verify the generated document content itself is semantically valid, not just downloadable. Look for tool/service transcript leakage (`<tool_code>`, `write_file(...)`, retry/apology text, parameter-error chatter) in `preview_excerpt`, DB state, and downloaded content. A common failure mode is that the backend correctly creates a real `.docx`, but packages raw chat/tool transcript instead of the intended document body. When that happens, the root fix is usually an explicit output contract for the generated-file path plus backend-side validation before attachment creation.

If that output-contract fix is already in place but the original production thread still times out while a fresh acceptance thread passes, suspect long-history prompt contamination. Inspect whether the generate-and-attach path is still sending the full thread (including prior file loops, `file_response`, `processing_status`, apology/retry chatter, and short technical turns). In that case, verify on the original problematic thread and prefer building a focused context from substantive user/assistant turns before simply raising timeouts.

References: `references/backend-live-verification.md`, `references/chat-file-routing-verification.md`, `references/generated-file-output-contract.md`, `references/generated-file-long-history-context.md`, `references/generated-document-artifact-vs-regression-drift.md`, `references/live-contour-last-mile-debugging.md`, `references/hermes-web-dashboard-followup-and-retrieval.md`, `references/split-user-contour-triage.md`

**BEFORE attempting ANY fix:**

### 1. Read Error Messages Carefully

- Don't skip past errors or warnings
- They often contain the exact solution
- Read stack traces completely
- Note line numbers, file paths, error codes

**Action:** Use `read_file` on the relevant source files. Use `search_files` to find the error string in the codebase.

### 2. Reproduce Consistently

- Can you trigger it reliably?
- What are the exact steps?
- Does it happen every time?
- If not reproducible → gather more data, don't guess

**Action:** Use the `terminal` tool to run the failing test or trigger the bug:

```bash
# Run specific failing test
pytest tests/test_module.py::test_name -v

# Run with verbose output
pytest tests/test_module.py -v --tb=long
```

### 3. Check Recent Changes

- What changed that could cause this?
- Git diff, recent commits
- New dependencies, config changes

**Action:**

```bash
# Recent commits
git log --oneline -10

# Uncommitted changes
git diff

# Changes in specific file
git log -p --follow src/problematic_file.py | head -100
```

### 4. Gather Evidence in Multi-Component Systems

**WHEN system has multiple components (API → service → database, CI → build → deploy):**

**BEFORE proposing fixes, add diagnostic instrumentation:**

For EACH component boundary:
- Log what data enters the component
- Log what data exits the component
- Verify environment/config propagation
- Check state at each layer

Run once to gather evidence showing WHERE it breaks.
THEN analyze evidence to identify the failing component.
THEN investigate that specific component.

### 5. Trace Data Flow

**WHEN error is deep in the call stack:**

- Where does the bad value originate?
- What called this function with the bad value?
- Keep tracing upstream until you find the source
- Fix at the source, not at the symptom

**Action:** Use `search_files` to trace references:

```python
# Find where the function is called
search_files("function_name(", path="src/", file_glob="*.py")

# Find where the variable is set
search_files("variable_name\\s*=", path="src/", file_glob="*.py")
```

### Phase 1 Completion Checklist

- [ ] Error messages fully read and understood
- [ ] Issue reproduced consistently
- [ ] Recent changes identified and reviewed
- [ ] Evidence gathered (logs, state, data flow)
- [ ] Problem isolated to specific component/code
- [ ] Root cause hypothesis formed

**STOP:** Do not proceed to Phase 2 until you understand WHY it's happening.

---

## Phase 2: Pattern Analysis

**Find the pattern before fixing:**

### 1. Find Working Examples

- Locate similar working code in the same codebase
- What works that's similar to what's broken?

**Action:** Use `search_files` to find comparable patterns:

```python
search_files("similar_pattern", path="src/", file_glob="*.py")
```

### 2. Compare Against References

- If implementing a pattern, read the reference implementation COMPLETELY
- Don't skim — read every line
- Understand the pattern fully before applying

### 3. Identify Differences

- What's different between working and broken?
- List every difference, however small
- Don't assume "that can't matter"

### 4. Understand Dependencies

- What other components does this need?
- What settings, config, environment?
- What assumptions does it make?

---

## Phase 3: Hypothesis and Testing

**Scientific method:**

### 1. Form a Single Hypothesis

- State clearly: "I think X is the root cause because Y"
- Write it down
- Be specific, not vague

### 2. Test Minimally

- Make the SMALLEST possible change to test the hypothesis
- One variable at a time
- Don't fix multiple things at once

### 3. Verify Before Continuing

- Did it work? → Phase 4
- Didn't work? → Form NEW hypothesis
- DON'T add more fixes on top

### 4. When You Don't Know

- Say "I don't understand X"
- Don't pretend to know
- Ask the user for help
- Research more

---

## Phase 4: Implementation

**Fix the root cause, not the symptom:**

### 1. Create Failing Test Case

- Simplest possible reproduction
- Automated test if possible
- MUST have before fixing
- Use the `test-driven-development` skill

### 2. Implement Single Fix

- Address the root cause identified
- ONE change at a time
- No "while I'm here" improvements
- No bundled refactoring

### 3. Verify Fix

```bash
# Run the specific regression test
pytest tests/test_module.py::test_regression -v

# Run full suite — no regressions
pytest tests/ -q
```

### 4. If Fix Doesn't Work — The Rule of Three

- **STOP.**
- Count: How many fixes have you tried?
- If < 3: Return to Phase 1, re-analyze with new information
- **If ≥ 3: STOP and question the architecture (step 5 below)**
- DON'T attempt Fix #4 without architectural discussion

### 5. If 3+ Fixes Failed: Question Architecture

**Pattern indicating an architectural problem:**
- Each fix reveals new shared state/coupling in a different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

**STOP and question fundamentals:**
- Is this pattern fundamentally sound?
- Are we "sticking with it through sheer inertia"?
- Should we refactor the architecture vs. continue fixing symptoms?

**Discuss with the user before attempting more fixes.**

This is NOT a failed hypothesis — this is a wrong architecture.

---

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals a new problem in a different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (Phase 4 step 5).

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence, trace data flow | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare, identify differences | Know what's different |
| **3. Hypothesis** | Form theory, test minimally, one variable at a time | Confirmed or new hypothesis |
| **4. Implementation** | Create regression test, fix root cause, verify | Bug resolved, all tests pass |

## Hermes Agent Integration

### Investigation Tools

Use these Hermes tools during Phase 1:

- **`search_files`** — Find error strings, trace function calls, locate patterns
- **`read_file`** — Read source code with line numbers for precise analysis
- **`terminal`** — Run tests, check git history, reproduce bugs
- **`web_search`/`web_extract`** — Research error messages, library docs

### With delegate_task

For complex multi-component debugging, dispatch investigation subagents:

```python
delegate_task(
    goal="Investigate why [specific test/behavior] fails",
    context="""
    Follow systematic-debugging skill:
    1. Read the error message carefully
    2. Reproduce the issue
    3. Trace the data flow to find root cause
    4. Report findings — do NOT fix yet

    Error: [paste full error]
    File: [path to failing code]
    Test command: [exact command]
    """,
    toolsets=['terminal', 'file']
)
```

### With test-driven-development

When fixing bugs:
1. Write a test that reproduces the bug (RED)
2. Debug systematically to find root cause
3. Fix the root cause (GREEN)
4. The test proves the fix and prevents regression

## Real-World Impact

From debugging sessions:
- Systematic approach: 15-30 minutes to fix
- Random fixes approach: 2-3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: Near zero vs common

**No shortcuts. No guessing. Systematic always wins.**
