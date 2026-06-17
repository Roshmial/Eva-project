# Hermes gateway under a dedicated service user on VPS

Use this note when Hermes is installed for a non-root user and gateway/service activation is part of remote server bootstrap.

## Durable lesson

`hermes gateway install` may write the user unit successfully but still fail at activation if it is launched from root through `runuser` without a proper user-systemd session/bus.

Observed failure shape:
- prompts for gateway startup and boot autostart are answered successfully;
- unit file is written under `~/.config/systemd/user/`;
- failure occurs at `systemctl --user daemon-reload`;
- message resembles `Failed to connect to bus: Permission denied`.

## What to do instead

Prefer this split:
1. Use root only for machine bootstrap: packages, users, directories, permissions, SSH, nginx, PostgreSQL.
2. Use the target runtime user for Hermes install/config and especially for gateway activation.
3. Perform `systemctl --user daemon-reload`, `enable`, and `start` from a real user session or another invocation path that has a valid user-systemd context.
4. Verify both the unit file location and the actual service state; file creation alone is not success.

## Why this matters

This failure is easy to misread as "gateway installed" because the binary exists and the unit file may already be present. In practice, the service is still not active.

## Related migration rule

When server migration has many moving parts, keep "service installed" and "service activated in user systemd" as separate checklist items. This prevents reporting a false-green deployment state.
