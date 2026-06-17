---
name: turnkey-local-first-mvp-delivery
description: "Deliver local-first MVP development tasks end-to-end for Misha: data layer, admin surface, bootstrap state, reference data, verification, and supporting artifacts without artificial decomposition."
---

# When to use

Use for development tasks where Misha asks to do something "под ключ" for a local-first web/admin product, especially when the request involves backend + frontend + data layer together, bootstrap state, admin capabilities, or preparation of a clean reference image for future rollout.

Typical triggers:
- "сделай под ключ"
- "сделай сразу всё"
- requests around data contour, source-of-truth boundaries, analytical layer, bootstrap state, admin screens, directories, roles, restrictions, or reference data
- requests where PMBook-style artifacts are implicitly part of the deliverable even if not listed separately

# Core rules

1. Treat the work as one integrated delivery, not a fake sequence of disconnected mini-steps.
   - Do not answer with "давай сначала матрицу" or similar artificial decomposition when the agent can infer the architecture and artifacts itself.
   - Build the complete contour: backend storage, API contract, frontend usage, data-flow logic, analytical consequences, and required documentation/logging.

2. Infer missing but necessary steps proactively.
   - If the user omitted steps, check whether the task is logically complete.
   - Either perform the missing steps yourself or explicitly propose the minimum extra actions needed.
   - Do not wait for the user to enumerate obvious follow-up work such as schema changes, seed/bootstrap cleanup, verification, admin forms, decision-log updates, or docs sync.

3. Default to local-first architecture already in the workspace.
   - Reuse the current backend, current DB, Hermes runtime, local analytical layer, and existing frontend.
   - Prefer extending existing admin/bootstrap endpoints over introducing parallel APIs.
   - Keep operational source-of-truth in runtime systems; keep analytical DB analytical-only.

4. Minimize duplication in the data layer.
   - No shadow master tables for the same business entity unless strictly necessary.
   - Separate operational entities from analytical projections.
   - Use backend tables for reference data; do not hardcode reference dictionaries in frontend runtime.
   - Avoid multiple tables for the same meaning when one normalized structure is enough.

5. For major frontend rewrites or framework migrations, protect the working runtime with an isolated copy.
   - If the user asks to move a live local-first frontend to React or another major UI stack, do not start in-place on the currently working runtime by default.
   - Prefer a separate project copy plus its own dev/preview port, while keeping the same backend API contract unless backend migration is explicitly in scope.
   - Treat "login screen renders" as insufficient evidence of progress: the first acceptable milestone is a live shell with all main screens wired to real data.
   - Record the launch path, current parity boundary, and remaining legacy gaps in a dedicated status artifact and in decision-log.

6. For clean bootstrap / first-run states, explicitly reset the operational surface.
   - Leave only the minimum required bootstrap data, usually one admin account plus backend-managed reference data.
   - Remove old synthetic/demo artifacts from operational frontend/backend stores before calling the state "clean".
   - Keep external Hermes/Telegram/runtime data visible only through their intended contours, not as fake local demo content.

6. Admin requirements are first-class, not optional polish.
   - If the frontend uses reference data, provide backend tables + admin CRUD/UI for those references.
   - If users must be manageable, provide manual admin creation/editing of users, roles, and restrictions.
   - Do not leave governance-critical data editable only in code.

7. Frontend text must be Russian by default.
   - Remove English labels from user-facing UI unless the term is a real technical product/name that must stay English.
   - Audit new forms and admin screens for labels like key/sort/payload/create/edit and translate them to Russian equivalents.
   - Run a short copy pass over banners, empty states, placeholders, and feedback messages before calling the task done.
   - Prefer professional, neutral Russian over colloquial wording: for example, replace phrasing like `галочками`, `плашка`, or vague `пока не задан` states with clearer business-language text tied to the actual object and action.

8. Verification is part of the deliverable.
   - After code changes, run syntax checks and real runtime/API checks.
   - Verify not only read endpoints but also write paths relevant to the requested feature.
   - For admin/reference work, include history endpoints in the live check set, not just list/detail/create/update.
   - Add at least one regression check for the exact endpoint or flow that failed, so the same hole is covered in smoke tests next time.
   - If something is still failing, report it as incomplete rather than implying the feature is done.

9. Keep authenticated bootstrap resilient.
   - Do not gate the entire post-login UI on secondary panels such as admin dashboards, jobs sidebars, or other non-core sections.
   - Load the minimum data required to show the main shell first; then load secondary sections as deferred work.
   - Prefer `Promise.allSettled(...)` or equivalent for post-login secondary fetches, and surface a Russian partial-failure banner instead of leaving the whole shell hidden.
   - When admin-only data fails, the user should still reach chat/profile/core navigation unless auth itself is invalid.
   - Do not block shell reveal on restoring the last active chat/thread. If session restore has a valid token and core profile/bootstrap calls succeeded, show `appShell` first and reopen the last thread only as a best-effort step.
   - Wrap `loadThread(activeThreadId)` / similar post-login chat restoration in local `try/catch` with a fallback to an empty chat state or current screen, plus a Russian banner about the specific restore failure. A broken last-thread payload must not dump the user back onto the login screen or keep the shell hidden.

10. Separate product defects from local browser/runtime defects before fixing UI blindly.
   - If live UI verification behaves inconsistently, first prove or falsify backend/auth correctness with direct API probes before changing frontend logic.
   - In local-first localhost work, prefer stabilizing the existing Playwright/browser path in user space before proposing new infrastructure or external browser services.
   - When a browser/runtime workaround becomes necessary for acceptance (for example, env-wrapping fontconfig/fonts or similar local dependencies), turn it into a canonical project script instead of leaving the recipe buried in chat history.
   - If you created temporary probes under `tmp/` to diagnose the issue, promote the one proven end-to-end smoke into a permanent regression script under the project and document the official launch path.
   - After a bug fix, verify the repaired flow twice when relevant: once at direct API level, and once through the real browser/UI path.

11. Logging and version-awareness must be considered before closure.
   - Update decision-log for architectural changes.
   - For mutable admin data, check whether timestamps are enough or whether audit/version history is required by the task.
   - If audit/versioning is implemented in backend, expose it in the admin UI as visible version/history, not as hidden DB-only infrastructure.
   - Translate backend error codes into Russian user-facing messages on the frontend; do not leak raw API codes like `email_already_exists` into admin UI.
   - If versioning/audit is not yet implemented, call that out explicitly as remaining work.
   - When you had to stabilize a local browser/runtime path or build a new regression smoke, document the canonical commands in README as part of closure, not as an optional extra.

12. For multi-user hardening, close the write-path contract end-to-end.
   - Do not treat `version` as decorative metadata. If shared entities are editable from several tabs/users, backend write-paths must use compare-and-swap / optimistic locking and return a conflict signal on stale updates.
   - Propagate the same `version` through frontend draft/state and every relevant save path: profile, admin edits, entity rename/alias flows, status toggles, and full edit modals.
   - For materialized shared helper entities (for example, one job-thread per user+job), do not rely only on `SELECT` + `INSERT` discipline in Python. Add a DB-level uniqueness invariant where the product model expects uniqueness, and if legacy rows may already violate it, dedupe first and create the unique index only after cleanup.
   - When tightening a legacy local-first schema, remember migration safety: new `NOT NULL` fields added to operational entities must get explicit backfill/default handling for old SQLite/DuckDB rows, otherwise rollout may fail before the new logic is ever exercised.
   - Acceptance for this class of work is not just syntax + one happy-path save. Require: stale update regression coverage, live runtime confirmation that the shell still opens, and user-facing conflict messaging in Russian.

13. For source-trust / data-policy features, extend the existing operational contour instead of inventing a parallel policy service.
   - If the task is about trusted sources, external fallback, registry of sources, or per-request processing mode, use the current `app_settings` / bootstrap / admin / send-flow contour first.
   - Put durable defaults in backend-managed settings such as `source_registry` and `processing_policy`, not in frontend constants.
   - Expose those settings through the existing bootstrap payload so chat/profile/admin screens read the same source of truth.
   - Prefer adding admin endpoints that patch the same settings store over creating a separate policy subsystem or shadow database.
   - For request-level behavior, prefer extending the existing message POST flow with a full policy object such as `request_execution_policy`, not a parallel endpoint. If the frontend supports both JSON and multipart sends, pass the policy through both paths: native object for JSON and serialized JSON string for multipart/form-data.
   - Keep chat-level draft state and admin-level policy draft state separate, but re-sync both from backend truth after bootstrap load and after admin save so the composer reflects the newly saved defaults.
   - When the model must obey source-trust boundaries, inject a compact system-context block that states the active mode, allowed source classes, and the rule that internal registered sources come first in local-first mode.
   - In admin UI, separate two concepts clearly: source registry (what sources exist and how trusted they are) and processing policy (default mode and whether chat-level override is allowed).
   - In chat UI, surface only the minimal override selector plus a short Russian explanation of what the chosen mode means; keep the full governance editor in admin.
   - For dashboard/source clarifications, do not assume the user knows whether local data exists. The system should either help the user identify a plausible local source or say explicitly that local data is insufficient and an open-source/external search path is needed.
   - In clarification UX, do not inject concrete canned task prompts for the user (for example, session-specific market names or dataset examples) as if they were the right next action. Keep the choices generic at class level: clarify the local source/scope or switch to an external/open-source overview.
   - If a successful dashboard should become recurring work, reuse the existing jobs/cron contour instead of inventing a `dashboard_subscription` entity. Surface the action from the assistant message that already carries `dashboard_artifact`, prefill the job draft from that message, and keep `local_jobs` as the default contour with `hermes_cron` as an explicit admin/runtime choice.
   - For cron-backed recurring dashboards, derive the scheduler payload from the existing job draft fields (`schedule_kind`, `time_of_day`, `days_of_week`, delivery target) and let backend `source_of_truth` routing decide whether the request becomes a local job or a Hermes cron job.
   - Do not guess mode keys from UX wording. Read the actual backend/runtime `allowed_modes` dictionary first and wire the frontend to those real values; if a plausible label like `internal_preferred` is absent from runtime, treat it as a wrong assumption and correct the UI/tests to the backend contract.
   - Do not call this class of task done after UI patches alone: verify the exact save/load/send paths end-to-end — bootstrap carries `data_policy`, admin load/save returns the edited policy, chat send includes `request_execution_policy`, the resulting message metadata/artifact is visible in history, and save-as-job / cron creation works against the real jobs API.

# Delivery checklist

1. Clarify source-of-truth boundaries.
2. Implement schema/storage changes in existing local backend.
3. Remove frontend hardcode for runtime dictionaries/reference data.
4. Add/administer CRUD paths for references and manual users.
5. Align bootstrap state to a clean first-run image.
6. Ensure frontend strings are Russian.
7. Run syntax checks.
8. Run live API/runtime verification.
9. Check actual DB state after writes.
10. Update decision-log/docs if architecture changed.
11. In the final report, separate:
   - what is confirmed working,
   - what is partially implemented,
   - what remains to verify.

# Pitfalls

- Declaring success after schema patches without live endpoint checks.
- Leaving reference data as frontend constants while only partially mirroring them in backend.
- Forgetting that DuckDB is stricter than SQLite on GROUP BY and aggregate queries.
- Calling a state "clean bootstrap" while old demo rows still exist in operational tables.
- Mixing Hermes analytical projections with local operational entities and calling them the same thing.
- Leaving English admin labels in a Russian UI.
- Treating a flaky localhost browser/runtime symptom as proof of a product bug before checking backend/auth with direct probes.
- In temporary external authorization flows, leaving the page generically labeled (`Авторизация`) so the user cannot tell whether they are logging into the product itself or authorizing downstream API access. Label the target system explicitly and state what server-side session/artifact is being created.
- In temporary external authorization flows, always showing a 2FA/password form instead of only surfacing it when the upstream API explicitly requires it.
- In temporary external authorization flows, leaving the input form visible after successful completion. Replace it with a terminal success state and make already-used links single-use for re-entry.
- Finishing a debugging session with only ad-hoc `tmp/` probes and no promoted canonical regression script for the flow that just failed.

# Notes

Session-specific notes and examples can be stored under `references/` when a particular delivery produces reusable API/data-shape lessons.
- See `references/admin-reference-users-audit-versioning.md` for concrete notes on delivering admin CRUD with visible audit/version UI, Russian error mapping, and DuckDB migration/query pitfalls.
- See `references/local-browser-runtime-and-ui-regression-smoke.md` for a compact pattern on stabilizing localhost browser verification, separating runtime issues from product issues, and promoting temporary Playwright probes into canonical regression scripts.
- See `references/multi-user-hardening-version-contract.md` for a compact acceptance and implementation pattern for optimistic locking, shared helper-entity uniqueness, and migration-safe local-first schema tightening.
- See `references/react-isolated-migration-baseline.md` for a repeatable pattern on starting a safe React migration in an isolated copy, proving real screen-level progress against the existing backend, and documenting the parity boundary honestly.
- See `references/source-registry-processing-policy-pattern.md` for a compact pattern on implementing source registry, processing policy, and request-level chat override inside the existing local-first settings/bootstrap/admin/send-flow contour.
- See `references/request-execution-policy-react-wiring.md` for a concrete React wiring pattern: separate chat/admin drafts, sync both from backend truth, and pass `request_execution_policy` through both JSON and multipart message flows.
- See `references/dashboard-policy-and-recurring-jobs.md` for the recurring-dashboard pattern: anchor save-as-job on the assistant message artifact, reuse jobs/cron instead of a new entity, and verify against the real backend mode dictionary.
- See `references/temporary-external-auth-flow.md` for a compact pattern on exposing a one-time external authorization page for downstream API access, including explicit user-facing labeling, conditional 2FA step handling, single-use links, and post-success UI state.
