# Combined contour checklist

Use this when a live app backup must span more than one host.

## Verify contour first
- active frontend host/port
- active backend host/port
- actual systemd unit names
- working directories from unit files
- launcher scripts from `ExecStart`

## Backup scope
Include:
- project code needed for runtime and maintenance
- deploy/package files
- scripts and docs
- systemd units and drop-ins
- launcher scripts

Exclude:
- `.env*`
- runtime DB/data directories
- logs and dumps
- caches
- `node_modules`
- `.venv`
- `dist`

## Combined-host decision rule
Prefer one central backup job when one host can read both sides of the contour.
This avoids:
- duplicate backup logic
- diverging schedules
- different GitHub auth setups
- ambiguous source of truth

## Copying rule
- local files: regular copy
- remote files: enumerate allowed files first
- remote binary files: copy as bytes, not decoded text

## Scheduler rule
- run the weekly job on the central host
- remove older duplicate jobs from secondary hosts
- when the host runs UTC, convert Moscow time explicitly and record the conversion

## Final verification
- manual script run succeeded
- push to GitHub succeeded
- remote `origin` is correct
- scheduled job exists
- old duplicate scheduler removed
