# Local auth-bootstrap false negatives during browser debugging

Use this when local browser QA mixes two moving parts:
- unstable Hermes/local browser session state;
- authenticated frontend bootstrap via localStorage token restore.

## Key lesson

Do not assume a token storage key.

In Hermes Web MVP the frontend reads:
- `const STORAGE_KEY = 'hermes_web_mvp_token';`

Injecting common fallback keys like `token` or `hermes_token` can make the page look like auth restore is broken when the app simply never sees the token.

## Practical debugging pattern

1. Inspect the frontend source for the real storage key before token injection.
2. Inject the token under that exact key.
3. Reload and capture:
   - network events for `/api/*`;
   - `#appShell` class;
   - `#loginScreen` class;
   - banner / login error text;
   - a short body-text snapshot.
4. Compare outcomes:
   - only `service-info` / setup calls fire -> likely token bootstrap never engaged;
   - authenticated API calls fire but UI stays hidden -> investigate app boot sequence;
   - browser session collapses before stable DOM capture -> investigate runtime/CDP layer separately.

## Separate typing issues from app issues

If browser typing reports success but login still acts like fields are empty:
- read input `.value` directly in the DOM;
- if needed, set value programmatically and dispatch `input` + `change` for diagnosis.

That does not prove the final UX is acceptable, but it cleanly separates a flaky browser-tool input path from a real frontend form bug.
