# about:blank after local navigate: repro pattern

Use this note when Hermes browser tools claim navigation succeeded on a local page but later commands behave as if the page is blank.

## High-signal symptom bundle

All of these together strongly indicate local session-state loss:

- `browser_navigate('http://127.0.0.1:<port>/...')` returns success;
- returned URL matches the local page;
- immediate `browser_snapshot` returns `(empty page)`;
- `browser_console(expression='window.location.href')` returns `about:blank`;
- DOM sample is `<html><head></head><body></body></html>` or equivalent.

## Best reproduction order

1. Reproduce through `tools/browser_tool.py` first.
2. Then manually run the underlying `agent-browser` sequence with the same session mode:
   - `open <url>`
   - `snapshot -c`
   - `eval window.location.href`
3. Compare outputs.

If manual `open` reports the local URL but later `snapshot` / `eval` still land on `about:blank`, the issue is not only in the high-level tool wrapper; the local session model itself is suspect.

## Interpretation

Treat this as a session persistence / routing issue before treating it as a frontend rendering issue.

Common likely direction:

- local navigation path uses plain `--session`;
- follow-up commands do not reconnect to the same effective page state;
- local pages need a CDP-backed path that preserves a concrete browser endpoint.

## Fix direction

Prefer a local CDP-backed browser launch for localhost/LAN pages:

- start Chromium-family browser with `--remote-debugging-port`;
- wait for `/json/version`;
- save `webSocketDebuggerUrl` as `cdp_url` in session metadata;
- route follow-up snapshot/eval/click commands through that stable browser endpoint;
- add cleanup for spawned browser process and profile dir.

## What not to do

- Do not keep doing frontend UX review as if browser QA were valid.
- Do not record a permanent claim that "browser tools are broken".
- Do not stop at `open` success; always inspect follow-up state.
