---
name: hermes-browser-debugging
description: Troubleshoot and fix Hermes browser tool failures, with emphasis on local Chromium, CDP routing, and end-to-end verification.
version: 1.0.0
author: Eva
---

# Hermes browser debugging

## When to use
- Hermes browser tools fail, hang, or return inconsistent results.
- `browser_navigate` claims success but the page state is wrong.
- `browser_snapshot` is empty, stale, or mismatched with the reported URL/title.
- Local browser mode behaves differently from cloud/CDP mode.
- You are modifying `tools/browser_tool.py` or validating a browser-layer fix.

## Core principle
Do not trust a single success signal from `browser_navigate`. Browser fixes are only real when the state is verified end-to-end:
1. navigation returns success,
2. snapshot shows expected content,
3. console or supervisor confirms the actual URL,
4. at least one follow-up action still works in the same session.

A reported title alone is not enough.

## Workflow
1. Reproduce the symptom with a minimal live script, not only unit tests.
2. Separate the failure layer:
   - CLI discovery / PATH,
   - Chromium runtime libraries,
   - browser launch,
   - CDP connectivity,
   - Hermes session routing,
   - page-state verification.
3. If local `agent-browser --session` reports success but the live page stays at `about:blank`, test whether direct CDP mode avoids the issue.
4. Prefer fixing the local path inside Hermes before proposing external infrastructure.
5. After the fix, verify with the exact user-facing flow: `navigate -> snapshot -> console/eval`, and optionally one interaction.
6. Run focused browser tests after the live repro is green.

## High-value verification pattern
Use a tiny Python repro through Hermes tool functions:
- `cleanup_all_browsers()`
- `browser_navigate("https://example.com", task_id=...)`
- `browser_snapshot(task_id=...)`
- `browser_console(expression='window.location.href', task_id=...)`
- optional click/type follow-up
- `cleanup_all_browsers()` again

Treat the bug as unresolved if any of these disagree.

If `browser_vision` is the failing layer, add a separate repro for screenshot recovery:
- navigate to a minimal page like `https://example.com`
- run `browser_vision(...)`
- confirm whether the primary capture was blank and whether Chrome fallback recovered a real screenshot/analysis
- keep screenshot-path fixes separate from session-routing fixes in your notes and verification

## Local-mode repair pattern
When local Linux mode has false-success navigation:
1. Check whether Chromium can launch at all.
2. Ensure vendored runtime libraries under `~/.hermes/browser-libs/root` are exposed through `LD_LIBRARY_PATH` for browser subprocesses.
3. If the failure is specifically in `agent-browser` local session mode, bypass that daemon/session path by:
   - launching local headless Chrome directly from Hermes,
   - reserving a loopback debugging port,
   - resolving `/json/version` to a concrete `webSocketDebuggerUrl`,
   - routing browser commands through `--cdp` instead of local `--session`.
4. Store launcher metadata in the session record so cleanup and observability still work.

## Pitfalls
- Do not conclude "fixed" from passing unit tests alone.
- Do not conclude "fixed" from `title` alone when snapshot is empty.
- Do not treat a successful `browser_navigate` followed by `Connection refused` on snapshot/eval as a frontend regression first; check for a stale configured CDP override before reopening app code.
- If the page now renders the shell of a feature (for example a dashboard card/frame) but the interior is empty, stop treating it as a browser-runtime problem first. Inspect the live application payload and compare its exact shape with what the React renderer expects.
- For dashboard-like UIs, verify not only that `message.meta.dashboard` exists, but whether the renderer supports the real grammar form coming from runtime (`section.kind`, `items`, plain-string list items, `{text, meta}` items, and chart sections encoded as `kind='bar_list'` / `kind='pie_list'` with data under `items`). A visible shell with no content often means a contract mismatch, not missing data.
- Distinguish two CDP-override failure classes:
  - unreachable at session creation time -> preflight can degrade immediately to local Chromium;
  - reachable during `navigate` but dead by the next `snapshot` / `eval` -> add runtime recovery, not just preflight health checks.
- For the mid-session case, preserve the last successful URL in session state so local recovery can reopen the page before retrying the failed command.
- When screenshot output is blank but snapshot/URL checks are healthy, fix the screenshot path first and only then interpret the visual result.
- Do not encode transient environment breakage as a permanent skill rule; save the durable repair pattern instead.
- When using local CDP launch, verify that cleanup still terminates the Chrome process.
- If you add a new local-mode path, keep cloud/CDP override behavior untouched.
- If a direct Python repro through `tools/browser_tool.py` is green but the already-running Hermes browser wrapper still returns `about:blank` / empty snapshots, treat that as likely stale host-process state or an old tool session — not immediate proof that the patch failed. Verify with a fresh task/session or restart the long-lived Hermes host before reopening the code.

## Mid-session CDP override recovery
When a configured CDP override is healthy at first but dies between commands:
1. Reproduce with the exact sequence `navigate -> snapshot -> console/eval` on one task id.
2. Confirm whether `_cdp_override_is_reachable(...)` only proves preflight health, not session durability.
3. Detect the runtime failure shape from command results (`CDP WebSocket connect failed`, `Connection refused`, similar transport errors).
4. Recover by replacing the poisoned task session with a local Chromium session.
5. Reopen the last known good URL before retrying the failed command once.
6. Mark the recovered result/session with explicit fallback metadata so later debugging can tell preflight fallback from runtime fallback.

## Wrapper-staleness check
When live verification is mixed:
1. Run the canonical direct repro through the current `tools/browser_tool.py` module.
2. Compare it with the built-in browser-tool path used by the active Hermes session.
3. If they disagree and the direct module path is green, inspect whether a long-lived gateway / browser host process predates the patch.
4. Record the distinction clearly: code-level fix may be done even when the currently running wrapper still serves stale behavior.
5. Only after that decide whether another code patch is needed.

## Local QA fallback when wrapper is unreliable
If local browser verification is explicitly required and the Hermes wrapper shows false-success navigation:
1. Reproduce the failure through `agent-browser --session` with `open`, then `eval window.location.href`, then `snapshot -c`.
2. Treat `open -> target URL` followed by `about:blank` / `(empty page)` as a session-persistence diagnosis, not as final evidence about the app.
3. Switch to an independent browser path for product QA (for example Playwright or another direct automation route) so app testing can continue while browser-layer diagnosis remains separate.
4. Keep the reporting split explicit:
   - browser-wrapper state;
   - independent app-QA result;
   - whether the app itself still has a real bug.
5. Do not mark runtime verification complete merely because the wrapper failure is explained; the app still needs a live smoke pass.

## What to preserve when patching
- Existing cloud provider behavior.
- Existing `BROWSER_CDP_URL` / config override semantics.
- Hybrid routing logic for private URLs.
- Browser command environment preparation (`PATH`, library paths, idle timeout).

## References
- `references/local-cdp-live-navigation-fix.md` — concrete reproduction, diagnosis, and repair pattern for false-success local navigation.
- `references/cdp-override-mid-session-recovery.md` — diagnosis and recovery pattern for CDP overrides that survive preflight but die before the next browser command.
- `references/dashboard-shell-no-data-contract-check.md` — when the browser can show the dashboard container but the content is empty: inspect live payload shape and align renderer expectations to runtime grammar.
