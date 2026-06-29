---
name: split-runtime-contour-verification
description: Verify and operate split-host web runtimes without mixing dev/prod contours or editing the wrong surface. Use before frontend/backend fixes when services are distributed across different hosts or ports.
---

# When to use

Use this skill when a web application is split across multiple runtime contours, for example:
- dev and prod live on different host/port combinations
- frontend and backend are on different hosts in prod
- the same repository is reused by multiple systemd units
- there is a risk of editing the right code on the wrong machine, or the wrong code on the right machine

This is especially important for Misha-style Hermes Web work, where:
- dev may be fully colocated on one host
- prod backend may live on one host
- prod frontend may live on another host
- conclusions from one contour must not be transferred to another without direct verification

# Core rule

Do not start with SSH assumptions.
First determine whether the current machine is already one of the target hosts.
Then determine which exact unit, working directory, env override, and backend target correspond to the requested surface.

# Required sequence

1. Confirm contour before editing anything.
   - Write down the intended target in concrete terms: host, port, role.
   - Separate:
     - dev frontend/backend/aux
     - prod frontend/backend/aux
   - If the user gave an explicit contour map, treat it as authoritative and preserve it.

2. Check whether you are already on the target machine.
   - Before attempting remote access, verify whether the named host is actually the current server.
   - Do not burn time on SSH to the current machine.
   - If the target host is current-local, work locally first.

3. Resolve the runtime from systemd, not from repo guesses.
   - Inspect the exact unit for the requested port.
   - Read:
     - unit file
     - drop-in overrides
     - WorkingDirectory
     - ExecStart
     - explicit environment overrides
   - For frontend units, verify the backend target override, for example a backend base URL.
   - Do not stop at `WorkingDirectory` and service name. On the target host, verify the live code payload too:
     - file hash or line count of the served entrypoint;
     - a distinctive code fragment near the suspected route or DB layer;
     - that the remote file content matches the local tree you think you deployed.
   - Reason: the same unit/path can still run a stale copy of the file, and the symptom will look like a runtime/env problem even though the real defect is old code content on disk.

4. Confirm live path from the runtime surface.
   - For frontend: check the live port and verify the proxied `/api/*` path answers from the expected backend.
   - For backend: check health/service-info endpoints directly on the backend host/port.
   - Prefer live runtime evidence over assumptions from source layout.

4.0 Before drawing conclusions from DB inspection, prove which data contour the live UI is actually using.
   - Do not assume the named prod PostgreSQL host is the source of truth for the visible UI.
   - Verify whether the current frontend/runtime is backed by:
     - local DuckDB under the frontend/backend service working tree;
     - remote PostgreSQL;
     - another split runtime entirely.
   - If a user reports "UI still broken" after a DB cleanup, first confirm that the inspected DB is the one serving that UI.
   - Treat "fixed in PostgreSQL on host A" and "confirmed in UI on host B" as different claims until the contour link is proven.

4.1 If the change touched backend routing, structured-response logic, policy loaders, or other nontrivial server behavior, verify the deploy payload includes adjacent runtime assets, not just the main entrypoint.
   - Do not assume copying `app.py` or rebuilding the frontend is enough.
   - Check for required neighbor files such as:
     - `policies/*.json`
     - prompt/config payloads
     - scripts invoked by the service at runtime
     - fixture or contract files loaded from relative paths
   - After rollout, verify both:
     - the new code markers are present on the target host; and
     - the referenced support files actually exist at the expected relative paths.
   - If the service fails after an otherwise clean code sync, inspect logs immediately for missing-file startup errors before assuming a bad restart or environment issue.

4.2 Verify the effective runtime environment, not only unit drop-ins.
   - If the service starts via a shell wrapper (`run_*.sh`, `runtime_env.sh`, `source ~/.hermes/.env`, etc.), inspect those files before trusting `systemctl cat` alone.
   - Read the live process environment from `/proc/$PID/environ` for the running service when a header, origin, target URL, or model route does not match the unit-level expectation.
   - Treat `systemd` Environment lines and shell-sourced `.env` files as separate configuration layers; the shell layer may silently override the apparently correct unit/drop-in values.
   - When the symptom appears only after restart, suspect that startup-time env composition is reintroducing an older local-only setting.

5. If the user-visible symptom is raw HTML/SVG/error-page text, classify the leak source before blaming the web contour.
   - Separate at least three possibilities:
     - frontend proxy / browser-facing web contour
     - backend application response
     - Hermes/gateway/provider error propagation that later got delivered into chat
   - Use payload signature as a clue:
     - full HTML page with title/body may be upstream provider or proxy
     - SVG/path fragments inside a chat reply may come from a provider error page that was stringified and re-sent by the agent path
   - Before attributing the symptom to `frontend -> backend`, inspect the agent/gateway logs for the same fragment or for provider-side errors such as Cloudflare / permission / HTML error pages.
   - Only call it a frontend-contour bug if the same payload can be reproduced from the live web surface or proxy path itself.

6. Verify that the live frontend is serving the intended code.
   - Confirm via live source or built asset markers that the running frontend includes the expected strings/features.
   - Examples of useful markers:
     - UI control ids
     - feature labels
     - new request fields
     - CSS selectors for the changed layout

6. Only after contour verification, make edits.
   - Edit the surface that actually serves the requested environment.
   - Rebuild/restart only the unit for that contour.
   - Re-check live endpoints and UI markers after restart.

# Pitfalls

- Pitfall: assuming a named host is remote when it is actually the current machine.
  - Fix: verify current host role first.

- Pitfall: treating a repo path as proof of the active runtime.
  - Fix: derive runtime from systemd unit + WorkingDirectory + ExecStart + override env.

- Pitfall: moving frontend conclusions from one contour to another.
  - Fix: confirm the exact serving port and backend proxy target for the requested environment.

- Pitfall: seeing HTML/SVG garbage in chat and immediately blaming the frontend proxy.
  - Fix: first determine whether the garbage is reproducible from the web surface itself or whether it originated in Hermes/gateway/provider error propagation.
  - Signature to watch for: provider HTML pages or SVG/path fragments that appear in logs and then get echoed into Telegram/chat, even when the split frontend/backend contour is healthy.

- Pitfall: editing backend host when the requested fix is on a split frontend host.
  - Fix: for split prod, treat frontend and backend as separate delivery surfaces.

- Pitfall: using prior dev findings as evidence about prod.
  - Fix: verify prod directly with live HTTP and unit wiring.

# Minimum verification checklist

- contour map explicitly restated
- target host role confirmed
- correct unit file identified
- correct override file identified
- correct WorkingDirectory identified
- correct backend target confirmed
- live HTTP on requested port responds
- running frontend/backend shows expected markers after change

# User-specific note

For Misha, contour mistakes are high-cost because they create fake progress. When working on Hermes Web or similar split runtimes, prefer a short, direct answer that explicitly states:
- which host/port was the real target
- which unit serves it
- which backend it points to
- what was actually changed there

# References

- See `references/runtime-env-override-vs-systemd.md` for the specific pattern where a shell-sourced `.env` silently overrides correct-looking systemd drop-ins and breaks public CORS/origin behavior after restart.
- See `references/hermes-web-contour-pitfalls.md` for a compact example of the dev/prod split pattern and the verification cues that caught the wrong-host mistake.
- See `references/chat-error-leak-triage.md` for the fast triage pattern when HTML/SVG garbage appears in Telegram/chat and may come from agent/provider error propagation rather than the live web contour.
- See `references/frontend-proxy-backend-base.md` for the Hermes Web MVP React pattern where `HERMES_WEB_FRONTEND_BACKEND_BASE` controls the frontend `/api/*` proxy target and must be set in the frontend systemd unit when frontend and backend are on different hosts.
- See `references/deploy-payload-adjacent-assets.md` for the rollout pattern where the main backend file is updated correctly but the service still fails because a newly required adjacent policy/config file was not deployed with it.
- See `references/ui-db-contour-split.md` for the specific case where a live UI looked like "prod on PostgreSQL" from the outside but was actually served from a separate DuckDB-backed runtime contour.
