# Hermes Telegram reactions: implementation notes

Durable pattern observed in-session for Hermes Telegram processing feedback.

## What was verified

Hermes already has a Telegram reaction lifecycle tied to processing hooks.

Observed semantics:
- processing start -> 👀
- processing success -> 👍
- processing failure -> 👎
- processing cancelled -> clear reaction

## Feature flag

Environment flag:
- `TELEGRAM_REACTIONS`

Observed behavior from tests:
- default: disabled
- truthy enable values include `true` and `1`
- falsy disable values include `false`, `0`, `no`

## Hermes code locations seen in-session

Primary implementation:
- `gateway/platforms/telegram.py`

Observed branch near end-state handling:
- `ProcessingOutcome.CANCELLED` calls reaction clearing
- other outcomes map to thumbs-up / thumbs-down

Observed tests:
- `tests/gateway/test_telegram_reactions.py`

Test coverage seen:
- disabled by default
- enabled via env flag
- `_set_reaction` success path
- graceful failure when bot missing
- graceful failure on API exception
- start hook adds 👀
- success hook adds 👍
- failure hook adds 👎
- cancelled hook clears reaction
- disabled mode makes no API calls
- missing ids are handled gracefully

## Implementation lesson worth reusing

When a Telegram agent uses reactions as processing feedback, cancellation must actively clear the in-progress reaction. Otherwise the UX leaves a stale "still working" marker on the user's message.

## Why this matters

This is a good low-noise pattern for local-first agents: lightweight acknowledgement without chat spam, plus explicit terminal states when work finishes.
