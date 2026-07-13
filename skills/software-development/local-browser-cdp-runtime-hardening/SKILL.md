---
name: local-browser-cdp-runtime-hardening
description: Diagnose and fix Hermes local browser/CDP contours when navigate, snapshot, console, and vision disagree or screenshots render blank.
---

# Local browser CDP runtime hardening

Use this when Hermes browser tools on a local Linux host behave inconsistently, especially after updates or runtime changes.

## Triggers

Load this skill when any of these appear:
- `browser_navigate()` reports success, but later checks still show `about:blank`.
- `browser_snapshot()` is empty or mismatched even though navigate succeeded.
- `browser_console('window.location.href')` disagrees with `browser_navigate()`.
- direct CDP open/eval/snapshot work, but `browser_vision()` or screenshots are blank/white.
- a dedicated local Chrome/Chromium CDP service already exists and Hermes may not be explicitly using it.

## Core idea

Split the problem into two layers:

1. routing / attachment layer
- Are Hermes browser tools attached to the intended CDP browser/session?

2. rendering runtime layer
- Even if DOM and eval work, can the local headless browser render screenshots correctly?

Do not treat these as the same bug.

## Preferred workflow

1. Confirm whether the host already has a local CDP endpoint.
- Check for a dedicated systemd user service or known local Chrome/Chromium process.
- If a stable CDP endpoint already exists, prefer reusing it instead of introducing new browser infrastructure.

2. Probe the CDP backend directly.
- Use a direct CDP / `agent-browser --cdp ...` smoke path.
- Verify open, eval, and snapshot on a simple page such as `https://example.com`.

3. If direct CDP works but Hermes tools disagree, hard-pin Hermes to that backend.
- Set `browser.cdp_url` in `~/.hermes/config.yaml` to the local discovery endpoint, for example `http://127.0.0.1:9224`.
- Re-check via Hermes browser tools.

4. If DOM/text checks work but screenshots are blank, treat it as a local runtime/rendering issue.
- Prefer user-space font/runtime repair before external browser services.
- Add fontconfig environment variables and library path to the local CDP browser service.
- Add `--no-sandbox --disable-dev-shm-usage` if the current host/runtime needs it.

## Verification standard

Do not stop at “browser launched” or a single successful navigate.

A fix counts only when all four layers are green:

1. `browser_navigate()`
- returns success for a known page

2. `browser_console()`
- `window.location.href` matches the intended page
- `document.title` matches
- ready state is sane

3. `browser_snapshot()`
- returns non-empty, human-meaningful content matching the page

4. `browser_vision()`
- shows the actual rendered page, not a blank/white frame

## Common pitfall patterns

### Pattern A: navigate says success, live tab still wrong

Symptoms:
- `browser_navigate()` returns expected title/url
- `browser_console()` still shows `about:blank` or another page
- `browser_snapshot()` is empty or mismatched

Interpretation:
- likely routing/session-attachment drift, not necessarily site/network failure

Fix:
- explicitly configure `browser.cdp_url` to the intended local CDP endpoint
- then re-run the full 4-layer verification

### Pattern B: snapshot/eval are correct, screenshots are blank

Symptoms:
- direct CDP `open/eval/snapshot` succeed
- Hermes `browser_console()` and `browser_snapshot()` are correct
- screenshot-based tools still show a white/blank image

Interpretation:
- likely local Linux rendering/font/runtime issue, not navigation logic

Fix:
- add user-space font runtime env to the CDP browser service:
  - `FONTCONFIG_PATH`
  - `FONTCONFIG_FILE`
  - `XDG_DATA_DIRS`
- include `LD_LIBRARY_PATH` for browser libs when applicable
- add `--no-sandbox --disable-dev-shm-usage` if required by the host

## Local-first decision rule

Prefer this order:
1. reuse the existing local CDP Chrome/Chromium service
2. explicitly wire Hermes to it with `browser.cdp_url`
3. harden the local runtime environment
4. only then consider more complex or external browser backends

## References

- `references/local-cdp-override-and-font-runtime.md` — concrete working fix pattern with local CDP override, systemd user service env, and verification sequence.
