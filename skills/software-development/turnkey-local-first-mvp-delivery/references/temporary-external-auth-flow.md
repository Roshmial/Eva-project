# Temporary external auth flow for downstream API access

Use this pattern when a local-first service already runs on the user's server, but a non-technical user needs to complete a one-time authorization flow from a phone or remote browser.

## When this pattern fits
- The real goal is not product-account login, but authorizing access to a downstream system such as Telegram API.
- The user should only perform the auth ceremony; all env, service wiring, and session storage should be prepared server-side.
- The current stack already has a running local service, and adding a thin page to that service is cheaper than introducing a new app.

## Recommended MVP flow
1. Reuse the existing service/runtime.
2. Add a temporary web page reachable by a one-time or short-lived tokenized URL.
3. Keep the flow stepwise:
   - phone / identifier entry;
   - code entry;
   - password / 2FA only if the upstream API explicitly requires it.
4. Persist the resulting session/token only on the server.
5. After success, replace the form with a final completion state such as `Спасибо, авторизация пройдена...`, not a stale input form.
6. Treat the link as single-use after success; subsequent attempts should return a conflict and instruct the operator to create a new link.

## User-facing copy rules
- Name the target explicitly: for example `Авторизация Telegram API`, not just `Авторизация`.
- Explain what is being created: a server-side session for access through the API.
- Keep the success state explicit and terminal: the user should know they can close the page.

## Safety baseline
- Creation of auth links should be admin-only:
  - localhost-only by default, or
  - protected by an admin token / reverse-proxy auth.
- External exposure over the public internet should prefer HTTPS.
- Do not echo codes or passwords back into the UI after submission.
- Expire unused links automatically.

## Verification checklist
- Confirm the auth-state record moved to `authorized`.
- Confirm the server-side session artifact was created.
- Confirm the session can call the upstream API as the intended account.
- Separately verify whether the account actually has access to the target resource; successful authorization does not prove channel/group membership.

## Important distinction
A successful login proves the session belongs to the expected account. It does **not** prove access to a specific Telegram chat/channel or other protected downstream resource. That must be checked separately with a live entity/resource probe.
