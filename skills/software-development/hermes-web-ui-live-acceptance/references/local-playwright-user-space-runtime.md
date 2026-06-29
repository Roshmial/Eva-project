# Local Playwright user-space runtime bootstrap

Use this when browser acceptance is needed on a host where Playwright Chromium exists but fails on missing shared libraries, and sudo/system package install is not available or not desirable.

## Pattern

1. Identify missing libraries from Chromium/`ldd` output.
2. Download the exact Ubuntu packages locally with `apt download`.
3. Unpack them under the project with `dpkg-deb -x`.
4. Build `LD_LIBRARY_PATH` from unpacked `usr/lib/x86_64-linux-gnu`, `lib/x86_64-linux-gnu`, `usr/lib`, and `lib` directories.
5. Launch Playwright/Chromium through a small wrapper script that exports `LD_LIBRARY_PATH` (and, when needed, `GTK_PATH` / `GIO_MODULE_DIR`).
6. After Chromium starts, continue with normal acceptance: login, navigate, inspect DOM/console, take screenshot.

## Minimal command pattern

```bash
apt download <package>...
dpkg-deb -x package.deb .local-browser-libs/extracted/<dir>
LD_LIBRARY_PATH="$(find .local-browser-libs/extracted -type d \( -path '*/usr/lib/x86_64-linux-gnu' -o -path '*/lib/x86_64-linux-gnu' -o -path '*/usr/lib' -o -path '*/lib' \) | paste -sd: -)"
node acceptance-script.cjs
```

## Typical package families

Do not hardcode one canonical list forever, but common families include:
- NSS / NSPR: `libnspr4`, `libnss3`
- GTK / GLib / Pango / Harfbuzz
- X11 / XCB / Xi / Xcursor / Xinerama / Xrender
- cairo / pixbuf / epoxy / fontconfig / fribidi / thai
- Wayland / GBM / DRM / xshmfence
- ALSA / AT-SPI

## Acceptance reminder

A working Chromium process is only the midpoint. The real pass requires the app to render the intended authenticated UI. If your first automation path still lands on login or `401`, switch from token injection assumptions to an explicit login flow and only then set UI state / open the target thread.
