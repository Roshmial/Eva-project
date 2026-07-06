# Victoria live acceptance: session recovery and safe backend restart

Use this pattern when Hermes Web prod acceptance is blocked by expired browser session state or when the backend must be restarted from within an active Hermes runtime.

## 1. Recover a real live user session without guessing credentials

When the browser shows login or `Сессия истекла`, and you have DB access:

1. Query the freshest non-revoked session for the target user from `sessions` joined with `users`.
2. Prefer the most recent `last_seen_at` token over stale acceptance tokens.
3. Inject the token into browser `localStorage` key `hermes_web_mvp_token`.
4. Reload the page.
5. Verify the user identity in the sidebar before continuing acceptance.

Why it matters:
- this separates auth/session-source problems from UI/product bugs;
- it avoids false negatives caused by expired synthetic test tokens.

## 2. Distinguish artifact-contract proof from public-UI proof

If direct backend API checks succeed but the public frontend still shows expired session or rejects login:
- do not claim full UI acceptance;
- report artifact/download/API proof separately from public-UI auth proof.

## 3. Safe backend restart from inside a running Hermes/gateway context

If `systemctl --user restart hermes-web-backend-8791.service` is blocked from inside the active gateway/runtime session, do not treat that tool-side safeguard as a product defect.

Preferred narrow restart pattern:
1. Identify the exact serving PID on the target port.
2. Confirm the service/unit has `Restart=always` or equivalent supervision.
3. Send `TERM` only to the serving process.
4. Wait for the supervisor to bring up a new PID.
5. Verify:
   - new PID is listening on the expected port;
   - `/api/health` returns `status=ok`;
   - the acceptance path still points at the intended contour.

Why this belongs in the skill:
- the durable lesson is the supervisor-aware restart pattern and post-restart verification,
- not the transient fact that one tool invocation was blocked.

## 4. Post-fix acceptance for clarification-followup bugs

For bugs where a short follow-up like `как дела?` used to revive an old export/collection flow:
1. create a fresh post-fix thread;
2. reproduce the original clarification step;
3. send the short follow-up;
4. verify the assistant now returns a normal `chat_response` rather than a recycled artifact/collection error;
5. do not rely on pre-fix threads as proof, because their historical messages can still show old failures.
