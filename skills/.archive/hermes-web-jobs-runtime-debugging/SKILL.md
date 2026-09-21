---
name: hermes-web-jobs-runtime-debugging
description: Diagnose and fix Hermes Web job-screen mismatches between live UI, backend API, and Hermes Cron source-of-truth semantics.
---

# When to use

Use this skill when working on Hermes Web job management and any of these symptoms appear:
- the Jobs UI shows controls that do not match what the backend really supports;
- rename/display name changes seem to save in one place but not another;
- recipients/assignees look editable in UI but runtime delivery still follows a different path;
- a job comes from `source_of_truth = hermes_cron` and behaves differently from normal web-managed jobs;
- you need to verify a live prod contour, not just read code.

# Goal

Localize whether the mismatch lives in:
1. frontend state/UI affordance,
2. backend API contract,
3. Hermes Cron bridge translation layer,
4. deployment/runtime drift between local code and live prod.

# Core model

Hermes Web can expose at least two different job families:
- `local_jobs`: native web-managed jobs with web-side access/recipient semantics;
- `hermes_cron`: jobs mirrored from Hermes cron, where the real delivery source of truth is `deliver` / delivery target semantics.

Do not assume the same UI controls apply to both families.

# Working procedure

1. Reproduce in live UI first.
- Open the actual prod or target runtime.
- Check whether the screen offers actions that the backend may not support for this job type.
- Record the exact job `id`, `source_of_truth`, visible buttons, and current labels.

2. Check the frontend affordance layer.
- Inspect `JobsScreen`, job detail cards, modals, and handlers around:
  - `display_name`
  - `name`
  - `recipients`
  - `access`
  - `source_of_truth`
  - `read_only`
- Verify whether edit buttons are gated by generic edit rights only, or also by job family.

3. Check the backend API contract before changing UI text.
- Inspect `PATCH /api/jobs/<job_id>` handling.
- Confirm whether Hermes Cron jobs are translated through a bridge layer rather than the normal jobs table path.
- For `hermes_cron`, verify what fields are actually writable:
  - `name`
  - `schedule`
  - `prompt`
  - `deliver`
  - pause/resume fields
- Treat `display_name` and `recipients` as compatibility inputs only if backend explicitly maps them.

4. Inspect the Hermes Cron bridge translation.
- Read the code that converts cron jobs into web jobs.
- Confirm what the web layer exposes as:
  - `source_of_truth`
  - `read_only`
  - `recipients`
  - `display_name` vs `name`
- If the bridge renders recipients as delivery targets, the UI must not pretend they are normal fixed users unless backend truly supports that conversion.

5. Fix backend/API semantics first when the UI is sending a near-valid business intent.
- If UI sends `display_name` for a Hermes Cron job, map it to `name` in backend if that is the real writable field.
- If UI sends `recipients`, either:
  - translate only the subset that has a real bridge equivalent, or
  - reject unsupported recipient types with an explicit API error code.
- Prefer an explicit error over silent no-op behavior.

6. Then align UI affordances.
- Hide or disable editing controls that are not supported for the current `source_of_truth`.
- Replace generic helper text with job-family-specific wording.
- Show the real semantic object, for example delivery target instead of pretending it is a normal assigned user.

7. Verify in the live contour.
- Recheck backend health.
- Verify API round-trip for the exact prod job.
- Then verify the browser/UI state after deployment.
- Do not stop at local code correctness if the user asked for prod verification.

# Specific durable lessons

## Hermes Cron recipients are not the same thing as web recipients

For Hermes Cron jobs, the effective delivery model may be `deliver` / delivery targets rather than native web `fixed_user` / `fixed_thread` recipients.

Implications:
- if the bridge exposes recipients derived from delivery targets, label them honestly in UI;
- do not expose “add recipient user” affordances unless backend really maps them into valid cron delivery targets;
- if unsupported, return a dedicated API error and humanize it in frontend.

## Rename can require compatibility mapping

For Hermes Cron jobs, a UI field labeled as public title or display name may need backend mapping:
- `display_name` from UI
- `name` in Hermes Cron update path

If rename appears broken only for Hermes Cron, inspect that mapping before blaming browser state.

# Pitfalls

- Do not assume a control should be visible just because the current user is admin/owner.
  Also gate by `source_of_truth` and actual runtime support.
- Do not model Hermes Cron jobs as if they were regular local jobs.
- Do not rely on code inspection alone when the user asked for live prod confirmation.
- Do not silently drop unsupported recipient mutations; explicit API errors are easier to debug and safer for admin UX.
- When deploying a backend-only fix, remember the live UI may still be misleading until frontend affordances are updated too.

# Verification checklist

- Confirm the job detail payload includes the expected `source_of_truth`.
- Confirm rename round-trip on the target job id.
- Confirm unsupported recipient edits fail explicitly if not implemented.
- Confirm the UI no longer offers invalid recipient actions for Hermes Cron jobs.
- Confirm labels/help text match the real delivery semantics.
- Confirm the live prod contour, not just local files.

# References

- See `references/hermes-cron-job-ui-contract.md` for a condensed note on the `hermes_cron` vs web-job mismatch pattern and what to verify.