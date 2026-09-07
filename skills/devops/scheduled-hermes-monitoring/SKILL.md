---
name: scheduled-hermes-monitoring
description: "Build recurring monitoring pipelines that run inside Hermes: start/check source systems, collect data, have the agent summarize, deliver results, and schedule via Hermes cron."
version: 1
created_by: agent
---

# Scheduled Hermes Monitoring

## When to use

Use this skill when the user asks to set up recurring monitoring, digesting, alerting, or daily/weekly summaries where Hermes must participate in the workflow.

Typical examples:
- daily Telegram/channel/news monitoring;
- recurring market or competitor digests;
- internal API polling followed by agent analysis;
- scheduled summaries delivered back to Telegram or another connected channel;
- internal agent-improvement jobs that inspect past sessions, refine skills, or improve Hermes behavior without messaging the user.

## Core principle

Do not hand the user a script plus manual instructions when the requirement is an Hermes-managed process.

The expected shape is:
1. Hermes starts or verifies the data source/API.
2. Hermes collects data or runs a collection script.
3. Hermes, not an external LLM API, performs the interpretation/summarization unless the user explicitly selects another model/provider.
4. Hermes delivers the final result to the requested channel.
5. Hermes cron owns the schedule.

## Required workflow

1. Clarify the first checkpoint only if needed.
   - If the user asked for step-by-step execution, do not design the whole system in one big leap.
   - Make one step, test it, report the factual result, then wait for approval or changes.

2. Inspect before changing.
   - Find the project/workdir and existing configs.
   - Read relevant scripts/config/state files before editing.
   - Check whether the source API/session/credentials are actually usable before building later stages.

3. Separate durable pipeline responsibilities.
   - Source/API runner: starts or verifies the local service.
   - Collector: gets new data and updates state/checkpoints.
   - Agent prompt: summarizes and filters what matters.
   - Scheduler: Hermes cron job with self-contained prompt and optional script.
   - Delivery: origin/current Telegram chat unless the user asks for another target.

4. Test each boundary.
   - API health or sample request.
   - Incremental collection behavior.
   - Agent summary quality on a saved sample.
   - Cron dry run via cronjob action='run' before relying on the schedule.
   - Do not assume that a “test period” means local-only delivery. For Misha, a test period still means delivery to Telegram unless he explicitly asks for local-only behavior.
   - For user-facing recurring briefs, verify the delivery semantics explicitly before leaving `deliver=local`; if the user expects live observation, use Telegram delivery during the test window.
   - For internal agent-improvement jobs, invert that default: prefer `deliver=local` unless the user explicitly wants the self-review reports surfaced in chat.
   - Before attaching non-bundled skills to a cron job on another Hermes host/profile, verify that those skills are actually installed there. Missing local skills are skipped at runtime, which can silently weaken the job if you only checked the create command.
   - If you manually trigger a Hermes cron job from the CLI, verify execution from the persisted job state and cron output artifacts, not only from the immediate “Triggered job” message. A queued run can still fail later on the scheduler tick.
   - If the workflow writes into a shared local database or hub, verify freshness end-to-end instead of checking only that the app can write. Compare source-of-truth counts/timestamps with the hub and confirm that the refresh path itself is scheduled.
   - When the same DuckDB file contains both live app tables and batch-refreshed analytical tables, treat them as separate update paths. A successful live write into one schema does not prove that the other schema is being refreshed on schedule.

5. Only then schedule.
   - Use the cronjob tool for recurring execution.
   - The cron prompt must be self-contained because cron runs in a fresh session.
   - Include exact workdir, source paths, expected output, filtering criteria, and delivery behavior.
   - For `no_agent=true` script jobs, remember that Hermes cron does not accept an arbitrary absolute script path at create time: the script must live under `~/.hermes/scripts/` and the cron config should reference only the filename or relative path there.
   - If the real source file belongs in a project workdir, keep a project copy for normal editing/testing and a cron copy under `~/.hermes/scripts/`; verify the cron copy, not just the workspace copy.
   - If one part of the message is optional but expensive or failure-prone to gather, split it into a helper job and feed the result into the main brief via `context_from`.
   - For internal self-improvement jobs, state the guardrails explicitly in the prompt: this is for improving the agent, not for advising the user; prefer skill updates over noisy reports; avoid changing user memory unless the signal is truly about the user.
   - If the user expects internal jobs to be more analytical, prefer an explicit reasoning-model override on those jobs instead of assuming the profile's default route is enough.
   - If the user expects `429` recovery, verify the target profile's `fallback_providers` chain and credential situation before concluding the job itself is broken.
   - When the user asks “where is this cron actually running?”, answer it from Hermes job ownership, not from the application being monitored: inspect the Hermes cron job's `workdir`, `deliver`, and `~/.hermes/cron/output/<job_id>/` artifacts first. A Telegram/API/backend project may be remote or split-host, while the cron job itself is still running locally inside the current Hermes profile.
  - If the user explicitly says there is a separate remote/isolated Hermes cron on another host, verify that remote Hermes home directly before concluding the job is local. Check the remote `~/.hermes/cron/jobs.json`, `~/.hermes/cron/output/<job_id>/`, the target workdir, and the service/API the job talks to. Do not override an explicit topology correction with a local-only assumption.
  - Distinguish “job ran” from “pipeline healthy”. If collector output says `no_new_messages`, read the underlying report and collector stdout/stderr to ensure an API `500` or other fetch failure was not silently converted into a green-looking status.
  - For an event-only runtime audit log, a stale file timestamp is not itself a failure: it may simply mean there were no errors. Run the audit in the real backend contour and pair the quiet-log interpretation with a live health probe. If the scheduler is local but the backend is remote, use a thin local wrapper that invokes the exact remote virtualenv/script; do not audit a stale local mirror.
  - For an expensive agent triage that only matters when an audit has signals, attach a deterministic monitor script. Its output must be stable (`no-signals` or a normalized signal digest) so unchanged healthy state suppresses the LLM run; preserve the first-tick baseline behavior.

## User preference: stepwise execution

For Misha, treat automation setup as an operator workflow, not a tutorial. He expects the agent to execute with Hermes tools.

Preferred cadence:
- do the first concrete step;
- test it;
- report the result briefly;
- ask for approval or adjustment before moving to the next step.

For recurring user-facing jobs in this environment:
- default to clean final output with no technical markup, no transport syntax, no “possible improvements”, and no self-review block unless the user explicitly asks for analysis;
- if the job is meant to send a Telegram image post, prefer the user-facing payload shape the user approved, not a tool-oriented representation.

Avoid:
- telling him to configure cron manually;
- using external LLM APIs when Hermes can summarize;
- ending with “you can now run…” if Hermes can run it;
- moving to scheduling before the data source has been proven to work.

## Pitfalls

- For Misha's user-facing recurring briefs, do not assume that a complaint about a "missing section" is a delivery bug. First inspect the final cron output artifact itself and compare it with collector/payload inputs. If the missing block is already absent in the saved cron markdown, the fault domain is the prompt/output contract, not Telegram delivery.
- In split contours, do not mix hosts when diagnosing recurring jobs. If the frontend/UI runs on the local server but the backend/API is remote, verify each layer in its real contour and state explicitly which side is confirmed. Do not report "frontend/backend updated" as one combined fact unless both contours were actually checked.
- When designing Telegram digests for Misha, avoid over-pruning the operator transparency layer. A clean client digest is good, but removing all technical summary can make the monitor operationally opaque. Prefer a compact factual footer when needed: found total messages, non-empty count, skipped empty/media-only count, requires-review count, collector/API status, and whether state/since advanced.
- Do not outsource summarization to OpenAI or another external API unless explicitly requested. Use the current Hermes agent/model for the analysis step.
- Do not create a manual OS cron/Task Scheduler instruction when Hermes cron is available.
- Do not claim the pipeline works until the data source/API returns real data or a clear authorization/configuration blocker is proven.
- Do not treat “there is a refresh script” or “the app wrote one new row” as proof that the reporting hub is current. Verify that the scheduled refresh job exists and that the destination counts/timestamps have caught up with the source system.
- If authentication is blocked by a human-required code/2FA, stop at that boundary and report it as a blocker rather than fabricating downstream success.
- For `no_agent=true` cron scripts, do not assume the scheduler can execute the script from an arbitrary project path. Hermes cron expects scripts under `~/.hermes/scripts/`; if creation fails on an absolute path, fix it by copying/writing the script there and then recreate the job.
- Do not treat `cronjob action='run'` returning success as the final proof for script jobs; confirm the persisted output under `~/.hermes/cron/output/<job_id>/` and inspect the rendered report text.
- Do not update incremental state before deciding whether the current batch was successfully processed, unless the user has accepted “collect even if summarize fails” semantics.
- In user-facing recurring jobs, do not leak raw MEDIA syntax, markdown image placeholders, send_message traces, tool logs, or “skill created” style service chatter into the delivered message.
- If a Telegram post is supposed to be two messages, encode that explicitly in the workflow: image first, caption second; do not collapse it into one captioned media message unless the user asked for that format.
- For internal agent-improvement jobs, do not default to user-facing delivery, and do not assume that the job is healthy just because creation succeeded; verify that the attached skills resolved and that at least one real run completed.
- Do not equate a configured model chain with full `429` resilience. If the host has only one provider credential, provider-level rate limits can still block the whole job even after fallback models are configured.

## Verification checklist

Before calling the setup complete, confirm:
- source API starts or is already running;
- source credentials/session are valid, or the blocker is explicitly reported;
- collector produces a file or structured payload;
- summary prompt produces a useful result on sample data;
- Hermes cron job exists with the correct schedule;
- if the destination is a local DB or hub, the latest imported counts/timestamps are checked against the source system rather than inferred from one successful write;
- a test run has delivered or produced the expected final message.

## References

- `references/telegram-it-consulting-monitoring.md` — session-specific notes from the Telegram IT-consulting daily digest setup.
- `references/separate-helper-job-pattern.md` — split an optional/fragile content block into a helper cron job and feed it into the main brief via `context_from`.
- `references/misha-cron-delivery-and-clean-output.md` — Misha-specific rules for test-window delivery, clean user-facing output, and two-message Telegram image posts.
- `references/internal-agent-improvement-jobs.md` — how to create and verify cron jobs that improve the agent itself, including local delivery default, skill-resolution checks, and post-trigger verification.
- `references/hermes-cron-script-job-verification.md` — practical notes for `no_agent=true` script jobs: required `~/.hermes/scripts/` placement, dual-copy workflow, and persisted-output verification.
