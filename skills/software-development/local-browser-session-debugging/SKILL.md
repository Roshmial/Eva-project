---
name: local-browser-session-debugging
description: Diagnose and fix Hermes local browser session issues, especially when navigation claims success but later commands hit about:blank or an empty page.
---

# Trigger

Use this when debugging Hermes browser tooling on local or local-first web apps, especially when:

- `browser_navigate` reports success but `browser_snapshot` returns `(empty page)`.
- `browser_console(expression='window.location.href')` returns `about:blank` after a supposedly successful local navigation.
- manual `agent-browser open <url>` appears to work, but follow-up `snapshot` or `eval` reads a blank document.
- local frontend QA is blocked because browser tools cannot hold page state across commands.

# Goal

Separate three failure classes cleanly:

1. the local app itself is broken;
2. the Hermes browser wrapper is routing commands to the wrong session/state;
3. `agent-browser` local session mode is losing state between commands and needs a CDP-backed path.

# Workflow

1. Reproduce through the actual Hermes browser wrapper first.
   - Run the real `browser_navigate` / `browser_snapshot` / `browser_console` path, not just a manual browser test.
   - Check four things together:
     - navigate return payload;
     - snapshot text;
     - `window.location.href`;
     - a short `document.documentElement.outerHTML` sample.

2. Confirm whether the bug is in the wrapper or in the underlying CLI.
   - Re-run the same flow manually with `agent-browser` using the same session semantics the wrapper uses.
   - Test the exact sequence:
     - `open <url>`
     - `snapshot -c`
     - `eval window.location.href`
   - If `open` reports the target URL but later commands see `about:blank`, the problem is in local browser session persistence, not just the app.

3. Verify the issue is specific to local-session routing.
   - Check whether the current browser path is using `--session` local mode versus `--cdp`.
   - Inspect whether session metadata preserves a usable `cdp_url` for follow-up calls.
   - If local pages are driven through plain `--session` and state is lost between commands, plan a CDP-backed local path.

4. Verify the live target before chasing browser state.
   - If docs, notes, or prior session outputs mention a localhost URL or port, treat them as hints, not proof.
   - Check which local port is actually listening now before concluding the app is down or the wrapper is wrong.
   - For screen-specific tasks, separate three states explicitly: target screen is open; only the login shell is open; the app is unreachable.

5. Prefer a CDP-backed fix for local pages.
   - Launch a local Chromium-family browser with `--remote-debugging-port`.
   - Wait for `/json/version` and capture `webSocketDebuggerUrl`.
   - Store that `cdp_url` in session state so subsequent snapshot/eval/click paths use the same live browser.
   - Keep the fix local-first: do not jump to external browser SaaS when the local stack should handle localhost pages.

6. Guard against stale CDP override state.
   - If `browser_navigate` appears to work but `browser_snapshot` / `eval` then fail with `CDP WebSocket connect failed` or `Connection refused`, suspect a dead `browser.cdp_url` / `BROWSER_CDP_URL` override.
   - Health-check the configured override via `/json/version` before creating a CDP session.
   - If the override is unreachable, degrade to a local Chromium session immediately instead of creating a poisoned session where only the first step appears successful.
   - Verify with the exact sequence `navigate -> snapshot -> eval`, not navigate alone.

7. When the browser wrapper is suspect, prove the app separately.
   - Reproduce the wrapper failure through `agent-browser --session` directly: `open <url>` followed by `eval window.location.href` and `snapshot -c`.
   - If that path shows `about:blank` / `(empty page)`, treat it as evidence about session persistence, not immediate proof that the app is blank.
   - Then verify the app through an independent browser path (for example Playwright or another direct browser automation route) before concluding the frontend itself is broken.
   - If the independent browser exposes a real product bug, keep the task open as app QA/debugging work; do not let the wrapper bug mask the application bug.
   - Before using token injection or session-restore shortcuts in that independent path, inspect the frontend source for the actual storage key / bootstrap trigger instead of guessing common keys like `token` or `hermes_token`. A wrong localStorage key creates a false negative that looks like a broken authenticated boot.
   - If typed input appears to succeed but submit behaves as if fields are empty, verify the DOM values explicitly. `browser_type` success is not enough evidence on flaky local backends; compare the input element `.value` in the page context and, for diagnosis only, fall back to direct value assignment plus `input` / `change` events to separate browser-tool typing issues from real app bugs.

6. Add cleanup from the start.
   - If the fix launches a local CDP browser, also persist enough metadata to terminate it and remove its profile dir during cleanup.
   - Update both per-session cleanup and `cleanup_all_browsers` expectations.

6. Only after browser runtime is trustworthy, continue UI QA.
   - Do not treat file inspection and `curl` as a full substitute for live browser verification when the task is explicitly frontend UX/UI polish.
   - Resume frontend review only after `navigate -> snapshot -> console` works end-to-end on the target page.

# What to capture during diagnosis

Record:

- exact local URL used for repro;
- whether navigate returned success;
- whether snapshot was empty;
- what `window.location.href` returned;
- whether manual `agent-browser` reproduced the same state drift;
- whether the session path was `--session` or `--cdp`.

Keep session-specific transcripts in `references/` rather than bloating the main skill.

# Pitfalls

- Do not conclude "frontend is broken" from `(empty page)` alone.
- Do not conclude "browser is fine" from a successful `open` result alone; always inspect follow-up state.
- Do not treat a blank screenshot as proof of an empty page when snapshot/URL data disagree. A primary CDP capture can be blank even when the page rendered.
- When the primary screenshot path returns a blank frame, retry with a temporary Chrome capture at the current URL before escalating.
- Do not stop at a speculative fix. Verify with real `navigate -> snapshot -> console` output.
- Do not encode temporary environment breakage as a durable rule. Capture the debugging pattern, not a permanent negative claim.

# Verification

A real fix should show all of the following on the same local page:

- `browser_navigate` returns success and the expected URL;
- `browser_snapshot` returns non-empty content;
- `browser_console(expression='window.location.href')` returns the actual page URL, not `about:blank`;
- a short DOM sample contains expected page markup;
- cleanup removes any extra local browser process/profile created by the fix.

# References

- `references/local-ui-wrapper-vs-app-qa.md` — как отделять ложную пустую local browser-session от реального бага приложения и не останавливать app QA слишком рано.
- `references/about-blank-local-session-repro.md` — condensed reproduction pattern and debugging cues for the `open -> snapshot/eval -> about:blank` failure mode.
- `references/local-auth-bootstrap-false-negatives.md` — как не спутать browser-runtime проблему с ложным auth-boot провалом из-за неверного localStorage key или некорректной token-injection проверки.
- `references/local-screen-open-vs-login-state.md` — как для запросов вида «открой экран X» разделять реальное открытие целевого экрана, только login shell и auth-блокер при одновременной browser-session деградации.
- `references/user-space-fontconfig-linux.md` — Linux workaround без root: как стабилизировать headless Chromium/Playwright/Hermes CDP через локальный `fontconfig` и шрифты в домашнем каталоге.
- `references/stale-cdp-override-and-blank-screenshot.md` — как распознать мёртвый CDP override и что делать, когда `browser_vision` даёт пустой кадр при живой странице.
