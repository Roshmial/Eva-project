# Local UI QA when Hermes browser wrapper loses page state

## When this reference helps
Use this when:
- `browser_navigate()` reports success on a localhost page;
- `browser_snapshot()` returns `(empty page)`;
- `browser_console('window.location.href')` returns `about:blank`;
- you still need to test the actual app flow instead of stopping at browser-layer diagnosis.

## Minimal classification pattern
1. Reproduce through Hermes browser tools.
2. Reproduce again through direct `agent-browser --session` commands:
   - `open <url>`
   - `eval window.location.href`
   - `snapshot -c`
3. If `open` reports the target URL but follow-up commands see `about:blank`, classify it as browser session-persistence trouble.
4. Do not conclude the app is blank from that alone.
5. Continue product QA through an independent browser path.

## Reporting split
Keep three outcomes separate:
- wrapper/browser session state;
- raw app availability (`curl`, service-info, setup-status, static HTML delivery);
- real browser app behavior under independent automation.

## Session lesson captured here
In this session the fallback path exposed two distinct findings:
- browser-wrapper / `agent-browser --session` state drift to `about:blank` after a nominally successful local `open`;
- a separate app-level login-flow bug where the UI sent an auth request with empty email/password fields.

The durable lesson is the separation pattern:
- wrapper failure can be real,
- app bug can also be real,
- one must not be used to explain away the other.
