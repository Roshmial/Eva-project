# Hermes update and runtime migration troubleshooting

## Purpose

Use this when `hermes update` reports failure, leaves an old gateway running, or updates the checkout without a clean final receipt. The goal is to identify the failed stage, repair only that stage, and prove the running gateway actually switched.

## Procedure

1. Read the newest structured update receipt under `$HERMES_HOME/logs/update_receipts/`.
   - Record `pre_update`, `post_update`, `stages`, dependency-sync outcome, planned runtimes, and gateway restart state.
   - Treat `outcome: running` with a dead writer PID as an interrupted receipt, not proof that the update is still active.

2. Separate four states explicitly.
   - Checkout: Git/source revision moved.
   - Dependencies: PM generation/venv built successfully.
   - Service definition: systemd/launchd points to the intended launcher/runtime.
   - Live gateway: replacement process actually loaded the intended revision and reconnected its platform.
   Never collapse these into one claim such as “the version installed.”

3. Diagnose dependency-sync failures from the first package build error.
   - Run `hermes pm status` and `hermes pm doctor`, then inspect the selected managed Python and its `sysconfig` compiler values.
   - A package without a wheel for the selected Python must build from source; verify the required compiler/build tools before retrying.
   - Reproduce the single failing package in a scratch target with the same Python and proposed environment override. A successful isolated build/import is the acceptance gate before rerunning the whole update.
   - Prefer a one-run `CC`/`CXX` override when it is proven compatible; do not modify global compiler links or install broad toolchains merely to test a hypothesis.

4. Build dependencies without disrupting the live gateway.
   - Run PM sync/install first and verify the new generation, imports, and launcher.
   - Refresh an outdated service definition before cutover so restart cannot relaunch the legacy venv.
   - Keep the old gateway serving until the new runtime passes these checks.

5. Perform one controlled cutover.
   - When invoked from inside the gateway, use Hermes's supported update/restart path; direct child commands may be refused because the gateway would kill them mid-command.
   - End the in-flight turn before a drain-aware background update needs to restart the gateway.
   - Expect the updater process itself to receive SIGTERM during a successful self-restart; classify the operation from replacement evidence, not that exit code.

6. Verify after cutover.
   - Compare old/new PID and start timestamp.
   - Check `hermes --version`, `hermes update --plan`, service status, and the process command/runtime path.
   - Read gateway logs until the required messaging platform reconnects.
   - Exercise the original user path that motivated the update.

7. Report version identity precisely.
   - A string such as `vX.Y.Z+N.gSHA` is a build N commits beyond the tag, not the exact stable tag.
   - State channel, tag ancestry, live commit, and whether the worktree is dirty separately when they matter.

## Pitfalls

- Do not infer a restart-stage failure when the receipt shows dependency sync failed earlier; the old gateway is then a safety fallback, not the cause.
- Do not trust `pm doctor` alone for source builds; it can validate managed tools while a package-specific compiler dependency is still absent.
- Do not use systemd `active` as proof of new code; an unchanged PID may still be the pre-update process.
- Do not call an interrupted receipt “complete” merely because the replacement gateway is healthy; verify whether any stale marker or actionable stage remains, and distinguish operational health from receipt bookkeeping.
