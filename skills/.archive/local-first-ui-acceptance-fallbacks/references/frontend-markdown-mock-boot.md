# Frontend markdown mock-boot acceptance pattern

Use this reference when a Hermes Web frontend change must be verified, but the full authenticated runtime path is noisy or partially failing.

## Session pattern captured

Change under test:
- backend prompt tightened with explicit self-check / anti-fabrication language;
- frontend markdown renderer extended to support `$\\to$` normalization and pipe tables.

What was fully real:
- `python3 -m pytest test_smoke.py` in backend passed (`34 passed`);
- `npm run react:build` passed;
- local backend/frontend health endpoints responded.

What was *not* fully healthy:
- after real login on a local prod-like surface, parallel post-login requests (`bootstrap`, `me`, `files`, `threads`, `jobs meta`) could return `503`;
- that blocked a clean full live authenticated UI acceptance for this pass.

## Fallback used

1. Serve the real built frontend.
2. Launch headless Playwright against that surface.
3. Intercept `http://127.0.0.1:<port>/api/**`.
4. Mock the minimum payloads for:
   - `/api/service-info`
   - `/api/setup/status`
   - `/api/auth/login`
   - `/api/me`
   - `/api/bootstrap`
   - `/api/feedback/reasons`
   - `/api/files`
   - `/api/jobs/meta`
   - `/api/threads`
   - `/api/threads/:id`
   - `/api/threads/:id/messages`
5. Use realistic payload shapes so the actual React app boots into chat.
6. Navigate to chat, open the composer if needed, submit the markdown sample, and assert rendered DOM.

## Assertions that proved the renderer change

Sample content:

`Проверка markdown`

`Схема: A $\\to$ B`

`| Колонка | Значение |`
`|---|---|`
`| alpha | 1 |`
`| beta | 2 |`

Expected DOM facts:
- rendered text contains `A → B`;
- rendered text does **not** contain raw `\\to`;
- one `table.message-md-table` exists;
- table has 2 headers and 4 cells;
- headers are `Колонка`, `Значение`;
- cells are `alpha`, `1`, `beta`, `2`.

Observed result in the session:
- `arrowPresent=true`
- `rawArrowTokenPresent=false`
- `tableCount=1`
- `thCount=2`
- `tdCount=4`

## Reporting rule

Report this as:
- renderer change verified via isolated headless DOM acceptance on the real built frontend;
- full authenticated live flow still has a separate boot/runtime `503` tail.

Do **not** report it as a fully clean end-to-end live acceptance if the real login flow remained degraded.

## Extra durable lesson

When backend file/download URLs intentionally gain token query params or similar runtime additions, prefer asserting the stable contract (`startswith('/api/files/<id>/download')`) rather than brittle exact URL equality.
