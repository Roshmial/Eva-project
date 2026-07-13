# Local CDP override + user-space font runtime: working Hermes fix pattern

Use this reference when Hermes browser tools on a local Linux host show split-brain behavior between navigate, console, snapshot, and vision.

## Symptoms that matched this case

1. Before routing fix
- `browser_navigate('https://example.com')` reported success and title `Example Domain`
- but follow-up state still behaved like `about:blank`
- `browser_snapshot()` could be empty/mismatched

2. Before runtime fix
- direct CDP open/eval/snapshot already worked
- but screenshot / `browser_vision()` returned a white or nearly blank frame

## Durable lessons

### 1) Treat routing and rendering as separate layers

A successful navigate does not prove the rest of the browser contour is healthy.

Use this order:
1. direct CDP smoke
2. Hermes navigate
3. Hermes console
4. Hermes snapshot
5. Hermes vision

### 2) If a stable local CDP endpoint already exists, pin Hermes to it

Example config:

```yaml
browser:
  cdp_url: http://127.0.0.1:9224
```

This is especially useful when a dedicated local Chrome/Chromium service already exists and Hermes otherwise falls back to a different local session.

### 3) Blank screenshots can come from local runtime/font issues even when DOM is correct

A practical service-level hardening pattern:

```ini
[Service]
Environment=FONTCONFIG_PATH=/home/hermes/.local/browser-runtime/root/etc/fonts
Environment=FONTCONFIG_FILE=/home/hermes/.local/browser-runtime/root/etc/fonts/fonts.conf
Environment=XDG_DATA_DIRS=/home/hermes/.local/browser-runtime/root/usr/share
Environment=LD_LIBRARY_PATH=/home/hermes/.hermes/browser-libs/root/usr/lib/x86_64-linux-gnu
ExecStart=/path/to/chrome --headless=new --remote-debugging-address=127.0.0.1 --remote-debugging-port=9224 --user-data-dir=/path/to/profile --disable-gpu --no-first-run --no-default-browser-check --no-sandbox --disable-dev-shm-usage about:blank
```

Then reload/restart the user service and repeat the 4-layer Hermes verification.

## Minimal acceptance target

A fix is good enough only when all of the following are true on the same test page:
- `browser_navigate()` succeeds
- `browser_console()` returns the real URL/title/body
- `browser_snapshot()` returns meaningful content
- `browser_vision()` shows the actual page instead of a blank image
