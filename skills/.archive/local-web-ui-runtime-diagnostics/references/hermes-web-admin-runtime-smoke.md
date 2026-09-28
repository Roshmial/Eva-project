# Hermes Web admin runtime smoke pattern

Use this reference when Hermes Web or a similar local-first admin UI has these moving parts:
- backend API on a local port;
- frontend static/proxy server on another local port;
- optional flaky built-in browser wrapper/CDP path;
- login screen plus hidden authenticated shell.

## Practical sequence

1. Verify backend first.
   - Example: `GET /api/service-info`
   - Then verify the exact admin endpoints needed for the smoke.
2. Verify the frontend origin itself.
   - Example: `curl http://127.0.0.1:8790/`
   - If the TCP port listens but HTTP hangs with no bytes, restart the frontend server/proxy process.
3. If the built-in browser wrapper is flaky, use an independent Playwright probe.
4. If Playwright Chromium complains about missing shared libs, reuse Hermes user-space browser libs:
   - `LD_LIBRARY_PATH=$HOME/.hermes/browser-libs/root/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}`
5. Authenticate directly against the backend API.
   - For Hermes Web in this session, backend auth succeeded independently of the UI login form.
6. Inject the real token into localStorage and reload.
   - Hermes Web storage key used here: `hermes_web_mvp_token`
7. Inspect the shell-transition markers before testing feature screens:
   - `#loginScreen`
   - `#appShell`
   - `#adminNavBtn`
   - `#adminChartGranularity`

## Interpretation guide

Observed pattern worth reusing:
- backend auth = OK;
- frontend origin = OK after restarting the hung frontend server;
- token present in localStorage after reload = OK;
- admin DOM nodes present = OK;
- login screen still visible and app shell still hidden = frontend boot / restore-session visibility issue.

This pattern is valuable because it prevents a false conclusion that "admin charts are broken" when the actual issue is earlier in authenticated shell activation.

## Session-specific Hermes Web details

- frontend origin that mattered: `http://127.0.0.1:8790/`
- backend origin that mattered: `http://127.0.0.1:8788/api`
- frontend server process was able to hang while still listening on the port; TCP connect alone was not sufficient proof of health.
- independent Playwright with user-space browser libs was good enough to separate browser/runtime issues from app boot issues.
