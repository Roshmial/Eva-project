# Live runtime privacy and restart pitfalls

Use this when verifying a live user flow or auth/runtime issue on a real Hermes Web contour.

## 1. Do not dump raw API payloads back to the user

When you inspect login responses, user records, dashboard payloads, or thread/message meta for a real user:
- do not paste raw JSON into chat;
- do not surface full user profile blobs, interaction memory, or internal meta;
- summarize the result in one or two human sentences.

Good:
- "Пароль восстановлен, вход проверен, всё работает."
- "Последний dashboard_result снова слабый: тема съехала, числа иллюстративные, источников мало."

Bad:
- full `/api/auth/login` body;
- full `user` object;
- raw `message.meta_json` unless the user explicitly asked for it.

## 2. Restart Hermes Web backend only through the project bootstrap

For live contour work on Hermes Web backend 8791, do not restart the backend by launching `waitress-serve` directly.

Why:
- direct `waitress-serve ... app:app` can bypass the runtime env bootstrap;
- the process may come up in `mock-hermes` instead of `hermes-api`;
- then auth, DSN, model routing, and user counts can point at the wrong runtime plane.

Use the project bootstrap instead:
- `run_backend_service.sh`
- which sources `scripts/runtime_env.sh`
- which in turn loads `~/.hermes/.env` and restores the intended live mode.

## 3. Post-restart acceptance checks

After a live backend restart, always verify all three:
1. `/api/health` shows the expected mode (`hermes-api`, not `mock-hermes`);
2. user/thread counts are plausible for that contour;
3. the concrete login or user flow that motivated the restart actually works.

## 4. Dashboard verification discipline

When a user says "dashboard is bad again", separate three failure classes:
- renderer/UI failure;
- backend fallback envelope pretending to be a real dashboard;
- semantically wrong dashboard payload (topic drift, invented numbers, wrong language, weak sources).

Do not stop at "the section rendered" if the payload itself is low-quality.
