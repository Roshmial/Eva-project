# Full pre-update GitHub backup with secrets preserved safely

Use this pattern when a live Hermes-style runtime must be updated, but the user requires that **all data and personal settings remain restorable** and also wants an off-host copy on GitHub.

This is **not** the same as a curated config/code backup.

## When this reference applies

- The live contour includes `~/.hermes` state that matters for restore.
- The user explicitly wants data, auth state, sessions, cron, memory, and personal settings preserved.
- A repo like `cons-github-backup-*` already exists, but it intentionally excludes secrets/runtime state.
- GitHub is required as backup destination, but raw `.env`, `auth.json`, session DBs, and similar files must not be committed in plaintext.

## Core distinction

Keep two backup layers separate:

### 1. Curated GitHub backup
Good for:
- code snapshot
- systemd units
- runbooks
- deploy package
- selected config/scripts

Usually excludes on purpose:
- `.env`
- `auth.json`
- `state.db`
- `response_store.db`
- live sessions
- logs/runtime outputs

This layer is good for reconstruction/bootstrap, but **not enough** for exact restore before a risky runtime upgrade.

### 2. Full pre-update snapshot
Needed for true rollback/restore:
- `~/.hermes/config.yaml`
- `~/.hermes/.env`
- `~/.hermes/auth.json`
- `~/.hermes/state.db`
- `~/.hermes/response_store.db`
- `~/.hermes/memories/`
- `~/.hermes/skills/`
- `~/.hermes/cron/`
- `~/.hermes/sessions/`
- `~/.config/systemd/user/*`
- app/runtime project dirs that are part of the contour

## Workflow

1. Inventory the live runtime first.
   - Confirm where Hermes actually lives.
   - Confirm whether the gateway is a user-systemd unit.
   - Confirm what project/runtime directories are logically part of the contour.

2. Build the full archive on the source host first.
   - Keep the original snapshot on the source host.
   - Compute SHA256 on the source archive.

3. Make a second off-host copy before any upgrade.
   - Pull the archive to the current ops host or another trusted machine.
   - Verify its SHA256 matches the source archive.

4. Export to GitHub only in encrypted form.
   - Encrypt the full archive with a separately stored key.
   - Split encrypted output into parts safely below GitHub's hard blob limit.
   - Commit only:
     - encrypted parts
     - manifest
     - checksums
     - source README/metadata

5. Keep the decryption key outside GitHub.
   - Store it on the source host and the ops host.
   - Do not commit it.
   - Do not place it in the same GitHub backup directory.

## Practical notes

- If GitHub accepts large parts but warns above the recommended 50MB size, treat that as degraded but usable. For the next iteration, reduce split size proactively.
- When a repo already contains weekly curated backup refreshes, add the full encrypted pre-update snapshot under a clearly separate directory such as `full-backups/<timestamp>/`.
- If the commit fails because the repo lacks `git config user.name/user.email`, reuse the repo's existing author identity style instead of inventing a one-off author.

## Verification checklist

Before calling the backup ready, confirm all of the following:
- source archive exists on the live host
- source SHA256 is recorded
- off-host copy exists and SHA256 matches
- encrypted GitHub export exists as parts + manifest + checksums
- push to origin actually completed
- decryption key is present outside GitHub in at least two trusted places

## Anti-patterns

- Treating a curated code/config repo as sufficient rollback material for a live Hermes upgrade.
- Uploading raw `.env`, `auth.json`, or DB files to GitHub in plaintext.
- Keeping the only good copy on the same host that is about to be changed.
- Declaring the GitHub backup complete before verifying the push reached `origin`.
- Losing the decrypt key or storing it only inside the same repo as the encrypted payload.
