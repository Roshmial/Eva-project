# Local CDP live navigation fix

## Symptom
Local page navigation could return formal success while the browser state stayed on `about:blank`:
- `browser_navigate()` returned `success: true`
- `browser_snapshot()` returned `(empty page)`
- `browser_console('window.location.href')` returned `about:blank`

## Durable repair pattern
1. Reproduce with a direct Python script that imports `tools.browser_tool`.
2. Do not trust local `--session` mode alone when it reports success without page state.
3. Launch local Chromium directly under Hermes and route the session through an explicit CDP URL.
4. Search for Chromium both in system locations and in Playwright cache.
5. Merge vendored browser runtime libraries into `LD_LIBRARY_PATH` for the launched browser process.
6. Cache snapshot refs and verify at least one follow-up action in the same session.
7. Ensure cleanup kills the local browser pid, removes the temporary profile dir, and clears cached refs.

## Verification standard
Treat the fix as real only when all checks agree:
- navigate returns success;
- snapshot is non-empty and shows expected elements;
- console confirms the real page URL;
- at least one follow-up action such as click still works.

## Important operational nuance
If the direct `tools/browser_tool.py` repro is green but the already-running built-in Hermes browser wrapper still returns stale `about:blank` behavior, suspect long-lived host-process state first. Re-open with a fresh task/session or restart the long-lived Hermes host before making another code patch.
