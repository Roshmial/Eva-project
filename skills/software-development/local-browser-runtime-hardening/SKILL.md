---
name: local-browser-runtime-hardening
description: Stabilize and verify local Playwright/Hermes browser runtime on Linux, especially headless Chromium/CDP setups without root access.
triggers:
  - Playwright or Hermes browser tools are flaky on localhost
  - Headless Chromium opens then crashes, aborts, or returns blank/about:blank states
  - Browser smoke fails intermittently and the root cause may be runtime vs app logic
  - Need a local-first browser verification path without adding new infrastructure
---

# Local browser runtime hardening

Use this skill when local browser automation is unreliable and you need to separate runtime instability from real product defects.

## Goal

Get to a stable, repeatable local browser path for:
- Playwright smoke tests
- Hermes browser tools via CDP
- localhost UI verification

without introducing external SaaS or new long-lived infrastructure.

## Core principle

First stabilize the browser runtime itself. Only after that trust UI failures as product failures.

If browser behavior is flaky, do not immediately patch frontend/backend logic based on noisy smoke results.

## Recommended sequence

1. Confirm whether the issue is runtime or product.
   - Check whether backend/API flows succeed directly.
   - Check whether the browser can reliably open the page, keep the page alive, and preserve session state.

2. Prefer the existing local stack.
   - Reuse Playwright-managed Chromium already present in cache before introducing a new browser.
   - Reuse Hermes browser tools through CDP once Chromium is stable.

3. On Linux without root, suspect missing fontconfig/fonts early.
   - Headless Chromium may start but behave unstably if fontconfig and base fonts are absent.
   - Symptoms may look unrelated: SIGABRT, page/context closing on goto/reload, unstable CDP attach, inconsistent UI smoke.

4. Build a user-space runtime before attempting broad UI fixes.
   - Download and unpack fontconfig and basic fonts into a user-owned directory.
   - Set environment variables for browser launches:
     - `FONTCONFIG_PATH`
     - `FONTCONFIG_FILE`
     - `XDG_DATA_DIRS`
   - Keep using the existing Chromium binary if it becomes stable after that.

5. Verify in layers.
   - Layer A: plain browser open of localhost page
   - Layer B: authenticated boot with token preseeded before page load
   - Layer C: Hermes browser tools through CDP
   - Layer D: full UI smoke across target screens

6. If UI smoke still fails, isolate with direct API reproduction.
   - Reproduce the same action outside the browser.
   - If API fails too, it is not a browser/UI-only issue.
   - If API passes and browser fails, stay focused on runtime or frontend timing.

## High-value techniques

### 1. Preseed auth token before first load

Prefer `addInitScript`/preload token injection before the first page load over setting localStorage after load plus `reload()`.

Reason:
- avoids introducing reload-related runtime noise
- gives a cleaner authenticated boot path
- makes it easier to distinguish app boot issues from browser instability

### 2. Treat browser events as evidence, not assumptions

Capture at least:
- console errors
- page errors
- HTTP responses with status >= 400
- visible DOM state after boot

This prevents false conclusions like “screen is broken” when the page actually never finished booting.

### 3. Use direct multipart API checks for file-upload flows

When chat/file upload smoke partially succeeds in UI:
- reproduce the same request directly against the API
- verify whether the response is `201`/`200` or `500`

This is especially useful when the UI appears to save some side effects while still surfacing an error.

### 4. For SQL/DB write flows using `RETURNING`, consume the returned row immediately

Pitfall:
- after `INSERT ... RETURNING id`, do not delay `fetchone()` until after another `execute()` on the same connection/cursor flow
- otherwise the returned row may be lost or become inconsistent in downstream logic

Safer pattern:
- execute insert with `RETURNING`
- immediately read `fetchone()[0]`
- only then run follow-up updates/selects

Use this suspicion early when a handler writes data successfully but crashes while building the response payload.

## Linux no-root hardening path

When root package installation is unavailable:

1. Create a user-space runtime directory.
2. Download required `.deb` packages without installing system-wide.
3. Extract them under the user-owned runtime path.
4. Point browser launches to that runtime using env vars.
5. Keep the rest of the stack unchanged.
6. If the user or project already has a wrapper like `scripts/browser_runtime_env.sh`, standardize on it instead of re-solving the same `.so` chain ad hoc in each session.

This approach is often enough to stabilize headless Chromium for both Playwright and Hermes CDP usage.

### Durable path rule for repeated Linux no-root work

If you had to unpack shared libraries once to get Chromium running, do not keep re-creating throwaway overlays under random workspace paths on later sessions.

Prefer a durable user-owned runtime path and a single launch wrapper, for example:
- `~/.hermes/browser-libs/root`
- `~/.local/browser-runtime/root`
- repo wrapper script such as `scripts/browser_runtime_env.sh`

Session rule:
- first look for the existing wrapper/runtime tree;
- reuse it for `chrome-headless-shell --version`, Playwright probes, and UI smoke;
- only fall back to fresh extraction when the durable runtime is genuinely absent or incomplete.

This prevents the exact failure mode where the agent repeatedly burns time re-downloading the same `libnspr4.so`/Chromium dependency chain instead of moving straight to product acceptance.

### Practical Ubuntu/Debian pattern for Playwright Chromium

If `ldd` on Playwright `chrome-headless-shell` shows many missing libs, do not start by guessing app bugs.

Use a layered runtime check:
1. Run `ldd <chrome-headless-shell> | grep 'not found'` to list missing shared libraries.
2. Download only the needed runtime packages with `apt download ...`.
3. Extract them with `dpkg-deb -x` into a user-owned runtime tree.
4. If Chromium starts and then dies later on page open/reload, add `fontconfig`, `libfontconfig1`, and base fonts (`fonts-dejavu-core` at minimum) to the same runtime tree.
5. Export at launch time:
   - `LD_LIBRARY_PATH`
   - `FONTCONFIG_PATH`
   - `FONTCONFIG_FILE`
   - `XDG_DATA_DIRS`
6. Verify in two short steps before any full smoke:
   - `chrome-headless-shell --version`
   - a minimal Playwright script that opens the target localhost URL and survives a short `waitForTimeout()`.

This sequence separates browser-runtime repair from product debugging and avoids wasting time on frontend/backend fixes while Chromium itself is still unstable.

See also: `references/ubuntu-user-space-playwright-runtime.md`.

## Verification checklist

A runtime is considered stabilized only when all of the following are true:

- plain page open on localhost succeeds repeatedly
- authenticated boot succeeds
- no critical browser console/page errors during smoke
- Hermes browser tools can `navigate -> snapshot -> console` on the same localhost app
- full UI smoke works on target screens
- if file upload is in scope, direct API reproduction also succeeds

## Common pitfalls

- Treating a wrong localStorage key as a product auth bug
- Assuming typed input failures in browser tooling mean the app input itself is broken
- Debugging frontend rendering before confirming that runtime and API are stable
- Trusting a partial UI success when the API may still be returning `500`
- Restarting app logic repeatedly without confirming the running server actually picked up the new code

## Response strategy for future sessions

When this class of issue appears:
- first state whether the evidence points to runtime, product, or mixed causes
- explicitly separate facts from hypotheses
- avoid declaring UI acceptance complete until browser runtime and direct API checks both support it

## References

- `references/user-space-fontconfig-and-multipart-smoke.md` — concrete Linux no-root runtime stabilization pattern and multipart/API verification notes from a real Hermes Web MVP case.
