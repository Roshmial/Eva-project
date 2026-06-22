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

For language / wording regressions in admin chat, verify the persisted live outputs and the route-specific backend text before blaming the model globally.
- Pull the latest admin/user thread messages from the live app DB and inspect the exact assistant text that was actually delivered.
- Separate three sources of foreign-language leakage: general system prompt, route-specific prompt/template, and backend-generated reply/mock text.
- If the app stores structured route metadata (`message_kind`, `downstream`, dashboard/mock labels), use it to localize the defect to one contour instead of declaring that “the whole assistant switched languages”.
- In dashboard/research routes, inspect backend literals such as `reply_text`, blueprint goals, and mock payload copy: these can leak English product terms even when the top-level persona says “reply only in Russian”.

Deployment note:
- If the named frontend is a local user-systemd prod surface, rebuild the frontend bundle and restart the actual prod service before declaring the UI fixed.
- In this class of contour, the live service may be a local `systemctl --user` unit (for example a `hermes-web-frontend-8803.service`) even when the public host is remote-facing.
- Apply the same check to backend services: verify whether the running prod unit is a system unit or a user unit before attempting restart, or you can waste time on the wrong `systemctl` scope and falsely think prod was restarted.

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

## 8. For chat-action / artifact failures disguised as success

When the user says "ничего не сделано", "задача не появилась", or "файл не сгенерился", do not stop at `chat_tasks.status='completed'`.

### Important split: routing success vs source-stage failure

For collection-style requests, explicitly separate:
- routing worked and the request entered the correct collection path;
- execution worked end-to-end;
- source-stage actually produced candidates/documents.

### Important split: imported probe vs running prod service

When verifying a Python backend on prod, do not assume that importing the backend module is a read-only inspection.
In Hermes-style backends, importing `app.py` can execute module-level startup such as `recover_interrupted_chat_tasks()` and `start_chat_processor()`. That can spawn an ad-hoc background worker inside the probe process and let it process pending chat tasks with newer code than the still-running public service.

This creates a dangerous false positive:
- direct module import / DB probe shows the new behavior;
- but the real public user path is still served by the old in-memory process and does not show it.

Verification rule:
- treat the public user path as the source of truth;
- if you need DB inspection, run it in a process with chat-processor startup disabled (for example with `HERMES_WEB_CHAT_PROCESSOR_ENABLED=0`, or another equally direct guard);
- if code on disk is new but the public path is old, classify it as a rollout gap and restart the live service before calling the fix verified.

This matters for generic web requests without explicit URLs.
If the live result is something like `web_collection_sources_not_found`, do **not** immediately classify it as a routing regression if:
- the contract was built correctly;
- the collection route was selected;
- the failure happened only when materializing search candidates.

In that case, classify it as a `search-stage / provider-availability / source-discovery` blocker, not as a chat-routing bug.

For requests of the form `собери данные из источника X по формату Y`, verify that the backend has a dedicated collection-contract route before the generic chat/export path.
- The runtime should first extract and validate a collection contract: `source_kind/source_label`, `subject`, `output_format`, and for structured outputs (`csv/xlsx/json/xml`) the required `fields`.
- If the request is incomplete, the correct prod behavior is `clarification_request`, not free-form assistant prose and not a fake `file_response`.
- If the request is complete, the correct prod behavior is a route-specific artifact such as `collection_contract` (or the app's equivalent structured contract), with execution steps stored in metadata for the downstream worker/runtime.
- If a request like `собери ... в csv` goes straight to file generation from normal assistant text, classify it as a routing bug, not a file-format bug.

Verify four layers separately:
- the user request in `app.messages`
- the request-processing row in `app.chat_tasks`
- the intended side effect (`app.jobs`, created task/thread, exported artifact)
- the user-visible delivery/rendering path

Diagnostic pattern:
- If the thread contains only normal assistant prose and there is no `job_created` / no new row in `app.jobs`, the system handled the request as chat text, not as an action.
- If `message_kind='file_response'`, inspect whether it is a real task artifact or only a generic export of the assistant message.
- Do not treat a physical file under `data/message_exports/` as proof that the requested deliverable exists. Open the file and verify that its contents match the requested dataset/document, not just a transcript wrapped in CSV/TXT/DOCX.
- Check whether the attachment exists only inside `messages.meta_json.attachments` or also has a corresponding durable record/render path in the app's normal file tables and UI path. A backend may claim success while the frontend still cannot surface the file properly.

Language-drift rule for these failures:
- inspect the persisted thread messages themselves, not only persona/profile memory.
- foreign-language leakage can be visible first in live assistant history even when user language and personalization remain Russian.
- if the same failure thread contains Portuguese/English assistant turns plus fake-success file output, classify it as a chat orchestration / publication failure, not merely a wording issue.

## 9. Verify with narrow tests

## 9A. User-path acceptance must be judged before any manual backend rescue

When the user explicitly asks to verify scenarios **through the user interface**, the acceptance verdict must reflect the raw user path first.

Verification rule:
- run the scenario from the real UI surface;
- observe whether the assistant message completes on its own;
- only after that may you inspect DB rows, task state, logs, or manually trigger processing for diagnosis.

Do **not** count a scenario as fully passing if it required any of the following to finish:
- manual `process_pending_chat_tasks_once(...)`
- direct DB manipulation
- ad-hoc worker import / off-process execution
- service restart mid-scenario
- switching from UI-path to backend-only execution to obtain the result

Classification rule:
- if the UI request completes end-to-end without intervention, mark it **pass**;
- if the result exists only after manual backend rescue, mark it **unstable / partial pass**;
- if the route returns `clarification_request`, runtime error, timeout, or generic fallback where the expected execution path was more specific, mark it as **not passing as requested** even if a human could reformulate it.

Important pitfall:
- green `/api/health` and even `chat_processor.running > 0` do **not** prove that fresh user chat tasks are being consumed reliably;
- always inspect whether new `chat_tasks` move from `pending` to `started/completed` on their own during acceptance.

## 9B. Dashboard and collection requests need separate acceptance criteria

For mixed prompts like `собери данные ... и построй дашборд`, do not collapse everything into a generic "assistant answered" verdict.
Check separately:
- did the request enter the collection path or generic chat path;
- did source acquisition succeed;
- did dashboard generation succeed;
- did the final UI render a dashboard-like result rather than a plain fallback/error reply.

If the runtime returns a processing error (for example a Python exception surfaced as a failed processing status), classify it as a real dashboard/runtime defect even when collection-style requests succeed elsewhere.

After code changes, add targeted tests for the new risk area instead of relying only on broad smoke tests.
Examples:
- session TTL default and expiry behavior
- DOCX table/header extraction
- XLSX/PPTX extraction paths
- long-chat compaction path
- malformed LLM-output rejection

### Prod-test discipline when the live service env differs from your shell

On live Hermes-style backends, do not assume an off-process Python import sees the same env/DB/session secret as the running service.
Before trusting direct runtime probes (issuing sessions, reading DB state, calling helper functions), confirm whether the service is launched through a wrapper such as `run_backend_service.sh` + `scripts/runtime_env.sh`.

If the service has a runtime wrapper:
- source the same runtime env before running probes;
- use the same `.venv` as the service;
- verify the live DSN/env from the running process when auth/session results look inconsistent.

A classic symptom is: session issuance appears to work off-process, but the resulting token gets `401` from the live API. Treat that as an env-contour mismatch until proven otherwise.

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
- Assuming the live backend uses the repo-default storage backend. Before trusting SQLite/DuckDB files, verify the actual runtime DSN/env on the live service; prod may be pointed at Postgres via `~/.hermes/.env`, a wrapper script, or systemd env even when local project files suggest file-backed storage.
- Letting a broken auth/session path block runtime verification. If HTTP auth is itself suspect, validate chat/job behavior directly through the live backend runtime (`enqueue_chat_task`, `process_chat_task`, DB rows, message meta) so you can separate product-logic regressions from API-auth regressions.
- Running prod verification with ambient `python3` instead of the same `.venv`/interpreter the live service uses. Dependency mismatches can create fake verification failures; use the service runtime when running targeted tests on prod.

# Output contract for the user

When you finish, give a short operational summary:
- what is confirmed live
- what is fixed in code
- what still requires rollout/deploy/restart
- what dependencies are still needed for full capability

# References

- See `references/live-ui-acceptance-pending-task-instability.md` for the specific acceptance pattern where UI scenarios appear healthy at the service level but still fail because fresh `chat_tasks` stay pending or require manual backend rescue.
- See `references/prod-token-accounting-false-freshness.md` for the specific false-positive pattern where importing `app.py` on prod starts an ad-hoc worker and makes a non-restarted service look fresh.
- See `references/prod-routing-policy-rollout-pitfalls.md` for rollout-specific pitfalls around missing policy directories, user-systemd detection, runtime-env mismatches, and distinguishing routing failures from source-stage failures.
- See `references/runtime-verification-checklist.md` for a concise checklist covering routing, admin runtime, document ingestion, session continuity, and LLM post-guards.
- See `references/prod-contour-rollout-pitfalls.md` for concrete runtime lessons about bind-host regressions after restart, local user-systemd frontend surfaces, chained admin-screen handler failures, and live marker-file ingestion probes.
- See `references/data-collection-contract-routing.md` for the verification pattern when `собери данные ... в csv/xlsx/json/xml` must become a backend collection contract instead of generic chat text or fake file output.
- See `references/curated-github-backup-live-runtime.md` for the pattern of building a curated GitHub backup from the real live contour, including systemd units, launcher scripts, deploy files, safe exclusions, and weekly refresh scheduling.
