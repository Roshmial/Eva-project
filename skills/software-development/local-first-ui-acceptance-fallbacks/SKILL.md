---
name: local-first-ui-acceptance-fallbacks
description: Fallback acceptance patterns for local-first web UIs when full live runtime verification is partially blocked but code and renderer behavior still need grounded proof.
---

# Purpose

Use this skill when a local-first web UI must be verified end-to-end, but the primary live verification path is only partially healthy. Typical examples:
- browser/CDP screenshot or snapshot paths are unstable;
- full authenticated boot returns partial 5xx responses after login;
- the UI renderer itself may still be correct, but the surrounding runtime path is noisy;
- you need a truthful acceptance result instead of either hand-waving success or blocking on an unrelated contour issue.

This skill is about *salvaging grounded verification without lying*. It does **not** replace full live acceptance when the full contour is healthy.

# When to trigger

Trigger this skill if **all** are true:
1. The task requires proving a frontend behavior, renderer change, or UI contract.
2. Build/test can still be run locally.
3. The main live path is impaired by an adjacent runtime issue that is real but not identical to the feature under test.
4. A narrower, isolated verification path can still prove the specific claim.

# Core rule

Separate:
- what is proven by real backend/build/runtime outputs;
- what is proven only by isolated frontend DOM acceptance;
- what remains blocked by a different runtime incident.

Never collapse those into one blanket "works" statement.

# Procedure

1. Run the normal code-level checks first.
   - backend tests/smokes for the changed contract;
   - frontend build for parser/renderer changes;
   - basic health checks for the local surface.

2. Try the ordinary live UI path.
   - If it works, use it and stop here.
   - If it fails, capture the failure class precisely: e.g. login succeeds but post-login bootstrap/me/files/threads/jobs requests return 503.

3. Decide whether the failing path is *adjacent* rather than *core* to the feature.
   - Example: markdown rendering change is still testable even if full boot after login is flaky.
   - Example: file preview renderer can still be tested if the same DOM receives mocked file metadata.

4. Build an isolated prod-like frontend acceptance path.
   - Serve the real built frontend.
   - Use a headless browser to intercept `/api/**` calls.
   - Mock only the minimum boot/session/thread payloads needed to reach the target UI state.
   - Preserve the real browser DOM, real React code, and real event flow.

5. Verify the exact user-visible claim with DOM assertions.
   - Assert normalized rendered text, not just raw source.
   - Assert structural elements (`table`, headers, cells, preview nodes, buttons, etc.).
   - Assert the *absence* of the old broken token/path where relevant.

6. Report results in three buckets.
   - Confirmed: what the isolated and real checks proved.
   - Blocked/adjacent incident: what prevented full live acceptance.
   - Remaining next step: the smallest follow-up needed to close the adjacent incident.

# Good acceptance shape

A good result looks like this:
- backend regression test passes;
- frontend build passes;
- local health endpoints respond;
- headless DOM pass proves the exact renderer behavior;
- final report explicitly states that full authenticated live flow is still affected by a separate boot/runtime issue.

# Pitfalls

- Do **not** claim "live verified" if the only proof came from mocked API interception.
- Do **not** abandon verification entirely just because browser screenshot/CDP was flaky; switch to a narrower proof path.
- Do **not** over-mock: the goal is real frontend code plus minimal mocked API state, not a synthetic unit test disguised as acceptance.
- Do **not** hide the adjacent incident. The fallback proves the feature; it does not erase the runtime problem.
- If a tokenized download URL or similar contract is intentionally richer than a previous exact assertion, relax the test to the stable invariant (`startswith`, required fields present) instead of forcing a brittle exact string.

# Verification checklist

Before finalizing, explicitly confirm:
1. Which checks were fully real: tests/build/health.
2. Which checks used isolated mock-boot DOM acceptance.
3. Which user-visible behavior was directly asserted.
4. Which remaining runtime issue still exists, if any.
5. That the final wording does not overstate proof.

# Support files

- See `references/frontend-markdown-mock-boot.md` for a concrete mock-boot DOM acceptance recipe and reporting pattern from a Hermes Web markdown/self-check session.
