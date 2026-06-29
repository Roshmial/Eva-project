# Live acceptance smoke drift vs real product break

Use when a live browser-driven acceptance script fails after login, but the failure may be in the smoke selectors rather than in the product itself.

## Core rule

Do not declare the live UI broken from smoke failure alone when the failing step is a selector contract such as:
- `input[type=file]` expected before the upload drawer/button is opened;
- old placeholder text no longer present;
- old send-button label no longer present;
- historical `data-*` admin hooks removed from the DOM.

First inspect the live DOM and separate:
1. real user-path failure;
2. stale acceptance script.

## Verified Hermes Web pattern from 2026-06-25

Real prod contour at verification time:
- public frontend: `http://95.182.85.233:8803/`
- backend API: `http://178.104.207.89:8791/api`
- frontend service: `hermes-web-frontend-8803.service`
- backend service: `hermes-web-backend-8791.service`

Observed smoke drift:
- upload input existed only after clicking `Файлы` and was hidden with `display:none`;
- message field placeholder was `Сообщение`, not the older longer phrase;
- send action used button text `↑`, not `Отправить`;
- admin tabs were switched by visible buttons (`Обзор`, `Пользователи`, `Операции`, `Справочники`, `Источники и policy`), not by `data-admin-section` hooks.

## Recommended response

1. Prove login and post-login nav manually or via browser tool.
2. Inspect DOM/console for the failing step.
3. If the flow still works manually, patch the smoke script immediately.
4. Re-run the full smoke on the real prod contour.
5. Update the operational verify script/runbook so future checks use the current contour, not legacy dev ports.

## Acceptance evidence pattern

A repaired smoke should return explicit booleans for critical areas, not just "no exceptions":
- chat
- profile
- jobs create
- jobs pause/resume
- admin user create
- admin operations tab
- admin references tab

If those are green on the real public contour, classify the issue as acceptance drift that has been closed, not as an unresolved live product regression.
