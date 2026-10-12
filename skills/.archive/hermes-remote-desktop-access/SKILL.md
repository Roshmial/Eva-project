---
name: hermes-remote-desktop-access
description: "Use when connecting Hermes Desktop to a remote runtime."
version: 1.0.0
created_by: agent
---

# Remote access from Hermes Desktop / Hermes One

## Default decision

Use **SSH Tunnel** when the desktop must manage the remote Hermes profile, including sessions, skills, memory, gateway, logs, and schedules. Keep the remote API bound to `127.0.0.1`; do not expose it publicly just to connect a desktop client.

Use plain **Remote** mode with an HTTP URL and API token only when chat-only access is sufficient and exposing a separately protected HTTPS endpoint is an explicit, justified choice.

## Procedure

1. Verify the remote runtime before asking the user to configure the desktop.
   - Confirm SSH is listening on the intended interface and port.
   - Confirm the Hermes API responds locally on the intended tunnel port, normally `127.0.0.1:8642/health`.
   - Confirm the SSH username resolves to the same home directory that owns the working `~/.hermes` profile.
   - Do not restart the gateway merely to test SSH Tunnel readiness; SSH forwarding and API health can be checked independently.

2. Configure SSH Tunnel in the desktop client.
   - Set SSH Host, SSH Port, remote runtime username, and Remote Hermes Port.
   - Set the **private** key file, for example `C:\Users\<user>\.ssh\id_ed25519`; never select `id_ed25519.pub`.
   - After a successful SSH test, save the connection and fully restart the desktop application before judging online status.

3. Diagnose authentication before changing server keys.
   - Compare the Windows public-key fingerprint with the server's `authorized_keys` fingerprint first.
   - If the private key has a passphrase, load it into Windows `ssh-agent` before starting the desktop client. Do not ask the user to share a passphrase or remove encryption by default.
   - Add a public key to the server only after proving that the supplied private key does not correspond to an authorized key.

4. Diagnose reachability separately from authentication.
   - A TCP timeout to the public SSH host is a network-path failure, not a key failure.
   - When both machines are already online in the same Tailscale tailnet, prefer the remote machine's Tailnet IP as the SSH Host. This preserves loopback-only API exposure and avoids relying on a blocked public SSH path.

5. Verify the usable connection.
   - Confirm the desktop's SSH test succeeds.
   - Confirm the tunnel endpoint responds from the remote side before claiming server readiness.
   - If the client remains offline after Save and a full application restart, obtain the connection-screen error and inspect the exact saved desktop configuration; do not guess that a healthy `/health` endpoint proves desktop protocol compatibility.

## Windows notes

Use quoted interpolation when constructing an SSH-key path in PowerShell:

```powershell
ssh-add "${env:USERPROFILE}\.ssh\id_ed25519"
Get-Content "${env:USERPROFILE}\.ssh\id_ed25519.pub"
```

Prefer opening the `.pub` file in a text editor when the only goal is to copy its public-key line; do not create unnecessary shell steps.

## Pitfalls

- Separate authentication from transport diagnosis: a public-host timeout happens before key validation, so rotating keys cannot fix it.
- Preserve passphrase protection and use `ssh-agent`, because an encrypted private key may not be usable directly by a desktop client's non-interactive SSH implementation.
- Use the runtime owner's SSH account, because the SSH proxy resolves `~/.hermes` for that account and otherwise management screens show unrelated or empty data.
- Treat SSH Test as an authentication check, not full client acceptance; save and restart the desktop app before evaluating its connection state.
