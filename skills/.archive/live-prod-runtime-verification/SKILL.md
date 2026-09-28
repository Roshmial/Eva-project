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
   - If the user has already declared a frontend host as the working/owned contour, do not default to saying that host is "unavailable" just because one tool path is limited. Start checks from that host, separate "shell reachable" from "post-login path verified", and only call out a limitation at the exact layer that is still unproven.
   - Important workflow correction: if the named frontend/server is the current managed host in this runtime, inspect it as a local contour first (local process, local listener, local curl, local logs) before treating it as an external SSH destination. Do not create fake uncertainty by re-classifying an owned prod surface as a foreign host.

2. Separate three states explicitly:
   - code state: what is fixed in the working tree
   - runtime state: what the live service currently does
   - deployed state: whether the live runtime actually includes the code fix

   Delivery rule for named prod tasks:
   - If the user asked about a specific production host/contour, local code changes or local green tests do not count as completion.
   - Do not report "done", "под ключ", or equivalent until the change is actually present on the named target and verified there.
   - A valid prod closeout needs the real target path: deploy or apply the change on that host, restart/reload the owning service if required, and run at least one live round-trip on the target contour.
   - If credentials or provider access still block the last live check, report that exact blocker explicitly instead of framing the work as already complete.

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
- Contour-separation pitfall: do not assume `hermes-gateway.service` is only a Telegram adapter. On some live Hermes Web contours, backend / CopilotKit systemd units may still have `Requires=hermes-gateway.service`. In that case, disabling gateway to "turn off Telegram" also kills the web runtime. First inspect unit dependencies (`Requires=` / `After=`) and the active gateway platforms.
- If the architecture says `Telegram is a separate front contour`, prefer keeping gateway alive as runtime/scheduler/API infrastructure while disabling only the Telegram platform in config (for example `platforms.telegram.enabled: false`) and preserving `api_server`. Treat `stop gateway` as a last resort until those unit couplings are removed.

Post-upgrade rule for Hermes itself:
- After upgrading Hermes on a live contour, do not stop at `hermes --version` or `hermes doctor`.
- Verify that `config.yaml` was migrated as intended, that dependent services are still owned by the intended supervisor (`systemd --user` vs stray listener), and that at least one real user-path probe still works after restart.
- If health answers but the backend unit is failed with `Address already in use`, classify it as an orphan-process / supervisor-contour problem first, not as a healthy runtime.

## 2. Reproduce the failure in the right layer

When the user asks to inspect the latest live user interactions for errors or bad agent behaviour, do not begin with speculative browser clicking. First run a production interaction audit in this order:
- backend service journal for recent exceptions/timeouts
- recent `app.chat_tasks` to identify affected users/threads and repeated error classes
- recent `app.messages` joined to threads/users to inspect the exact user-visible assistant outputs and metadata
- only then narrow into browser/UI replay if a frontend-only question remains

This is the fastest way to distinguish:
- shell is up but post-login flows are broken
- runtime exception vs routing defect vs output-contract defect
- one affected user/thread vs systemic regression

When the user asks for an audit of a recent production day or a slice like 'за вчера' / 'за сегодня', explicitly:
- anchor the date window first from the live system clock;
- exclude any users or personas the user named out of scope;
- summarize activity by user before diving into errors, so you know whether the issue is isolated or broad;
- inspect `chat_tasks.last_error` / status rows and then the corresponding `messages` to see the exact user-visible text;
- verify claimed side effects separately in domain tables (`app.jobs`, exported files, created artifacts), because assistant text like 'создана задача' or 'файл готов' can be false-positive prose.

See `references/prod-interaction-audit-and-postgres-like-gotchas.md` and `references/prod-interaction-audit-false-success-patterns.md`.

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
- For chat rendering regressions, explicitly map every text source and every render branch before changing sanitizers. In Hermes-style chat UIs the user-visible text may come from different fields depending on message kind: `content`, `display_text`, `meta.display_text`, `meta.recurring_summary.summary`, `meta.recurring_summary.status_detail`, or a specialized file/result/dashboard card.
- Do not declare a rendering fix verified just because one field is clean in the DB or API. Verify the exact branch the frontend uses for that message class. A recurring/job card can ignore the normal bubble path entirely, while a normal assistant reply may still render through the standard markdown bubble.
- If backend payload already has a clean `display_text` but the UI still shows stale reasoning/planning text, inspect whether the frontend prefers an older nested field (for example `recurring_summary.summary/status_detail`) ahead of `display_text`. Fix the priority order in the renderer and, if possible, align the backend contract so nested summaries are normalized too.
- Distinguish a chat-bubble regression from a message viewer/export regression before patching. If the user screenshot shows a document-style page (for example a white standalone page with product header/timestamp rather than an in-chat bubble), inspect the message export/viewer path separately. A common split is: chat bubble already uses cleaned `display_text`, while HTML/markdown export still reads raw `message_row['content']` and renders plain text.
- In that viewer/export class of bug, add a canonical export body helper (for example `build_message_export_body(...)`) and expose a normalized field in the export payload (for example `display_content`) so downstream viewers/consumers do not fall back to raw `content`.

For language / wording regressions in admin chat, verify the persisted live outputs and the route-specific backend text before blaming the model globally.
- Pull the latest admin/user thread messages from the live app DB and inspect the exact assistant text that was actually delivered.
- Separate three sources of foreign-language leakage: general system prompt, route-specific prompt/template, and backend-generated reply/mock text.
- If the app stores structured route metadata (`message_kind`, `downstream`, dashboard/mock labels), use it to localize the defect to one contour instead of declaring that “the whole assistant switched languages”.
- In dashboard/research routes, inspect backend literals such as `reply_text`, blueprint goals, and mock payload copy: these can leak English product terms even when the top-level persona says “reply only in Russian”.

Deployment note:
- If the named frontend is a local user-systemd prod surface, rebuild the frontend bundle and restart the actual prod service before declaring the UI fixed.
- In this class of contour, the live service may be a local `systemctl --user` unit (for example a `hermes-web-frontend-8803.service`) even when the public host is remote-facing.
- Apply the same check to backend services: verify whether the running prod unit is a system unit or a user unit before attempting restart, or you can waste time on the wrong `systemctl` scope and falsely think prod was restarted.
- Distinguish a real post-login product failure from a stale acceptance script. If browser smoke fails after login on a selector like `input[type=file]`, placeholder text, send-button label, or admin-tab hook, first inspect the live DOM and classify whether the user flow is actually broken or the smoke script has drifted behind the UI contract.
- When the UI is still working manually, patch the smoke script immediately so acceptance stays aligned with the live product. Prefer resilient selectors tied to current user-visible controls (for example `Файлы`, `Сообщение`, `↑`, and admin tab button text) over historical implementation hooks that may disappear.
- For Hermes Web specifically, keep the acceptance script and verify runbook aligned with the real public contour, not old dev defaults. If prod currently runs as `95.182.85.233:8803 -> 178.104.207.89:8791`, update the smoke env defaults / documented overrides to that contour before calling the operational tail closed.

## 4. For document-ingestion failures

Always inspect both structure coverage and volume limits.

Related export/generation pitfall:
- If the bug is not about ingesting user uploads but about generating/exporting a user-facing `docx`/`pptx`, inspect the document builder separately from chat rendering.
- In Hermes-style backends the same export builder may serve both explicit message export and generated-file delivery. A fix in chat continuity or file routing is not enough if the builder still wraps the final content in technical metadata or flattens structure into plain text.
- For user-facing documents, prefer cleaned display content (for example `build_message_export_body(...)`) as the source of truth, not line-flattened export helpers that prepend `Чат: ...`, `Сообщение #...`, `Дата: ...`, ids, timestamps, or other service metadata.
- Preserve at least the baseline structure users expect to survive packaging: headings, paragraphs, bullets/numbered lists, and markdown-style tables.
- Add targeted regressions that assert both sides at once: (a) structural preservation is present, and (b) technical metadata is absent from the generated document.
- See `references/document-generation-structure-and-metadata.md`.

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
- For direct URL sources that are really dynamic directories/search pages (for example map/search portals like 2GIS), a complete request may still be best handled as a validated `collection_contract` rather than an immediate synchronous fetch. If live execution falls over on source materialization, do not force that into the generic error bucket; first verify whether the safer prod behavior should be "contract accepted, execution deferred/handled elsewhere".
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

### Split auth-store / backend-owner verification for public frontends

When a public frontend host answers successfully but login or exported-state checks disagree with your local/backend probes, do not keep patching the local contour blindly.

Verification pattern:
- inspect the real frontend owner service/unit and confirm the proxy target (`HERMES_WEB_FRONTEND_BACKEND_BASE`, launcher script, or equivalent);
- compare the same auth request against both paths: direct backend (`backend_host:port/api/...`) and public frontend proxy (`frontend_host/api/...`);
- if direct backend and public proxy disagree, classify it as a contour split first, not as a product bug in auth/export;
- on the real backend-owner, read the running process env (`/proc/<pid>/environ`) to confirm DSN/runtime storage before editing users or test data;
- if you need a deterministic smoke user, create or reset it on the actual backend-owner datastore, then re-check both direct backend login and public proxy login before running browser acceptance.

Operational lesson:
- a localhost DuckDB/SQLite fix or password reset proves nothing for a public frontend if that frontend actually proxies to a remote Postgres-backed backend;
- first identify the backend-owner, then seed or repair auth there, then run the real public user-path.

### Split-prod rollout discipline when frontend and backend can drift independently

In split-prod contours, do not assume that a new public frontend bundle means the backend contract is also live, and do not assume that copying only `app.py` is enough for backend rollout.

Verification rule:
- inspect the public frontend bundle or DOM for the expected markers/behaviour;
- inspect the backend code on the real runtime host for the corresponding markers/branches;
- treat frontend-host proof and backend-host proof as separate checkpoints.

Rollout rule:
- deploy the backend as a package, not as a single-file hunch;
- include required policy/support files that the new code now imports or expects at startup;
- if the backend starts failing only after restart, inspect service logs immediately for missing policy/spec/reference files before blaming the main code change.

A common failure pattern is:
- frontend already serves new Sprint markers;
- backend host still runs old contract code;
- after partial rollout, backend crashes because a new JSON policy file was not deployed with the main Python file.

Classify this as a rollout completeness problem, not as evidence that the product change itself was invalid.

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
- On Postgres/psycopg-backed runtimes, embedding raw `LIKE '%...%'` JSON-string patterns directly in translated SQL can break placeholder parsing and turn `/api/threads`-style reads into live `500` errors. Prefer SQL parameters, escaped `%%`, or structured JSON access instead of raw percent-pattern literals.
- Looking only at parser logic and forgetting extraction truncation limits.
- Assuming “history is stored in DB” is enough for chat continuity under model resets.
- Treating bad LLM output as a prompting issue instead of adding a publication guard.
- Reporting prod as fixed when only the working tree and tests are fixed.
- Assuming the live backend uses the repo-default storage backend. Before trusting SQLite/DuckDB files, verify the actual runtime DSN/env on the live service; prod may be pointed at Postgres via `~/.hermes/.env`, a wrapper script, or systemd env even when local project files suggest file-backed storage.
- Letting a broken auth/session path block runtime verification. If HTTP auth is itself suspect, validate chat/job behavior directly through the live backend runtime (`enqueue_chat_task`, `process_chat_task`, DB rows, message meta) so you can separate product-logic regressions from API-auth regressions.
- Running prod verification with ambient `python3` instead of the same `.venv`/interpreter the live service uses. Dependency mismatches can create fake verification failures; use the service runtime when running targeted tests on prod.
- Treating stale smoke probes or obsolete demo credentials as proof that auth is broken. First verify whether the acceptance script still matches the current `/api/auth/login` flow and the real live smoke user.
- Resetting a smoke-user password or inspecting sessions off-process without sourcing the same runtime env as the backend. This can update the wrong DB and create false `401` conclusions.
- Declaring gateway post-upgrade acceptance green while logs still say that no user allowlist is configured. A running gateway with denied users is not a completed rollout.

# Output contract for the user

When you finish, give a short operational summary:
- what is confirmed live
- what is fixed in code
- what still requires rollout/deploy/restart
- what dependencies are still needed for full capability

# References

- See `references/message-viewer-vs-chat-rendering-split.md` for the specific pattern where screenshots look like a chat-render bug but the real defect is in message export/viewer HTML/markdown paths that still use raw `content`.
- See `references/recurring-render-branch-vs-display-text.md` for the specific split-render pattern where `display_text` is already clean but a recurring/job card still leaks stale reasoning from nested `recurring_summary` fields.
- See `references/live-ui-acceptance-pending-task-instability.md` for the specific acceptance pattern where UI scenarios appear healthy at the service level but still fail because fresh `chat_tasks` stay pending or require manual backend rescue.
- See `references/prod-token-accounting-false-freshness.md` for the specific false-positive pattern where importing `app.py` on prod starts an ad-hoc worker and makes a non-restarted service look fresh.
- See `references/prod-routing-policy-rollout-pitfalls.md` for rollout-specific pitfalls around missing policy directories, user-systemd detection, runtime-env mismatches, and distinguishing routing failures from source-stage failures.
- See `references/runtime-verification-checklist.md` for a concise checklist covering routing, admin runtime, document ingestion, session continuity, and LLM post-guards.
- See `references/prod-contour-rollout-pitfalls.md` for concrete runtime lessons about bind-host regressions after restart, local user-systemd frontend surfaces, chained admin-screen handler failures, and live marker-file ingestion probes.
- See `references/data-collection-contract-routing.md` for the verification pattern when `собери данные ... в csv/xlsx/json/xml` must become a backend collection contract instead of generic chat text or fake file output.
- See `references/curated-github-backup-live-runtime.md` for the pattern of building a curated GitHub backup from the real live contour, including systemd units, launcher scripts, deploy files, safe exclusions, and weekly refresh scheduling.
- See `references/full-preupdate-github-backup-with-secrets.md` for the complementary pattern when a Hermes/runtime upgrade requires a full live snapshot with auth/session/config state preserved, but GitHub must receive only an encrypted export rather than raw secrets.
- See `references/post-upgrade-hermes-runtime-hardening.md` for the specific post-upgrade pattern: config migration checks, orphan-process cleanup, runtime-env-matched smoke auth, and allowlist verification after restarting gateway/backend services.
- See `references/split-prod-rollout-marker-and-policy-checks.md` for the split-prod pattern: verify frontend bundle and backend host separately, and roll out required policy/support files together with backend code.
- See `references/public-frontend-backend-owner-auth-split.md` for the specific auth/state mismatch pattern where a public frontend proxies to a different backend-owner than the local contour you are probing.
- See `references/live-acceptance-smoke-drift-vs-product-break.md` for the specific pattern where post-login browser smoke fails because selectors drifted behind the live UI contract (`Файлы`, `Сообщение`, `↑`, text-based admin tabs) even though the real user flow is still healthy.
