# User-space fontconfig + fonts for stable local browser runtime on Linux

Use this when Playwright Chromium or Hermes CDP browser:
- opens `localhost` once and then becomes flaky;
- crashes or closes the page/context on simple `goto()` / reload;
- runs on a host without root access and without system `fontconfig` / base fonts.

## Why this matters

A missing browser binary is only one class of problem. Another class is a half-working Chromium with no usable font stack. In that state the browser may start, but headless rendering and later page operations become unstable enough to look like an app bug.

## Local-first fix

Prefer a user-space runtime instead of adding external browser infrastructure.

1. Reuse the existing Playwright Chromium binary if it is already cached.
2. Download these deb packages without installing system-wide:
   - `fontconfig-config`
   - `libfontconfig1`
   - `fonts-dejavu-core`
   - `fonts-liberation2`
3. Extract them into a home-directory runtime root, for example:
   - `~/.local/browser-runtime/root`
4. Launch Chromium / Playwright / Hermes CDP with:
   - `FONTCONFIG_PATH=~/.local/browser-runtime/root/etc/fonts`
   - `FONTCONFIG_FILE=~/.local/browser-runtime/root/etc/fonts/fonts.conf`
   - `XDG_DATA_DIRS=~/.local/browser-runtime/root/usr/share`
   - existing `LD_LIBRARY_PATH` for Hermes browser libs if Hermes already uses one

## Minimal commands

Download and extract:

```bash
mkdir -p ~/.local/browser-runtime/debs ~/.local/browser-runtime/root
cd ~/.local/browser-runtime/debs
apt-get download fontconfig-config libfontconfig1 fonts-dejavu-core fonts-liberation2
for deb in *.deb; do dpkg-deb -x "$deb" ~/.local/browser-runtime/root; done
```

Run Playwright / node script:

```bash
env \
  FONTCONFIG_PATH=$HOME/.local/browser-runtime/root/etc/fonts \
  FONTCONFIG_FILE=$HOME/.local/browser-runtime/root/etc/fonts/fonts.conf \
  XDG_DATA_DIRS=$HOME/.local/browser-runtime/root/usr/share \
  LD_LIBRARY_PATH=$HOME/.hermes/browser-libs/root/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-} \
  node your_playwright_script.mjs
```

Run Chromium as a Hermes CDP backend:

```bash
env \
  FONTCONFIG_PATH=$HOME/.local/browser-runtime/root/etc/fonts \
  FONTCONFIG_FILE=$HOME/.local/browser-runtime/root/etc/fonts/fonts.conf \
  XDG_DATA_DIRS=$HOME/.local/browser-runtime/root/usr/share \
  LD_LIBRARY_PATH=$HOME/.hermes/browser-libs/root/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-} \
  ~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome \
  --headless=new \
  --remote-debugging-port=9224 \
  --user-data-dir=$HOME/.hermes/chrome-debug-9224 \
  --no-first-run --no-default-browser-check --no-sandbox --disable-dev-shm-usage about:blank
```

Then point Hermes to the CDP endpoint, for example `browser.cdp_url = http://127.0.0.1:9224`.

## Verification standard

Do not stop at “browser process started”. Verify both layers:

1. Direct Playwright probe:
   - `goto(http://127.0.0.1:8790/)`
   - page title/text render correctly
   - no immediate `page.close` / `page.crash`
2. Hermes browser tools:
   - `browser_navigate()` succeeds
   - `browser_snapshot()` is non-empty
   - `browser_console('window.location.href')` returns the real localhost URL
   - short DOM sample is readable

## Pitfall

If authenticated boot still fails after runtime stabilization, inspect the frontend for the real storage key before blaming the app. A wrong `localStorage` key creates a false negative that looks like a browser or auth problem.
