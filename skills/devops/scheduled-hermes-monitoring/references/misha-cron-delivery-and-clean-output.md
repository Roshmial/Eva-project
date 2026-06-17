# Misha: cron delivery and clean output

Use these rules for recurring user-facing Hermes jobs in Misha's setup.

## Test-window semantics

A "test period" for a cron job does not automatically mean local-only delivery.
For Misha, the default interpretation is:
- the job is limited in duration;
- output still goes to Telegram;
- he may refine the wording or behavior during the test window;
- the agent should monitor the runs and adjust.

Only keep delivery local if he explicitly asks for local-only behavior.

## Output cleanliness

For user-facing jobs, the delivered payload must be presentation-clean:
- no raw `MEDIA:` syntax in the prose;
- no markdown image placeholders in the final visible text;
- no service chatter, tool traces, or "skill created"-style messages;
- no extra block with "possible improvements" unless requested.

## Telegram image-post shape

If the approved format is an image post in Telegram, prefer:
1. separate image message;
2. separate caption text message.

Do not silently revert to a single captioned media message when the user explicitly asked for two messages.
