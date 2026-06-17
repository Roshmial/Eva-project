# Dashboard policy + recurring jobs pattern

When delivering request-driven dashboards in a local-first web MVP, prefer this contour:

1. Request-level policy
- Reuse the existing message POST flow.
- Pass `request_execution_policy` through both JSON and multipart paths.
- Keep durable defaults in backend-managed `source_registry` and `processing_policy`.

2. Admin governance
- Split admin editing into two concerns:
  - `source_registry`: what sources exist, trust level, registration status, enabled flag.
  - `processing_policy`: default mode, override allowance, external action, source selection order.
- Use backend patch endpoints over the existing settings store; do not invent a parallel policy service.

3. Message history UX
- Show the effective policy and the resulting `dashboard_artifact` in message history.
- If the assistant message produced a dashboard artifact, that message is the right anchor for a recurring-action affordance.

4. Save successful dashboard as recurring work
- Do not invent a separate `dashboard_subscription` entity.
- Reuse the existing jobs/cron contour.
- Open a prefilled job draft from the assistant message carrying `dashboard_artifact`.
- Default to `local_jobs`; expose `hermes_cron` as an explicit contour choice.
- Build cron payload from existing job draft fields: `schedule_kind`, `time_of_day`, `days_of_week`, `deliver`.

5. Contract pitfall
- Do not guess backend mode keys from product wording.
- Read runtime `allowed_modes` first and bind UI/tests to those values.
- In this session the real backend values were:
  - `registered_only`
  - `registered_plus_external`
  - `external_allowed`
- A plausible invented key like `internal_preferred` must be treated as a wrong assumption and removed from UI/tests.

6. Verification pattern
- Build frontend: `npm run react:build`
- Syntax-check backend Python.
- Add or update smoke tests for:
  - admin source/policy save
  - jobs API flow for `source_of_truth = hermes_cron`
- If unittest import resolution depends on module location, prefer fixing the launch path (for example `PYTHONPATH=...`) and then running the real tests, rather than recording the transient import failure as a durable rule.
