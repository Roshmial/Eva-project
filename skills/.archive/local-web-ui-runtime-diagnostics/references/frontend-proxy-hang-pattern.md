# Frontend proxy hang pattern for local-first web UIs

Use this when a local web UI "does not open" but the failure boundary is unclear.

## Symptom cluster

Typical signals:
- `ss` shows the frontend port (for example `8790`) as listening;
- `curl http://127.0.0.1:8790/` hangs or times out instead of returning HTML;
- browser navigation times out or the page appears blank/stuck;
- backend API on `8788` still answers `service-info` with `200`.

This combination usually means the frontend process exists but is not healthy enough to serve requests.

## What to check

1. Confirm backend first.
- Example: `curl http://127.0.0.1:8788/api/service-info`
- If backend is healthy, do not start by patching auth or app boot.

2. Probe the frontend origin directly.
- Example: `curl http://127.0.0.1:8790/`
- A timeout here is stronger evidence than "process exists".

3. Read the frontend log.
- Look for request-handler exceptions such as `BrokenPipeError`.
- In a single-threaded Python server/proxy, one bad client interaction can leave the origin effectively wedged for future requests.

4. Verify whether the server implementation is single-threaded.
- `socketserver.TCPServer` is a red flag for this class of local proxy.

## Durable fix pattern

For lightweight Python local proxies/static servers:
- switch from `socketserver.TCPServer` to `socketserver.ThreadingTCPServer`;
- set `daemon_threads = True`.

Why this helps:
- one stalled client or broken pipe no longer blocks the entire origin;
- the fix addresses runtime resilience, not just the latest crash.

## Related origin/CORS check

A separate but adjacent failure pattern is hostname mismatch:
- UI opened on `http://localhost:8790`;
- backend CORS only allows `http://127.0.0.1:8790`;
- frontend config hard-codes the other hostname.

In local-first contours, verify all three together:
- actual browser origin;
- frontend-configured backend URL;
- backend `Access-Control-Allow-Origin` behavior.

Prefer frontend config derived from `window.location.hostname` when the only difference is `localhost` vs `127.0.0.1`.

## Acceptance

Consider the incident resolved only when:
- `8788` responds;
- `8790` returns HTML quickly;
- browser navigation opens the UI;
- the login screen shows normal service status instead of `Failed to fetch`.