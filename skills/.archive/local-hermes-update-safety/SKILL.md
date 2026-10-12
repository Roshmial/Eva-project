---
name: local-hermes-update-safety
description: Use when changing Hermes update/backup behavior safely.
---

# Purpose

Use this skill when changing how Hermes Agent performs self-update, pre-update backup, repair-on-current-checkout, or nearby operator-safety logic.

The goal is to keep `hermes update` safe for real mutations while avoiding noisy or wasteful work on paths that only check availability.

# When to use

Use this skill when the task involves any of:

1. `hermes update` sequencing
2. pre-update backup behavior
3. repair behavior when checkout is current but runtime/venv is unhealthy
4. deciding whether scheduled backups overlap with update-triggered backups
5. validating that a no-op update path stays side-effect-light

# Core rule

For Hermes self-update flows, separate these three phases explicitly:

1. availability check
2. mutation decision
3. safety backup before mutation

A plain availability check like `git fetch` + `rev-list` should not create a new pre-update backup by itself.

Pre-update backup should run only when the command is about to mutate the checkout or runtime, for example:

- applying new commits
- resetting or merging to a new target revision
- repairing Python dependencies / recreating venv on an unhealthy runtime

# Recommended sequence

1. Resolve update target branch.
2. Fetch remote refs needed for the check.
3. Determine whether there are actual new commits to apply.
4. If no new commits and no runtime repair is needed, exit without creating a fresh pre-update backup.
5. If commits exist, run pre-update backup immediately before the first real mutation.
6. If checkout is current but runtime repair is needed, run pre-update backup immediately before repair work.
7. Keep the backup call idempotent within the command so multiple mutation branches do not create duplicate backups.

# Design guidance

## Treat backup as a mutation boundary guard

The backup belongs at the boundary before meaningful mutation, not at the start of the command.

Bad pattern:
- backup first
- then discover nothing will change

Better pattern:
- check first
- if change/repair is truly needed, back up once
- mutate immediately after

## Distinguish backup classes

Do not treat all backups as duplicates just because they touch some of the same files.

Typical split:
- scheduled curated Git backups: portability, documentation, selected config, curated recovery surface
- pre-update backup: local safety rollback before runtime mutation
- data-specific backups: DB snapshots for a separate operational dataset

Partial overlap is acceptable when the recovery intent differs.

## Prefer one-shot helper semantics

Inside update code, use a local helper or guard so backup can be requested from several branches but executes only once.

Example intent:
- real code update path requests backup
- runtime repair path requests backup
- no-op path never requests backup

# Verification checklist

After changing update-backup sequencing, verify all three cases:

1. no-op update path does not trigger backup
2. real update path does trigger backup before apply
3. runtime-repair path on current checkout does trigger backup before repair

Also run a wider nearby test slice so sequencing changes do not silently break adjacent update logic.

# Good regression tests

Add focused tests for:

- `Already up to date` path with healthy runtime
- update path with positive commit count
- current checkout + unhealthy venv/runtime repair path

A useful assertion pattern is to patch the backup function and make it raise a sentinel exception in the paths where it must be called.

# Pitfalls

## Pitfall: backup tied to command start instead of mutation start

This creates unnecessary archives on every no-op update and becomes especially noisy when the environment already has regular scheduled backups.

## Pitfall: removing backup from repair path

`Already up to date` does not imply a healthy runtime. If the command repairs Python dependencies or recreates the venv, that is still a mutation boundary and still deserves pre-update backup.

## Pitfall: declaring scheduled backups a full duplicate

Curated Git backups, DB backups, and pre-update rollback backups usually serve different restore scenarios. Check scope and restore intent before pruning one.

# Session-specific reference

See `references/update-backup-ordering.md` for the concrete July 2026 Hermes case: reordered pre-update backup after availability check, reviewed overlap with scheduled backups, and validated with targeted pytest coverage.
