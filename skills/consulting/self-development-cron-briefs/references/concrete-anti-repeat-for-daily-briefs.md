# Concrete anti-repeat control for daily self-development briefs

When a user says a daily brief feels repetitive, do not stop at schedule overlap or duplicated sends.

There are two different repetition classes:

1. Delivery duplication
- the same cron job ran more than once;
- a manual run and the scheduled run both delivered;
- this creates extra morning messages.

2. Content recycling inside otherwise valid daily runs
- the daily brief is delivered once per run, but the same concrete fallback ideas return across different days;
- this is not solved by scheduler debugging.

## Confirmed failure pattern from this session

The user pointed out that concrete leisure/support ideas kept recurring in the 6:30 daily brief.

Confirmed repeats found in recent history:
- `GeoGuessr` appeared on 2026-06-22 and again on 2026-07-02.
- `Сад будущего` appeared on 2026-06-13, 2026-06-27, and 2026-07-02.

This proved that checking only generic categories such as `walk`, `game`, or `small reset` is not enough. The prompt must check concrete objects.

## Practical prompt fix

Strengthen the daily cron prompt so it:
- scans at least the last 10 morning briefs;
- treats repeated concrete places and repeated concrete games/media suggestions as failures;
- treats reuse of the same concrete place or game within about 14 days as a hard failure;
- forces a different category instead of paraphrasing the same idea;
- may explicitly blacklist sticky fallback ideas until the rotation stabilizes.

Example of an acceptable explicit ban in prompt text:
- `Do not reuse GeoGuessr or Сад будущего if either of them appeared in the recent brief history.`

## Verification pattern

After tightening the prompt, do a manual rerun and verify that the new output no longer uses the repeated concrete objects.

In this session, the post-fix manual run replaced the repeated objects with different suggestions, which is the right acceptance signal.
