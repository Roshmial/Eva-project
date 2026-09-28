# Stale CDP override and blank screenshot cues

Use this note when browser behaviour is mixed and the first signal looks deceptively healthy.

## Symptom pattern A — poisoned CDP override session

Typical sequence:
- `browser_navigate` returns success and may even report the expected title.
- Follow-up `browser_snapshot` or `browser_eval` fails with `CDP WebSocket connect failed` / `Connection refused`.
- The failing endpoint is often a configured `browser.cdp_url` or `BROWSER_CDP_URL` such as `127.0.0.1:9224` that is no longer alive.

Interpretation:
- this is not a generic frontend failure;
- it is not the old `CDP 404` class;
- it usually means the wrapper created a CDP-backed session from stale override state instead of degrading to local Chromium.

Recommended repair pattern:
1. Health-check the override via `/json/version` before session creation.
2. If unreachable, do not create a CDP session at all.
3. Fall back to a local Chromium session immediately.
4. Verify with `navigate -> snapshot -> eval`, not navigate alone.

## Symptom pattern B — blank screenshot with live page

Typical sequence:
- page state checks show a real page is present;
- screenshot-based analysis returns a blank or near-blank frame;
- the issue reproduces in `browser_vision` more readily than in `browser_snapshot`.

Interpretation:
- treat it as a screenshot-path defect first, not proof that the page is empty.
- primary CDP capture may return a blank frame even while the page rendered.

Recommended repair pattern:
1. Detect suspiciously blank screenshot output.
2. Retry once via temporary Chrome capture at the current URL.
3. Propagate a fallback warning so the operator knows vision used the recovery path.
4. Keep the distinction explicit: screenshot-path recovery is a separate fix from session-routing recovery.

## Verification checklist

A convincing repair should show:
- blank screenshot case recovered through fallback and returned a non-empty analysis;
- stale CDP override case degrades to local session instead of poisoning follow-up calls;
- focused tests cover both paths.
