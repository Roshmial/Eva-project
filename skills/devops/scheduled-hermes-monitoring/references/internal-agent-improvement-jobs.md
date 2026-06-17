# Internal agent-improvement cron jobs

Session pattern captured from the June 2026 Hermes 178 work.

Use this when the user asks for jobs that make the agent itself smarter or more useful, rather than sending a briefing to the user.

## Durable rules

- Delivery default flips compared with user-facing briefings:
  - user-facing monitoring/digests usually need visible delivery during test windows;
  - internal self-review/self-learning jobs should default to `deliver=local` unless the user explicitly wants the reports surfaced in chat.

- Validate attached skills on the target host/profile before trusting the job definition.
  - A cron job can be created successfully even when a referenced local skill is missing on that machine/profile.
  - At runtime Hermes injects a warning and skips the missing skill.
  - This means “job created” is not enough verification for internal improvement loops that rely on a specific local skill.

- Manual trigger is only the first checkpoint.
  - After `hermes cron run <job_id>`, inspect persisted job state and the latest cron output artifact.
  - A run can be queued successfully and still fail later on the scheduler tick.

- Prompt guardrail for this class of jobs:
  - explicitly say the job is for improving the agent, not advising the user;
  - prefer updating an existing skill over generating a noisy report;
  - avoid writing user memory unless the finding is clearly about the user rather than the workflow.

- If the user expects "429 -> switch to the next model", verify the fallback layer explicitly instead of assuming it is already active.
  - Check the target profile config for `fallback_providers` or legacy `fallback_model`.
  - If the chain is empty, job-level retries will have nowhere to go even if Hermes core supports fallback.
  - Restore the agreed chain in profile config before blaming the individual cron job.

- Distinguish model-chain fallback from provider-level survivability.
  - A free-first chain inside one provider is still useful and should be restored when missing.
  - But if the host has only one credential on one provider, repeated provider-level `429` remains a systemic risk even after model-chain fallback is configured.
  - Do not overclaim that the job is resilient unless there is either another usable provider in `fallback_providers` or multiple rotating credentials in the pool.

- For internal self-learning/self-development jobs, reasoning-first model override is a valid default when the user asks for deeper analysis.
  - Set the job's `provider` and `model` explicitly instead of relying on the lightweight global default route.
  - Keep delivery local unless the user explicitly wants the reports surfaced.

## Good verification shape

1. Confirm the job exists with the intended schedule, delivery, skills, and workdir.
2. Trigger one run.
3. Re-check `last_status`, `last_error`, `last_run_at`, and `next_run_at` from persisted cron state.
4. Read the latest cron output file for the real result, including skipped-skill warnings.
5. Only then say the internal improvement loop is actually running.
