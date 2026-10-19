---
name: session-librarian
description: "Organize sessions by prompt: find, rename, archive, prune."
version: 1.0.0
author: Hermes Agent + Teknium
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Sessions, Organization, Cleanup, Library, Productivity]
    category: productivity
    related_skills: [weekly-review-planning]
---

# Session Librarian

Manage the user's session library conversationally: find past sessions about a
topic, summarize what they decided, rename them meaningfully, split work into
parallel sessions, and propose stale ones for archive or deletion — all from a
plain-language request like *"find my sessions about Q3 pricing, keep the
useful ones, and clean up the duplicates."*

Inspired by Perplexity Computer's prompt-driven session management (Aug 2026):
the agent starts, organizes, and cleans up the user's own session library, and
always shows the plan before touching anything.

## When to Use

- "What sessions do I have about X?" / "What did we decide about X?"
- "Rename these sessions to something meaningful."
- "Clean up my session library" / "archive the stale ones."
- "Fork that session into a follow-up focused on Y."
- "Split this into one session per ticket" (see Parallel workstreams below).

## The Two Surfaces

| Task | Surface |
|---|---|
| Find sessions by topic, read content, summarize decisions | `session_search` tool (FTS5 over the message store) |
| List/filter by metadata (age, source, cost, tokens, workspace) | `hermes sessions list` / `stats` via terminal |
| Rename | `hermes sessions rename <session_id> <title...>` |
| Bulk soft-hide (reversible) | `hermes sessions archive <filters>` |
| Delete (destructive) | `hermes sessions delete` / `hermes sessions prune <filters>` |
| Export before deleting anything valuable | `hermes sessions export --session-id <id> --format md` |
| Continue work in a new place | `/branch` (fork current session) or start a fresh session and cite the summary |

## Procedure

① **Discover.** Use `session_search(query=..., limit=5-10)` with topic
keywords; vary phrasing (feature name, symptom, project name). For metadata
sweeps ("sessions older than 60 days from telegram"), use
`hermes sessions list --source telegram --limit 50` instead.

② **Summarize per session.** The discovery result's `bookend_start` (goal),
match window, and `bookend_end` (resolution) usually suffice — only dump a
full session (`session_search(session_id=...)`) when the user asks for
decisions in depth. Report each as: link (`@session:` form) — one-line goal —
one-line outcome.

③ **Plan before acting (MANDATORY for anything that mutates).** Present a
plan table first: which sessions get renamed to what, which get archived,
which are proposed for deletion and why (duplicate of which keeper, stale,
empty). Wait for the user's go-ahead. Exception: a single rename the user
explicitly dictated can be done directly.

④ **Choose a retention tier before deleting.**
- Prefer `archive` (reversible soft-hide) over `delete`/`prune`.
- When cleanup is driven by database size, do not jump from raw online history straight to deletion. Keep recent sessions raw online, keep reusable conclusions in the canonical decision log, and retain raw history in a compressed cold archive.
- Preserve important, pinned, active, unresolved, compliance-relevant, or explicitly protected sessions raw regardless of age.
- Do not create a permanent summary per session by default. Use temporary compact extracts only to audit coverage; promote the reusable meaning into one canonical topic entry in the decision log.
- Before pruning a meaningful session, require all gates: verified raw archive; semantic decision-log coverage or explicit `no reusable knowledge` classification; source evidence for added decisions; resolved conflicts/supersession; deterministic sample verification; protected-session exclusions.
- Always run destructive commands with `--dry-run` first and show the output, then re-run with `--yes` after confirmation.
- If a monolithic export is too resource-intensive, archive a transactionally consistent database snapshot or export bounded batches; never treat an incomplete export as protection.

⑤ **Act and verify.** Apply the approved rename/archive/prune plan with the safest primitive. For tiered retention, verify decision-log retrieval for known topics, inspect cited raw messages, restore or inspect a sample archived session, and falsify the `noise` classification on a deterministic sample before deleting online originals.

⑥ **Report.** Report renamed/archived/pruned counts, decision-log topics added or consolidated, archive/checksum status, sample-verification result, protected/skipped sessions, measured post-cleanup size, and how to access archived records.

## Parallel Workstreams

For "one session per ticket, investigate each, report back": do NOT try to
drive other live sessions. Use `delegate_task` with one task per workstream —
each subagent runs in its own session automatically — then synthesize their
summaries. Mention that each delegation's transcript is itself searchable
later via `session_search`.

## Pitfalls

- **Never delete without a dry-run + explicit confirmation in this
  conversation.** A standing "clean things up" is authority to *propose*, not
  to prune.
- **`session_search` finds content, not metadata.** Age/cost/source filters
  live in the CLI; combine both when the request mixes them ("old sessions
  about pricing").
- **Titles are identity for `/resume <title>`.** When renaming, keep titles
  short, unique, and prefix-friendly; warn the user if a rename collides with
  an existing title.
- **Archived ≠ deleted.** Archive hides sessions from default listings only.
  Say which one you did.
- **Do not substitute a backup for usable memory.** A compressed raw database protects recoverability but does not preserve day-to-day recall; verify semantic coverage in the canonical decision log before pruning online history. Per-session summaries are optional audit artifacts, not a required second knowledge base.
- **Do not present expected space savings as achieved.** Measure database size after prune/index rebuild/VACUUM; page reuse and FTS structure make pre-clean estimates unreliable.
- **Cross-profile session links** (`@session:<profile>/<id>`) are read-only
  from another profile; management commands act on the current profile's DB.

## Verification

After a cleanup pass, re-run the discovery query and `hermes sessions list`
to confirm the library reflects the plan (keepers present with new titles,
archived ones gone from the default listing). For tiered retention, also verify
decision-log retrieval, cited-message traceability, archive integrity, a deterministic noise sample, and one sample restore before claiming the old sessions are safely removable.

See `references/tiered-session-retention.md` for the decision-coverage contract, gates,
and a reusable hot/warm/cold retention design.
