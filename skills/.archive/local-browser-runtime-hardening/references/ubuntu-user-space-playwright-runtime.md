# Ubuntu 24.04 no-root Playwright runtime pattern

## When to use

Use this when Playwright Chromium is present in `~/.cache/ms-playwright/`, but `chrome-headless-shell` fails to start because the host is too minimal and root package install is unavailable.

## Reliable sequence

1. Inspect missing libs first:
   - `ldd <chrome-headless-shell> | grep 'not found'`
2. Download the missing runtime packages with `apt download ...`.
3. Extract each `.deb` into a user-owned tree with `dpkg-deb -x`.
4. Build an env file that exports:
   - `LD_LIBRARY_PATH`
   - `FONTCONFIG_PATH`
   - `FONTCONFIG_FILE`
   - `XDG_DATA_DIRS`
5. If Chromium still crashes after startup, add:
   - `fontconfig-config`
   - `libfontconfig1`
   - `fonts-dejavu-core`
   - optionally another base font package
6. Verify in layers:
   - `chrome-headless-shell --version`
   - minimal Playwright launch against localhost
   - only then full smoke / Hermes browser verification

## Why this matters

A broken browser runtime can masquerade as app regressions. The stable pattern is:
- first repair runtime,
- then run minimal launch,
- only then trust smoke failures as app evidence.

## Session-specific lesson worth reusing

Even after the shared-library layer is fixed, headless Chromium may still close the page during `goto` / `reload` until fontconfig and fonts are present. Treat missing fontconfig as an early suspect, not a last resort.
