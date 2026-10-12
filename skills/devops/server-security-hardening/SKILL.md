---
name: server-security-hardening
description: Use when auditing or hardening an Internet-facing server.
---

# Linux Server Security Hardening

## Operating rule

Treat hardening as a live change with lockout risk. Inspect first, preserve the management path, make the smallest persistent change, and verify both local function and external exposure before reporting completion.

## Procedure

1. Establish the real exposure surface.
   - Inspect listeners with `ss -lntup` and map each PID to its command, parent, cgroup, and working directory.
   - Test the public IP and relevant ports; a loopback check alone does not prove that a service is closed externally.
   - Inspect firewall/security-group state when privileges and provider access allow it. State explicitly when either layer could not be read.
   - Separate loopback-only, private-overlay, and public listeners in the findings.

2. Inspect the controls that determine persistence.
   - Identify system or user systemd units, containers, supervisors, environment files, and startup scripts before killing a PID.
   - Change the owning persistent configuration rather than stopping a process that will restart with the old bind address.
   - For a service that need not be public, prefer binding it to `127.0.0.1`; use a firewall or cloud security group as an additional layer, not as a substitute for a safe bind.

3. Protect secrets while editing configuration.
   - Never use a generic patch/read operation on a secret-bearing `.env` file when its diff or output may reveal adjacent values.
   - Perform a key-targeted edit with a script that prints only status, never the file content or replacement secret.
   - If tool output exposes a credential, rotate every credential that can be rotated immediately, restart dependent services, verify recovery, and disclose the residual credential that requires owner-side rotation.

4. Apply the change safely.
   - For user services, edit the user unit or its environment source, then run `systemctl --user daemon-reload` and restart only the affected units.
   - For SSH, firewall, routing, or provider security-group changes, preserve an existing session or out-of-band console until a second connection succeeds.
   - Do not claim package patching was completed when `sudo` or provider privileges blocked it. Complete all unprivileged hardening first, then give the exact privileged command and residual risk.

5. Verify completion from both sides.
   - Confirm the listener address with `ss -lntp`.
   - Confirm the local health endpoint or expected HTTP status.
   - Confirm the same port is unreachable through the public address from an external vantage point when possible; a self-connect through the public IP is useful but may not model every cloud firewall path.
   - Confirm service state and enablement so the fix survives restart.
   - Re-read logs after restart for bind errors, dependency failures, or authentication regressions.

6. Prioritize controls by risk reduction.
   - First: security updates, key-only SSH, no direct root login, restricted public listeners, and firewall/security-group allowlists.
   - Next: TLS/reverse proxy, rate limiting, Fail2ban/CrowdSec where appropriate, secret rotation, and application-level authorization review.
   - Treat SSH tarpits such as Endlessh as optional telemetry/noise reduction only; they do not replace patching, authentication hardening, or network access control.

## Reporting

Report three things plainly:
- what was verified and changed;
- what remains exposed or unverified;
- the single next action with the largest risk reduction.

Never describe a port as closed merely because the application stopped responding locally; cite the listener state and public-path test.