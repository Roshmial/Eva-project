# Persistent local CDP + blank screenshot on Linux

Use this reference when the symptom is split across two layers:

1. Hermes browser tools drift to `about:blank` or `(empty page)` after a seemingly successful navigation.
2. Direct CDP control works, but screenshots or `browser_vision` are still blank / almost blank.

## Durable diagnosis pattern

### Layer 1 — wrapper/session routing

Failure shape:
- `browser_navigate('https://example.com')` reports success and even returns title `Example Domain`.
- But follow-up Hermes checks disagree:
  - `browser_console` shows `about:blank`, or
  - `browser_snapshot` is empty.

What to prove:
- Query the running local CDP endpoint:
  - `/json/version`
  - `/json/list`
- Re-run the same page through direct CDP:
  - `agent-browser --cdp <ws> --json open <url>`
  - `agent-browser --cdp <ws> --json eval 'window.location.href'`
  - `agent-browser --cdp <ws> --json snapshot -c`

Interpretation:
- If direct `--cdp` is green but Hermes browser tools still drift, the problem is not the page and not generic Chromium reachability.
- The durable fix is to pin Hermes to the same local endpoint with persistent config:
  - `browser.cdp_url: http://127.0.0.1:<port>`

This is stronger than relying on transient session metadata or one-off connect state.

### Layer 2 — screenshot/rendering runtime

Failure shape:
- `browser_console` and `browser_snapshot` are correct.
- But direct screenshot capture or `browser_vision` is blank / nearly blank.

Interpretation:
- This is not evidence that the page is empty.
- Treat screenshot capture as a separate Linux runtime/rendering problem.

## Local-first repair pattern

For a dedicated local Chrome CDP service, prefer fixing the service runtime instead of inventing app-level explanations.

Useful environment for a user-space runtime:
- `FONTCONFIG_PATH=/home/hermes/.local/browser-runtime/root/etc/fonts`
- `FONTCONFIG_FILE=/home/hermes/.local/browser-runtime/root/etc/fonts/fonts.conf`
- `XDG_DATA_DIRS=/home/hermes/.local/browser-runtime/root/usr/share`
- `LD_LIBRARY_PATH=/home/hermes/.hermes/browser-libs/root/usr/lib/x86_64-linux-gnu`

Useful hardening flags for the service command line:
- `--no-sandbox`
- `--disable-dev-shm-usage`

After changing the service:
1. reload/restart the user service;
2. verify `/json/version` again;
3. repeat the same direct CDP open/eval/snapshot flow;
4. then re-run Hermes browser tools.

## Minimum acceptance standard

Do not call it fixed until all of these are green on the same page:
- `browser_navigate`
- `browser_console(window.location.href)`
- `browser_snapshot`
- `browser_vision` or direct screenshot capture

A green navigate alone is not enough.
A green DOM-only check is not enough when the original bug included blank screenshots.
