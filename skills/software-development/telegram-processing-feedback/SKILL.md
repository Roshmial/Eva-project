---
name: telegram-processing-feedback
description: Design and implement lightweight Telegram feedback loops for async message processing, especially status reactions and completion signaling in local-first bots and agents.
---

# When to use

Use this skill when:
- a Telegram bot or agent needs to acknowledge that a user message was received;
- processing is asynchronous and may take long enough that silence feels broken;
- you want a lighter UX than sending multiple status messages;
- you are wiring lifecycle hooks such as started / succeeded / failed / cancelled.

# Goal

Provide fast, low-noise user feedback while keeping the chat clean.

# Recommended pattern

1. Start with the lightest visible signal.
   - Prefer a reaction on the user's message before sending extra text.
   - Good default: in-progress reaction like 👀.

2. Map processing outcomes to explicit end states.
   - Success: replace the in-progress reaction with a positive terminal signal.
   - Failure: replace it with a negative terminal signal.
   - Cancelled / interrupted: clear the in-progress signal rather than leaving a stale status behind.

3. Gate the feature behind a config flag.
   - Reactions are a UX feature, not a hard dependency.
   - The bot should keep working normally when reactions are disabled or unavailable.
   - Для Hermes Telegram сначала проверь, включена ли переменная `TELEGRAM_REACTIONS`; при её отсутствии текущая реализация считает reactions выключенными по умолчанию.
   - Поэтому при разборе «почему нет 👍/👎» сначала проверь feature flag, и только потом лезь в lifecycle hooks.

4. Fail soft.
   - Reaction API failures must never break message handling.
   - Log the problem, return control, continue processing.

5. Test every lifecycle branch.
   - Disabled by default.
   - Explicit enable/disable values.
   - Start hook.
   - Success hook.
   - Failure hook.
   - Cancelled hook.
   - Missing chat_id / message_id.
   - API exception path.

# Design notes

- Reactions are best for state, not explanation.
- Keep semantics stable. If you pick a meaning for each emoji, do not change it casually.
- For long-running flows, reaction-first plus a final text answer is usually cleaner than multiple progress messages.
- If the platform or library supports clearing reactions by passing `None` or an empty payload, use that on cancellation to avoid stale in-progress markers.

# Pitfalls

- Do not leave the in-progress reaction on cancelled runs. A stale "working" marker is worse than no marker.
- Do not assume reactions are always supported in every chat type, bot permission model, or library version.
- Do not couple business success to UX success. If setting the reaction fails, the main task should still complete.
- Do not spam extra status messages when a reaction already covers the acknowledgement need.

# Verification checklist

- A new incoming message gets an immediate lightweight acknowledgement.
- Success replaces the in-progress signal.
- Failure replaces the in-progress signal.
- Cancellation removes the in-progress signal.
- With the feature flag off, no reaction API calls are made.
- API exceptions do not bubble into the main processing path.

# References

- `references/hermes-telegram-reactions.md` — Hermes-specific implementation notes, file paths, and test cases observed in-session.
