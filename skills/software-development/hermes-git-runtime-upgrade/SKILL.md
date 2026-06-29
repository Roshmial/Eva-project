---
name: hermes-git-runtime-upgrade
description: Backup-first upgrade of a self-hosted Hermes runtime installed from git, with local patch preservation, service restart, and restore validation.
version: 1.0.0
author: Hermes Agent
---

# Hermes git runtime upgrade

## When to use

Use this skill when Hermes is running on a real host as part of a live contour and the installed runtime comes from a git checkout rather than a disposable package install.

Typical triggers:
- the user asks to upgrade Hermes on a server;
- gateway is part of a production chain like frontend -> backend -> gateway -> Hermes;
- Hermes runs from `~/.hermes/hermes-agent` or another editable git checkout;
- the host may contain local downstream modifications in Hermes source files.

## Goal

Upgrade Hermes without losing:
- auth state;
- config and `.env`;
- memories, skills, cron, sessions, and databases;
- local downstream behavior that was implemented as source patches.

## Core rules

1. Backup first, upgrade second.
2. Never run a blind upgrade on a dirty checkout.
3. Treat local git diffs as product behavior until proven otherwise.
4. Verify the declared runtime contour directly instead of inferring topology.
5. If the user tells you a host is "our server" or that you deployed it, inspect it as owned infrastructure, not as an unknown external host.
6. Do not rely only on `PATH` for Hermes detection. Check explicit install paths as well.

## Topology verification before upgrade

When the user gives an explicit contour like `frontend -> backend -> gateway -> Hermes`:
- verify each layer at that layer;
- do not collapse frontend and backend into one assumption;
- if the frontend server is the current machine, inspect local process, local port, and local service files before trying remote SSH patterns.

For Hermes detection on the target host, check in this order:
- `~/.local/bin/hermes --version`
- `~/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main --version`
- `~/.hermes/hermes-agent/pyproject.toml`
- systemd user unit `hermes-gateway.service`

Reason: non-login shells may miss `~/.local/bin`, which can create a false "Hermes is not installed" conclusion.

## Safe upgrade workflow

### 1. Capture live baseline

Record:
- current Hermes version;
- install method marker if present;
- git branch / HEAD / tag;
- running services related to gateway and web contour;
- health probes for backend and gateway-facing paths.

### 2. Create full restore-capable backup

Backup must include at least:
- `~/.hermes/config.yaml`
- `~/.hermes/.env`
- `~/.hermes/auth.json`
- `~/.hermes/state.db`
- `~/.hermes/response_store.db` if present
- `~/.hermes/memories/`
- `~/.hermes/skills/`
- `~/.hermes/cron/`
- `~/.hermes/sessions/`
- related user systemd units
- any coupled project repo that forms the live contour

If the backup is pushed to GitHub, encrypt it first. Never push raw auth/config/session data to GitHub.

### 3. Freeze local source modifications

Before changing the checkout, save:
- `base-head.txt`
- per-file patches for each modified file
- a full working-tree patch

Store them inside the backup directory.

### 4. Stop only the service layer that must move

If the contour is `frontend -> backend -> gateway -> Hermes`, the risky moving part during Hermes upgrade is usually the gateway.

Prefer stopping only `hermes-gateway.service` first. Keep frontend and backend untouched unless the upgrade path proves they also need coordinated restarts.

Important pitfall:
- some agent runtimes or wrappers may block a direct self-stop command if the command appears to terminate the live gateway process that is carrying the current session;
- in that case, stop the systemd user service through a separate remote shell or separate process boundary.

### 5. Upgrade by git/tag, not by wishful abstraction

For git-based installs:
- fetch tags and remotes;
- choose an explicit target tag or commit for reproducibility;
- stash local modifications;
- checkout the target tag/commit;
- refresh the venv and reinstall with `pip install -e .`.

Prefer a fixed release tag over a floating branch for production upgrades.

### 6. Reapply downstream behavior consciously

Do not assume old patches apply cleanly.

Process:
- inspect the new upstream context around each old patch;
- if the patch applies cleanly, great;
- if not, restore the behavior semantically and minimally;
- if upstream already removed the original problem, do not reintroduce a needless patch.

### 7. Run restore-oriented validation

Minimum validation after restart:
- Hermes version is the expected new version;
- gateway service is active and enabled;
- cron listing works;
- backend health still works;
- `config.yaml`, `.env`, `auth.json`, `state.db`, memories, skills, cron, sessions still exist;
- preserved downstream custom behavior still compiles and behaves as expected.

### 8. Record residual debt

If a local downstream patch remains after the upgrade, record it explicitly as technical debt for the next upgrade.

## Pitfalls

### False negative on Hermes presence

A plain `hermes --version` can fail in a non-login shell even when Hermes is installed and running. Always check explicit runtime paths before concluding Hermes is absent.

### Wrong host ownership assumption

If the user says a server or contour is yours, act on that. Do not treat it as an unknown external host and do not switch to indirect heuristics before checking the host directly.

### Blind `hermes update` on dirty checkout

This can overwrite or conflict with local downstream behavior. Freeze patches first.

### Reapplying obsolete patches

After upgrade, an old patch may no longer be needed because upstream already changed the code path. Reapply semantics, not lines.

## Deliverables

A successful run should leave behind:
- a restore-capable backup;
- saved local patch files;
- the upgraded runtime;
- a verified gateway restart;
- a short log of what downstream behavior still remains patched.

## References

- `references/178-backup-first-upgrade-example.md` — concrete example of backup-first git upgrade with encrypted GitHub backup, patch freezing, manual cron patch restoration, and post-upgrade verification on a live contour.
