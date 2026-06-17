# Misha: Telegram test mode and event selection

Use this reference when tuning recurring self-development briefs for Misha.

## Durable workflow rules

- For Misha, a cron "test period" still delivers to Telegram. The test aspect is the limited duration and iterative tuning, not local-only delivery.
- If there is an old production daily job and a newer test-week job, prefer one active delivery path to avoid duplicate or misleading behavior. Paused legacy jobs can create confusion during troubleshooting.
- When a scheduled message did not arrive, inspect both schedule status and delivery target. In this case the root cause was not cron timing but `deliver=local` on the active test job while the older job was paused.

## Content rules for daily briefs

- Start the daily brief with: "Доброе утро, Миша!"
- Prefer one grounded focus for the day over an overloaded checklist.
- If adding a leisure or event suggestion, avoid bland respectable defaults. Prefer interesting, unusual, contemporary, or personally plausible options.
- Do not insert technically valid but low-energy recommendations just to fill the slot.

## Content rules for weekly event picks

- Monday send time: 09:45 Moscow time.
- Range: Monday through Sunday of the current week.
- Minimum: 10 events.
- Include links and short recommendations.
- Bias toward events that feel alive, specific, and worth real attention rather than generic safe picks.

## Troubleshooting pattern

When the user reports a missed scheduled message:
1. Check whether the active job is paused.
2. Check whether a legacy job exists and could mislead expectations.
3. Check `deliver` before assuming schedule failure.
4. If the user calls it a test period, do not switch delivery to local-only unless they explicitly ask for that.
