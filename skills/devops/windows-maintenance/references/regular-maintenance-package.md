# Reusable Windows maintenance package

## Package shape

Use one elevated launcher and separate scripts for:

1. Deep read-only audit.
2. Safe recurring cleanup.
3. Component and protected-file repair.
4. Windows and driver updates.
5. Interactive unused-software analysis, explicit selection and registered-uninstaller execution, with a separate read-only mode only when requested.
6. Lightweight scheduled health check.
7. Audit-policy evaluator and confirmed action runner.
8. Explicit schedule install and uninstall.

Keep reports outside the package directory. Package a Russian README, version file and SHA-256 manifest.

## Audit-to-action control loop

Treat each audit as immutable evidence and link modules through files rather than shared process state:

1. Write the audit ZIP and a pointer to the newest successful report.
2. Extract it into a unique temporary directory and parse structured JSON plus only the text probes needed by explicit rules.
3. Emit versioned recommendations containing the source path and SHA-256, severity, reason, recommendation ID, target module and whether the action is safe to offer.
4. Let the action runner consume only the newest recommendation file and map IDs to a fixed module allowlist; never execute a path supplied by audit data.
5. Before collection, remove the old audit pointer. Evaluate only the exact ZIP produced by the new run; never search for a fallback ZIP after a failed audit.
6. Mark an audit incomplete when mandatory probes are missing, failed, or recorded collection errors. An incomplete audit cannot emit `no_action` or authorize state changes.
7. Before action, recheck source existence and SHA-256, supported rules version, recommendation age, completeness and stale-marker state.
8. Require a separate confirmation for each state-changing module. A pending reboot blocks repair, component-store cleanup and updates but may leave read-only review available.
9. Require every module to write a status contract (`completed`, `completed_with_errors`, `failed`, or `blocked`) and report path; process launch alone is not success.
10. After any attempted state-changing action, remove the recommendation pointer and persist a stale marker keyed by source hash. Require a new audit to verify closure and generate a new plan.
11. Keep unsupported or novel findings visible as manual-review items. Expanding the raw audit does not automatically expand execution authority, and a device error must not broaden into installing all available drivers.

Regression-test the evaluator against a representative real audit, not only synthetic JSON. Assert both expected recommendations and important non-findings; for example, inactive Defender is not a critical gap when a registered third-party antivirus is present.

## Safe recurring cleanup

Allow only regenerable data and apply size/age gates:

- individual user and Windows temporary files older than 14 days;
- individual Windows Error Reporting files older than 30 days;
- NVIDIA/DirectX shader caches only above a documented size threshold;
- updater artifacts and hardware-utility caches only above a documented threshold.

Enumerate old files recursively, delete them individually with errors surfaced, then remove only empty directories. Never delete a directory recursively based only on its own `LastWriteTime`, because it may contain fresh files. Never include Documents, Downloads, Recycle Bin, browser profiles, game logs, game libraries, Docker/WSL data, restore points or installed applications. Make WinSxS cleanup a separate switch and never use `/ResetBase` without explicit approval.

## Scheduled check

Schedule a lightweight check rather than deep DISM/SFC work. Collect free space, physical-disk health, problem devices, Defender state, pending reboot and recent storage/hardware errors. Trigger safe cache cleanup only below a documented free-space threshold, such as 20%. Run under the intended interactive user when cleanup depends on that user's `%LOCALAPPDATA%`; a SYSTEM task otherwise cleans the wrong profile. Keep a bounded report history, for example the newest 12 runs.

## Update mode

Gate on pending reboot. Use only Windows Update/Microsoft Update, but do not claim driver signatures unless they are independently verified. Reject preview/beta/Insider, `BrowseOnly`, feature upgrades, BIOS, UEFI, firmware and updates requiring interaction across both software and driver groups. If software updates require reboot, stop before drivers and resume only after reboot. Create a restore point when available, inspect per-update result codes, never reboot automatically, and always produce a `failed` report if the COM session cannot be created. Handle Microsoft Update registration failure by falling back to Windows Update rather than aborting the entire run.

## Unused-software mode

Use one interface for the complete user journey: analyze, display candidates, select, confirm once, launch uninstallers, and verify. Do not stop at a CSV/ZIP when the requested outcome is cleanup.

1. Build desktop inventory from the standard HKLM/HKCU uninstall keys and retain the exact registry identity, publisher, version, location, estimated size, `SystemComponent`, `NoRemove`, `ParentKeyName`, `ReleaseType`, and uninstall metadata. Preserve separate registry records even when display name/version match.
2. Correlate inventory with BAM, Prefetch, current processes, startup commands, services and scheduled tasks. A single old BAM/Prefetch signal does not prove non-use, and absence of evidence is not evidence of absence. Track completeness for registry and every usage probe separately; capture non-terminating errors and failed/null paths for non-system processes, then block removal after any mandatory probe is incomplete.
3. Keep runtimes, redistributables, frameworks, drivers, SDKs, firmware, security updates, hidden/child uninstall records and other dependency-like packages in a protected class that is never selectable.
4. Show numbered candidates with conservative labels and offer a separate command to show all non-system desktop applications. In an already elevated flow, resolve every evidence row to a direct child under a protected HKLM uninstall root and rebuild display/security fields from live registry data. Keep HKCU entries in read-only inventory only: executing a user-writable HKCU record from an elevated process is a privilege-escalation boundary.
5. Parse comma-separated numbers and ranges. Reprompt malformed, overflowing or out-of-range input without terminating; then show name, version, publisher and abbreviated registry identity and require one typed confirmation. Do not expose production switches that bypass selection or confirmation.
6. Immediately before launch, re-read the same live key and require the name and registered command to match what was shown. A CSV is evidence, never an elevated execution source.
7. Accept only a quoted absolute `.exe`, a simple unquoted `.exe` without spaces resolved against `InstallLocation`, or canonical system `msiexec.exe`. Reject ambiguous unquoted paths, script/document associations and command interpreters. For elevated execution, restrict files to trusted Windows/Program Files roots; require trusted ownership, reject low-privilege write/delete access on the file and every parent directory, reject reparse points, and set `WorkingDirectory` to the protected executable directory. Launch with `System.Diagnostics.ProcessStartInfo`, `UseShellExecute=false`, and no shell.
8. For MSI, convert `/I{GUID}` to `/X{GUID}`, strip `/forcerestart`, `/promptrestart`, and conflicting `REBOOT=...`, then append `/norestart REBOOT=ReallySuppress`. Accept `0`; accept `3010` as success requiring a manual reboot; treat `1641` as an unexpected reboot attempt.
9. Require the exact key to exist before launch and poll it afterward. Report only `removed`, `started_not_verified`, or `failed`; a surviving key makes the overall status `completed_with_errors`.
10. Keep analysis files in a unique user-owned session directory. Remove it on cancellation or fully verified success; preserve it and show its path on failed/unverified outcomes. Emit no intermediate archive/report unless requested.
11. Keep Appx/Microsoft Store packages out of this desktop flow unless a separate protected-package policy and explicit package selection are implemented.

## Repair progress

Run `DISM /RestoreHealth`, `SFC /ScanNow`, then `DISM /ScanHealth`. Do not append `SFC /VerifyOnly` routinely. Start each native tool separately with redirected stdout/stderr, poll every 2 seconds, and tail the file for changed percentages so safe process isolation does not look frozen. Every 30 seconds print elapsed time, that process's CPU delta, latest percentage, servicing-log timestamp and inactivity duration. Warn after sustained inactivity but do not auto-kill servicing.

## Release verification

Before delivery:

1. Parse every `.ps1` with `System.Management.Automation.Language.Parser` on a PowerShell runtime; delimiter counts are insufficient.
2. Search read-only scripts for mutating cmdlets and allow only removal of their own temporary report directory.
3. Search the whole package for prohibited one-time actions such as Docker distribution deletion, hibernation changes, `/ResetBase`, disk formatting and partition removal.
4. Create the ZIP with a single top-level directory and reject path traversal during test extraction.
5. Include a pre-elevation verifier in the launcher so a modified or missing file blocks administrative execution.
6. Verify the internal SHA-256 manifest after extracting the final ZIP, then alter one copied file and prove the verifier rejects it.
7. Re-parse the extracted scripts and test ZIP integrity.
8. Run scenario tests for healthy, low-space, corruption, pending reboot, third-party antivirus, hardware failure, incomplete audit, unknown finding, intentionally disabled device, native-process failure, status contracts and stale-audit rejection. Use a representative real audit in addition to synthetic fixtures.
9. For interactive uninstall, additionally test live-registry rebinding, command change after display, missing/nested/HKCU keys, protected system flags, interpreter/script rejection, invalid-selection reprompt, multiple selection, MSI restart suppression, each incomplete evidence probe, duplicate registry identities, and exit-0-with-key-surviving status propagation. Review owner/ACL/parent-chain/reparse-point enforcement statically, and exercise it on Windows when a target is available.
10. State honestly when Windows-specific COM, Task Scheduler or Windows PowerShell 5.1 runtime paths were not exercised on the target PC.