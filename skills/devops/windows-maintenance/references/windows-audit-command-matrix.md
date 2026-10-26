# Windows audit command matrix

## Read-only baseline

| Area | Command or API | Interpretation |
|---|---|---|
| Volumes | `Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3'` | Record size, free bytes and percentage before any work. |
| Largest directories | `diskusage.exe /h /d:4 /t:250 C:\` | Repeat for each fixed volume. Depth can hide deeper cache directories, so pair with top files. |
| Largest files | `diskusage.exe /h /u:250 C:\` | Paths may expose private content; aggregate in user-facing reports. |
| Component store | `DISM /Online /Cleanup-Image /AnalyzeComponentStore` | Explorer size is not the reclaimable amount. Follow DISM’s cleanup recommendation. |
| Component health | `DISM /Online /Cleanup-Image /ScanHealth` | “Repairable” requires a repair stage, not merely cleanup. |
| Protected files | Omit routine `SFC /VerifyOnly`; use `SFC /ScanNow` only in the gated repair path | `ScanNow` already verifies before repair. Avoid a redundant native stage that can be long and visually stalled. |
| SSD/TRIM | `Get-PhysicalDisk`; `Get-StorageReliabilityCounter`; `fsutil behavior query DisableDeleteNotify` | Do not recommend defragmentation for a healthy SSD. |
| Fragmentation | `defrag C: /A /V` | Analysis only; trust its recommendation. |
| Restore points | `vssadmin list shadowstorage`; `vssadmin list shadows` | Recovery data is not ordinary cache. |
| WSL | `wsl --list --verbose`; `wsl --status` | A stopped distribution can still own a large VHDX. |
| Docker | Named-pipe check, then `docker system df -v` | If the engine is stopped, inspect Docker VHDX paths instead of treating the API error as an empty store. |
| Ollama | Process check, then `ollama list`; scan model path | Models may be relocated to another volume rather than deleted. |
| Steam | Read `steamapps\libraryfolders.vdf` | Prefer moving or uninstalling games through Steam. |
| Events | `Get-WinEvent` grouped by provider and ID | A repeated service failure can matter more than one crash; inspect representative messages. |
| Trust | `Get-AuthenticodeSignature`; `Get-FileHash -Algorithm SHA256` | Resolve executable paths from startup, task and service commands first. |

## Supported state-changing commands

| Goal | Command | Required gate |
|---|---|---|
| Repair component store | `DISM /Online /Cleanup-Image /RestoreHealth` | Restore point when available; verify afterward. |
| Repair protected files | `SFC /ScanNow` | Run after DISM, then verify. |
| Clean superseded components | `DISM /Online /Cleanup-Image /StartComponentCleanup` | Do not add `/ResetBase` without approval because it removes update rollback. |
| Disable hibernation | `powercfg /hibernate off` | Explain that Fast Startup is disabled too. Reversal: `powercfg /hibernate on`. |
| Clear Delivery Optimization | `Delete-DeliveryOptimizationCache -Force` | Regenerable cache. |
| Remove Docker Desktop | `Start-Process 'Docker Desktop Installer.exe' -Wait uninstall` | Full data deletion requires a separate explicit confirmation. |
| Remove Docker WSL data | `wsl --shutdown`; `wsl --unregister docker-desktop` | Irreversible deletion of containers, images and volumes. Remove residual allowlisted Docker paths only after this gate. |

## Fault-isolated PowerShell pattern

```powershell
$errors = [System.Collections.Generic.List[string]]::new()
$steps = [System.Collections.Generic.List[object]]::new()
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}
trap {
    $errors.Add("line $($_.InvocationInfo.ScriptLineNumber): $($_.Exception.Message)")
    continue
}

function Invoke-Section {
    param([string]$Name, [scriptblock]$Action)
    try {
        & $Action
        $steps.Add([pscustomobject]@{ Name=$Name; Status='completed' })
    } catch {
        $errors.Add("${Name}: $($_.Exception.Message)")
        $steps.Add([pscustomobject]@{ Name=$Name; Status='failed' })
    }
}

$report = [ordered]@{
    Steps  = @($steps | ForEach-Object { $_ })
    Errors = @($errors | ForEach-Object { [string]$_ })
}
```

Do not use `@($genericList)` directly in Windows PowerShell 5.1 report construction; it can raise a runtime argument-type mismatch. For native commands, reset and inspect `$LASTEXITCODE` explicitly: a non-zero native exit in Windows PowerShell 5.1 usually does not enter `catch`. For long DISM/SFC stages, prefer `Start-Process -PassThru` with redirected stdout/stderr, poll every 2 seconds, tail percentages, and report process CPU delta/inactivity every 30 seconds rather than piping native output through PowerShell.

## Optional-daemon preflight

```powershell
$dockerPipes = @('\\.\pipe\dockerDesktopLinuxEngine', '\\.\pipe\docker_engine')
if (Get-Command docker.exe -ErrorAction SilentlyContinue) {
    if ($dockerPipes | Where-Object { Test-Path -LiteralPath $_ }) {
        docker.exe system df -v
    } else {
        'Docker installed; engine stopped; API query skipped.'
    }
}
```

Inventory the Docker VHDX independently, because an inactive daemon does not mean its data is absent.

## Packaging gate

1. Write structured result, raw command logs, an error list and a machine-readable module status (`completed`, `completed_with_errors`, `failed`, or `blocked`).
2. Stop the transcript before compression.
3. Create the archive with terminating error handling.
4. Verify that the archive exists and is non-empty.
5. Delete the staging directory only after step 4 succeeds; otherwise retain it and report the path.
6. When a parent runner launched the module, return the status and report path through a separate status-contract file; process launch is not completion.
