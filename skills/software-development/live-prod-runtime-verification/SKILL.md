---
name: live-prod-runtime-verification
description: Verify and harden a live local-first/prod runtime by checking the actual contour, separating code-state from deployed-state, and closing common failure classes around routing, document ingestion, session continuity, and model-output guards.
---

# When to use

Use this skill when the task is about a live Hermes-style web/runtime contour and the user expects factual verification on the real target, not architectural speculation. Typical triggers:

- frontend/backend routing errors on a named host/port
- UI/runtime bugs that must be reproduced in the live app
- discrepancies between code fixes and deployed behavior
- attachment/document ingestion failures in chat workflows
- session expiry / continuity problems in long-running chats
- unstable or malformed LLM outputs that need server-side guardrails

# Core operating rules

1. Start from the named runtime contour.
   - If the user names a specific server, host, port, or contour, treat that as the primary verification target.
   - Do not drift into generic SSH/network speculation when the user expects direct runtime validation on that contour.

2. Separate three states explicitly:
   - code state: what is fixed in the working tree
   - runtime state: what the live service currently does
   - deployed state: whether the live runtime actually includes the code fix

3. Prefer proof over inference.
   - Verify proxying with live HTTP endpoints.
   - Verify UI issues with a real browser/runtime path where possible.
   - Verify backend logic with targeted tests for the exact failure class.

4. When reporting, split:
   - confirmed facts
   - remaining assumptions
   - what is fixed in code
   - what is still not proven on prod

# Workflow

## 1. Confirm the contour first

Map the live route before touching code:
- frontend host:port
- backend host:port
- expected upstream relation
- health/service-info endpoints
- backend bind host actually used at runtime (`127.0.0.1` vs `0.0.0.0`)

For proxy failures, confirm whether the frontend points at the real backend target or an outdated localhost/loopback upstream.

Important pitfall:
- A backend restart can silently regress the contour even when the code is correct: the service may come back bound to `127.0.0.1` because `HERMES_WEB_BACKEND_HOST` was not pinned in the runtime env.
- In a split contour where another host proxies to the backend by external IP, this recreates `frontend_proxy_upstream_unavailable` immediately after restart.
- Fix the runtime env, not just the process: persist `HERMES_WEB_BACKEND_HOST=0.0.0.0` (or the contour-appropriate bind) before calling the incident closed.

## 2. Reproduce the failure in the right layer

Classify the issue before fixing:
- routing/proxy
- auth/session
- UI render/runtime exception
- attachment ingestion / extraction
- model-quality / post-generation failure

Do not merge these into one vague “frontend broken” bucket.

## 3. For UI/admin failures

Check both visibility conditions and runtime exceptions.
- First confirm whether the control should render for the current role/device.
- Then check browser console/runtime errors.
- A missing handler or miswired prop can make an admin screen look “inaccessible” even when navigation is present.
- Do not stop after the first fixed exception. Re-open the same screen on the live surface and exercise at least one deeper tab/action, because admin screens often fail as a chain of missing handlers (`fix A` just exposes `fix B`).

Deployment note:
- If the named frontend is a local user-systemd prod surface, rebuild the frontend bundle and restart the actual prod service before declaring the UI fixed.
- In this class of contour, the live service may be a local `systemctl --user` unit (for example a `hermes-web-frontend-8803.service`) even when the public host is remote-facing.

## 4. For document-ingestion failures

Always inspect both structure coverage and volume limits.

Check:
- upload size limit
- number-of-files limit
- extracted-text truncation limit
- inline preview truncation limit
- format-specific structure coverage
- runtime dependencies actually installed in the deployed venv/service env

Minimum structure review by format:
- DOCX: paragraphs, tables, headers, footers
- XLSX: sheets and row/cell text
- PPTX: slide text, tables, notes
- PDF: extracted page text and fallback note when OCR/parser support is absent

A common pitfall is thinking the parser “missed content” when the real cause is truncation after extraction.

Verification pattern:
- Do not stop at unit tests.
- Generate or upload small marker-based sample files (`HEADER-ALPHA`, `TABLE-BETA`, `NOTE-GAMMA` style probes) through the real API and inspect the returned `text_extracted`, `extraction_note`, and preview fields.
- This catches the important difference between “code path exists” and “runtime dependencies are installed and the deployed service actually extracts the content”.

## 5. For session-expiry bugs

Verify whether TTL is anchored to:
- login time
- or last user activity

Check both:
- the expiry calculation function
- the runtime/session-touch path that updates last activity

A correct formula with a wrong default TTL is still a production bug.

## 6. For long-chat continuity after LLM resets

Do not rely only on raw message replay.

If chat history can grow large, add a server-side continuity mechanism:
- persist the full message history in the app DB
- detect long/large histories
- compress the older part of the same chat into a factual summary
- send summary + recent tail to the model
- expose metadata that compaction happened

This is the durable pattern for “LLM session reset but same app chat should continue coherently”.

## 7. For unstable/bad LLM outputs

Add post-generation publish guards on the backend.

At minimum block or fail closed on:
- tool transcript leakage
- obviously broken technical/runtime dumps
- repetitive garbage / looping output
- claims that an attachment/file exists when no real artifact exists

Treat this as a backend publication gate, not just a prompt-quality problem.

## 8. Verify with narrow tests

After code changes, add targeted tests for the new risk area instead of relying only on broad smoke tests.
Examples:
- session TTL default and expiry behavior
- DOCX table/header extraction
- XLSX/PPTX extraction paths
- long-chat compaction path
- malformed LLM-output rejection

## 9. Safe live-patch discipline

When the fix touches a live Python/JS runtime, do not improvise directly inside the production file with ad-hoc heredocs, line-number rewrites, or stacked one-off debug injections.

Minimum discipline:
- first read the exact target block from the live file and the local/source copy
- prepare the patch in a standalone local file or deterministic script
- validate syntax before restart (`python -m py_compile` for Python, build/lint for frontend)
- keep a rollback handle (backup file, git diff, or explicit copied original)
- restart only after the edited artifact is proven syntactically valid
- after restart, run one real user-path probe, not just health

Escalation rule:
- if one live patch attempt fails because of quoting/indentation/syntax, stop stacking more blind edits on top of the damaged file
- restore or inspect the exact current file state first, then prepare the next patch off-box or on a temp copy
- if two patch attempts fail, switch to a safer delivery path (scripted patch, copied file replacement, or source-side edit + redeploy) instead of continuing inline surgery

# Pitfalls

- Proving only the code fix and not the deployed behavior.
- Looking only at parser logic and forgetting extraction truncation limits.
- Assuming “history is stored in DB” is enough for chat continuity under model resets.
- Treating bad LLM output as a prompting issue instead of adding a publication guard.
- Reporting prod as fixed when only the working tree and tests are fixed.

# Output contract for the user

When you finish, give a short operational summary:
- what is confirmed live
- what is fixed in code
- what still requires rollout/deploy/restart
- what dependencies are still needed for full capability

# References

- See `references/runtime-verification-checklist.md` for a concise checklist covering routing, admin runtime, document ingestion, session continuity, and LLM post-guards.
- See `references/prod-contour-rollout-pitfalls.md` for concrete runtime lessons about bind-host regressions after restart, local user-systemd frontend surfaces, chained admin-screen handler failures, and live marker-file ingestion probes.
