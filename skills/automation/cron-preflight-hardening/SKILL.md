---
name: cron-preflight-hardening
description: "Use when flaky cron jobs need preflight hardening."
version: 1.0.0
author: Hermes Agent
created_by: agent
---

# Cron preflight hardening

Use when a recurring Hermes cron job technically runs but behaves unstably: loops on web search, wastes turns re-deriving deterministic context, drifts stylistically, or produces outputs that are valid syntactically but weak operationally.

This skill is for local-first Hermes cron jobs. Prefer tightening the existing Hermes job before inventing a separate daemon or external scheduler.

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

6. Live-verify immediately
- Update the job.
- Run it manually right away.
- Read the produced cron output artifact and verify the actual delivered text, not only scheduler status.

7. Treat input freshness as a release gate
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

## Verification checklist

- Job still scheduled and enabled.
- Script attached and referenced by relative filename.
- Prompt reflects the new two-layer boundary.
- Live run succeeds.
- Output artifact contains the intended user-facing result, not service text.
- Search behavior is narrower and more deterministic than before.

## References

- See `references/weekly-and-daily-cron-redesign-2026-08.md` for a concrete redesign pattern: weekly event preflight plus daily brief preflight, including the relative-script-path pitfall.
