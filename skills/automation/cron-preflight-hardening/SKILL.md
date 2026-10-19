---
name: cron-preflight-hardening
description: "Use when flaky cron jobs need preflight hardening."
version: 1.0.0
author: Hermes Agent
license: MIT
created_by: agent
metadata:
  hermes:
    tags: [cron, automation, reliability, preflight]
    related_skills: [scheduled-hermes-monitoring, hermes-agent]
---

# Cron preflight hardening

Use when a recurring Hermes cron job technically runs but behaves unstably: loops on web search, wastes turns re-deriving deterministic context, drifts stylistically, or produces outputs that are valid syntactically but weak operationally.

This skill is for Hermes-managed cron jobs. Prefer tightening the existing Hermes job before inventing a separate daemon or external scheduler.

## When to use

- A user-facing cron job mixes deterministic context gathering with creative synthesis and becomes flaky.
- A web-heavy cron job keeps retrying search or broadens scope until quality drops.
- A daily/weekly job repeatedly spends tokens re-reading the same local context before it can do the real work.
- The user asks to make an existing cron job more stable rather than redesigning the whole system.

## Core pattern

Split the job into two layers:

1. Deterministic preflight script
- Put stable context gathering into a script under `~/.hermes/scripts/`.
- The script should output only compact, high-signal context the agent will actually use.
- Good preflight outputs: current Moscow date/time, week boundaries, local YAML-derived day context, recent outputs, recent linked recommendations, allowed source URLs, dedup hints.

2. Narrow agent layer
- Leave only selection, ranking, synthesis, and light verification to the agent.
- Rewrite the cron prompt so the script output is the primary context.
- Tell the agent not to re-derive script-provided facts unless it needs selective verification.

## Implementation steps

1. Inspect the current job class
- Decide whether the job is really an agent job.
- If the task is pure collection/backup/sync, move toward `script + no_agent=true`.
- If the task needs reasoning or writing quality, keep it as an agent job but reduce its surface area.

2. Move deterministic inputs into a preflight script
- Save the script under `~/.hermes/scripts/`.
- In cron config, reference the script by filename only, not an absolute path.
- Keep the script idempotent and side-effect-light unless persistence is explicitly needed.

3. Tighten source strategy for web-heavy jobs
- Start from official URLs when available.
- Use `web_extract`/direct extraction first.
- Treat `web_search` as rescue path only.
- Set explicit per-source and total search caps in the prompt.
- Stop searching as soon as enough verified items exist.

4. Add anti-repeat and anti-drift context
- Feed recent outputs or recent linked recommendations from local files/state into the script output.
- Explicitly instruct the agent not to repeat recent recommendations when another verified option exists.
- For daily briefs, feed recent final texts so critic/generator stages can avoid slipping back into banned phrasing.

5. Harden style requirements in the prompt
- Ban known bad phrasing classes explicitly when the user has already rejected them.
- For ordinary workday briefs, prefer one direct grounded recommendation over soft coaching.
- If there is no valid event/helper item, forbid inventing a surrogate city recommendation just to make the output feel richer.

6. Isolate script dependencies from the Hermes runtime
- For project scripts that import third-party packages, create a project-owned virtual environment with a pinned requirements file; do not rely on packages manually present in Hermes's own venv.
- A Hermes runtime upgrade may replace its Python generation. Treat every import from that environment as ephemeral unless Hermes itself declares the dependency.
- `no_agent` scripts are executed by the scheduler's interpreter, so a shebang does not select another Python. Make the cron launcher explicitly `exec` the project Python or spawn it by absolute path before importing project packages.
- Route every entry point for the same data pipeline — cron wrappers, systemd services, collectors, backups, and refresh hooks — to the same project environment. Fixing only the job that alerted leaves sibling jobs broken.

7. Check capacity and coordinate database jobs
- Before a database rebuild or backup, check free space against live database + staging copy + retained backup + safety margin. Atomic rebuilds and backup rotation temporarily require multiple full-size copies.
- If space is exhausted, remove only verified rebuildable caches first; never delete live databases, WAL/SHM files, or the last valid backup to make room.
- Prefer atomic staging plus `os.replace` for analytical rebuilds so an interrupted or ENOSPC run cannot corrupt the live database.
- Do not let a frequent collector synchronously trigger a full analytical rebuild. Keep collection cheap and schedule the heavy refresh separately; otherwise several healthy jobs can combine into continuous CPU/RAM pressure.
- If refresh and backup touch the same database, serialize them with one shared OS lock. Hold the lock across `exec` or wrap the entire systemd `ExecStart` with `flock`; a Python lock descriptor must be inheritable or it vanishes when the launcher replaces itself.
- For a periodic service whose runtime may exceed its interval, schedule from completion with `OnUnitInactiveSec`, not from start with `OnUnitActiveSec`; the latter can restart the job immediately and keep it running almost continuously.
- Stream large SQLite-to-DuckDB imports in bounded batches and compute status aggregates in SQL. Avoid materializing all message content twice in Python, because payload expansion can exceed RAM even when the database fits on disk.

8. Live-verify immediately
- Update the job and run it manually right away.
- Read `hermes cron runs <id>` and the produced artifact; scheduler success alone is insufficient.
- For backups, recompute the checksum and inspect the manifest/source counts. For sync jobs, verify the target file changed or was correctly reported unchanged.
- Run one sibling job that shares the repaired runtime, then check the next scheduled execution path or service unit points to the same environment.
- After a Hermes runtime change, inspect `hermes cron list --all`, not just the job that alerted. Group jobs by shared launcher, project environment, web provider, database, and delivery target; repair the dependency boundary once per group and rerun every previously failed job.
- For user-facing jobs, verify execution and delivery separately. A durable `completed` run without `delivery_outcome=delivered` is not a recovered notification pipeline.

9. Treat input freshness as a release gate
- A no-signal report is valid only after the source file exists, is readable, and is fresh for the job window.
- Missing, malformed, or stale telemetry must produce an explicit failed/degraded status; never render it as a clean report with zero findings.
- A backup job may succeed only when it copied the live source. If it falls back to an older backup, do not create a new dated snapshot or silently advance retention.
- Keep QA jobs read-only by default. A report that applies inferred overrides is a state-changing classifier and must be a separate explicit job with a deliberate apply boundary.

## Prompt-writing rules that helped

### For weekly event jobs
- Provide allowed source clusters in script output.
- Tell the agent to use official source URLs first.
- Allow at most one rescue search per source and a small total search budget.
- Prefer fewer verified items over a padded list.

### For daily brief jobs
- Provide day context, helper output, recent finals, and recent linked anchors in script output.
- Use the script output as the first-class day context.
- Reserve tools for selective checks only: weather, a missing fact, or anti-repeat confirmation.
- In a normal workday without a valid helper event, require one short direct work anchor rather than a lifestyle-style closing.

## Pitfalls

- Do not pass the cron script path as an absolute path in `cronjob update`; Hermes expects a filename relative to `~/.hermes/scripts/`.
- Do not let preflight output balloon into a full transcript dump; the goal is to reduce agent load, not relocate it.
- Do not treat `web_search` as the default first step when you already know the canonical source URLs.
- Do not accept `last_status=ok` as proof of success; inspect the real output file.
- Do not rely on a prompt-only fix when the instability comes from the job mixing context collection and synthesis.
- Do not install project-only Python packages into Hermes's managed runtime as the durable repair; the next runtime generation can remove them.
- Do not validate an `exec`-based launcher only with static syntax checks; run it through `hermes cron run` because the scheduler's execution wrapper changes `__file__`, argv, environment, and interpreter behavior.
- Do not repair only the first missing import after a runtime replacement. Import-test the whole project entry point and pin its transitive runtime dependencies, because the next missing package otherwise appears one cron cycle later.
- Do not mark an entire cron estate fixed from scheduler heartbeat or a count of active jobs. Check the latest durable run for every previously failed job, verify delivery for user-facing jobs, and test one representative path from each shared dependency family.

## Verification checklist

- Job still scheduled and enabled.
- Script attached and referenced by relative filename.
- Prompt reflects the new two-layer boundary.
- Live run succeeds.
- Output artifact contains the intended user-facing result, not service text.
- Search behavior is narrower and more deterministic than before.

## References

- See `references/weekly-event-and-daily-brief-preflights.md` for reusable weekly-event and daily-brief preflight shapes, including the relative-script-path pitfall.
- See `references/database-refresh-backup-coordination.md` for a reusable locking, scheduling, batching, and verification recipe for analytical hubs.
