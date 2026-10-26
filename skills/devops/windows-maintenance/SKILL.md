---
name: windows-maintenance
description: Use when auditing or cleaning a Windows PC safely.
version: 1.7.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [windows, maintenance, cleanup, repair, powershell, storage]
    related_skills: [execution-finalization-discipline, ponytail, systematic-debugging]
---

# Windows Maintenance

## When to Use

Load this skill for Windows storage pressure, whole-PC health audits, safe cleanup, startup/service optimization, DISM/SFC repair, Docker/WSL disk recovery, or a request to “deep scan” a PC before changing it.

## Purpose

Audit, repair, and clean a Windows PC without deleting user data or turning generic “debloat” advice into uncontrolled system changes. Prefer measurable recovery, reversible settings, and exact post-change verification.

## Workflow

### 1. Fix the scope before touching the machine

- Translate “speed up” or “clean” into the actual symptom: low system-disk space, slow boot, memory pressure, errors, privacy, or malware concern.
- Start with a read-only audit. Do not bundle cleanup into the discovery script.
- Record the initial free space, health state, installed applications, startup state, and pending reboot state.
- Treat user documents, Downloads, browser profiles, game saves, restore points, virtual-machine disks, container volumes, and model stores as protected data until the user explicitly decides otherwise.

### 2. Audit the whole system, not only temporary folders

Collect these classes independently so one failure cannot hide the rest:

1. OS, hardware, RAM, volumes, SSD health, TRIM, pagefile, Secure Boot, TPM, BitLocker and firewall.
2. Top processes, startup entries, non-Microsoft scheduled tasks, services, installed programs and application packages.
3. Full-drive largest directories and files with `diskusage.exe`; include every fixed volume so relocation opportunities are visible.
4. Windows component health with `DISM /ScanHealth`; inspect WinSxS with `DISM /AnalyzeComponentStore`. Do not run `SFC /VerifyOnly` in the routine deep audit: `SFC /ScanNow` belongs in the repair path and already performs verification.
5. Restore-point usage, fragmentation analysis, pending reboot and system/application error events.
6. Application-owned stores: Docker/WSL virtual disks, Ollama models, Steam libraries, game logs and hardware-software caches.
7. Executable trust for startup/task/service binaries: existence, Authenticode status and hash.

Use `references/windows-audit-command-matrix.md` for commands, side effects and PowerShell patterns.

### 3. Classify every candidate before proposing deletion

Use four buckets:

- Regenerable cache: shader cache, delivery optimization, updater artifacts, stale temporary files. Usually safe; explain first-run rebuild effects.
- Application state: Docker VHDX, WSL distributions, virtual machines, game libraries, model stores. Move, prune through the owning application, or delete only after explicit confirmation.
- System recovery data: WinSxS, restore points, hibernation. Use supported Windows commands and explain lost capabilities.
- User data: downloads, media, saves, documents. Never delete automatically; report aggregate size without exposing private filenames in chat.

Do not equate a file’s logical size with safely reclaimable space. For WinSxS, use DISM’s cleanup recommendation; for sparse VHDX files, distinguish logical size, physical size and reclaimable contents.

#### Keep unused-software cleanup as one interactive flow

When the user wants to clean unused software, deliver `analyze → show candidates → explicit selection → uninstall → verify` in the same interface. A report-only audit followed by a separate action menu is an incomplete workflow for this request, and broad system maintenance is a different intent.

- Correlate uninstall inventory with BAM, Prefetch, running processes, startup entries, services and tasks; label stale evidence and missing evidence separately.
- Show numbered candidates with name, publisher, estimated size and last positive-use evidence. Let the user select numbers/ranges and optionally switch to the full non-system desktop-software list.
- Exclude runtimes, redistributables, frameworks, drivers, SDKs, firmware, security updates and dependency-like packages from selection. Enforce live registry flags such as `SystemComponent`, `NoRemove`, `ParentKeyName`, and update/hotfix `ReleaseType`; never uninstall solely because evidence is absent.
- Treat CSV/JSON as usage evidence only. Before display and again immediately before launch, require a direct child key under a protected HKLM uninstall root and rebuild the name, flags, install location, and uninstall command from that live key. In an already elevated process, never execute an HKCU uninstall record: an unelevated user can rewrite it and turn cleanup into privilege escalation. Block a missing, redirected, nested, weak-ACL, or changed key/command.
- Require one explicit confirmation for the final selected set. Remove production parameters that bypass selection or confirmation; test through fixtures/harnesses rather than exposing a noninteractive destructive path.
- Launch only a real `.exe` or canonical system `msiexec.exe` with `System.Diagnostics.ProcessStartInfo` and `UseShellExecute=false`. Reject ambiguous unquoted paths, scripts/documents, `cmd`, PowerShell, `mshta`, `wscript`, and `cscript`; never use `Invoke-Expression`, shell evaluation, or manual deletion of application/user-data directories. For an already elevated flow, restrict executable targets to trusted system/application roots, require a trusted owner, inspect low-privilege write/delete rights on the file and every parent directory, reject reparse points, and use the protected executable directory as `WorkingDirectory`; checking only the file DACL misses owner and parent `DELETE_CHILD` replacement attacks.
- For MSI, convert `/I{ProductCode}` to `/X{ProductCode}`, remove `/forcerestart`/`/promptrestart` and conflicting `REBOOT=...`, then append `/norestart REBOOT=ReallySuppress`. Treat exit `1641` as an unexpected reboot attempt; `3010` is success requiring a manual reboot.
- Require the exact uninstall key to exist before launch and verify that it disappears afterward. A surviving key is `started_not_verified` and makes the overall result `completed_with_errors`; process exit alone is never success.
- Keep analysis artifacts in a unique user-owned temporary directory. Remove them after cancellation or fully verified success; preserve and reveal the path after a failed or unverified removal so diagnostics are not destroyed. Do not emit an intermediate ZIP/report unless explicitly requested.
- Track completeness separately for uninstall registry, BAM, Prefetch, running processes, startup commands, services, and scheduled tasks. Capture non-terminating probe errors explicitly; failed or null process paths for non-system processes also make evidence incomplete. If any mandatory evidence probe is unavailable or fails, block candidate-driven removal rather than treating missing evidence as proof of non-use.
- Keep distinct registry identities even when display name/version match, reprompt malformed or out-of-range selections, and show publisher plus an abbreviated registry identity in final confirmation.
- Keep Microsoft Store/Appx removal separate unless there is an explicit package-level selection and a protected-system-package policy; desktop uninstall evidence does not transfer reliably to Appx.

### 4. Ask only decisions that change data or capabilities

Require explicit choices for:

- deleting all Docker containers, images and volumes versus preserving or moving the data disk;
- disabling hibernation, which also disables Fast Startup;
- removing restore points;
- disabling peripheral, VR, VPN, sync or gaming services;
- deleting personal downloads, game saves or model files.

A tentative statement such as “probably removable” is not consent to data loss. Restate the irreversible consequence and obtain a direct selection.

### 5. Repair before optimizing around corruption

If DISM or SFC reports corruption:

1. Create a restore point when System Restore is available.
2. Run `DISM /Online /Cleanup-Image /RestoreHealth`.
3. Run `SFC /ScanNow`; this command already verifies protected files before repairing them.
4. Run `DISM /Online /Cleanup-Image /StartComponentCleanup` without `/ResetBase` unless loss of update rollback is explicitly approved.
5. Re-run `DISM /ScanHealth`. Do not automatically append `SFC /VerifyOnly` after a successful `SFC /ScanNow`; it duplicates the verification pass and can add a long, apparently stalled stage. Repeat SFC only after reboot when the first result remained inconclusive or corruption persisted.
6. If `RestoreHealth` reports success but the immediate `ScanHealth` still says the component store is repairable, treat repair as open: record the pending-reboot state, reboot, then re-audit before repeating repair. A successful command exit does not override the verification result.

Do not present cache cleanup as a completed optimization while system corruption remains unresolved.

### 6. Make long PowerShell jobs fault-isolated

- Wrap every independent section; record `completed`, `failed` or `skipped`, then continue.
- Add a script-scope trap for unexpected terminating errors and keep a final `collection-errors.txt`.
- Set `$PSNativeCommandUseErrorActionPreference = $false` when available, then inspect native exit codes explicitly.
- Preflight the backing service, not just the executable. If Docker’s named pipe is absent or Ollama is not running, skip the API query while still inventorying its files.
- Target Windows PowerShell 5.1 unless the user explicitly has PowerShell 7. Materialize generic lists before placing them in `[ordered]` reports: `@($list | ForEach-Object { $_ })` or `ToArray()`.
- Treat delimiter counts as a weak static check, never as syntax or runtime validation. Parse or execute on the supported PowerShell runtime before delivery whenever possible.
- Native Windows tools may emit UTF-16 or mixed console encodings. Preserve raw logs plus exit codes; do not infer a clean result from unreadable text.
- Run DISM/SFC as separate native processes with stdout/stderr redirected to report files rather than through a PowerShell pipeline. Poll process completion every 2 seconds, tail the redirected output for the newest percentage, and print each changed percentage. Every 30 seconds report elapsed time, that process's CPU delta, servicing-log timestamp and inactivity duration; aggregate cumulative CPU from unrelated servicing processes can make a dead stage look active. Warn after sustained inactivity, but never auto-kill DISM/SFC because interruption can damage servicing state.
- If the named native process has already exited but the parent script remains blocked, inspect the PowerShell process tree, command lines, process start times, and staging-folder/ZIP timestamps before killing anything. Stop only the child PowerShell that owns the script, preserve the interactive parent, then package the existing staging folder manually; this releases locked transcript handles without discarding the evidence.
- Design the normal script so a native-stage failure cannot strand packaging: write step state and live post-state before archive creation, make archive creation independent of the last probe, and never make an optional verification pass the gate for the result artifact.

### 7. Verify exact effects before reporting completion

After changes, verify:

- free space before and after, using the live volume rather than summing estimates;
- repaired DISM and SFC status;
- removed application registry entry and all approved residual paths;
- absence or presence of `hiberfil.sys` according to the decision;
- preserved services and data that were out of scope;
- reboot requirement and pending file operations;
- non-empty result archive before deleting the staging directory.

For a remotely guided repair, generate a result archive and review it before asking for reboot. If packaging fails or the parent script must be terminated, preserve the uncompressed report, add a manual recovery result with live free space, hibernation state, application registry state and every approved residual path, then archive that folder. Never infer full application removal from one missing data directory, and never delete the only evidence.

### 8. Build recurring maintenance as separated modes

When packaging maintenance for repeated use, keep one launcher but separate these actions:

- deep read-only audit;
- threshold-based cleanup of regenerable caches and individual old temporary files; never delete a directory recursively merely because the directory timestamp is old, because it may contain fresh files;
- DISM/SFC repair on demand;
- Microsoft Update for filtered Windows and driver candidates, without claiming signature guarantees the script did not verify;
- interactive unused-software cleanup: read-only evidence collection, explicit per-program selection, registered uninstaller execution and registry verification in one session;
- an optional weekly lightweight health check.

Never carry one-time destructive approvals such as deleting Docker data or disabling hibernation into the recurring package. Install scheduled tasks only through an explicit menu action, retain a bounded number of reports, and make the scheduled path read-only except for allowlisted cache cleanup when disk free space crosses a documented threshold. Treat “unused” as a review candidate: combine BAM, Prefetch, running processes, startup, services and tasks because Windows has no universal reliable `LastUsed` field. If the requested outcome is removal, keep that evidence, user selection, confirmation, uninstaller launch and verification in one interface instead of stopping at a report.

Make the audit the control-plane input rather than merely another menu item. Delete the old audit pointer before collection, require the new run to produce a verified ZIP, and pass that exact path to the evaluator so a failed run cannot fall back to old evidence. The evaluator must record source SHA-256, rules version, completeness and validation errors; missing/failed mandatory probes must emit `audit_incomplete` and forbid `no_action`. The runner must recheck source existence/hash, rules version, recommendation age and stale-marker state, map only known IDs to a fixed allowlist, and consume a machine-readable `completed`/`completed_with_errors`/`failed`/`blocked` contract from each module. After any attempted state-changing action, remove the recommendation pointer and persist a stale marker so the same audit cannot be reused. Preserve unknown findings for manual review; never broaden a device finding into installing every available driver.

For a reusable package layout, audit-to-action loop, schedule rules and release verification, use `references/regular-maintenance-package.md`.

## User-facing delivery

Lead with the largest measured causes and the expected decision, not a generic checklist. Keep sensitive filenames out of summaries. Separate confirmed findings, approved actions, actual recovered space, and remaining risks. Do not substitute a system-wide maintenance workflow or a report artifact when the user asked for a focused interactive action such as selecting and uninstalling unused applications.