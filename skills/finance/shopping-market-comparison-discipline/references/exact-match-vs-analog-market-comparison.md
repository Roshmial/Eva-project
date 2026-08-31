# Exact-match vs analog market comparison

## Why this note exists

In live shopping comparison tasks, the easiest failure mode is drifting from the exact requested item into nearby variants because search engines surface them more aggressively.

## Practical lesson

When the user says `тот же товар`, treat it as a hard constraint.

The comparison must first preserve:
- exact pack size;
- exact flavor combination;
- exact product line.

Only after the exact-match search is exhausted may the agent add:
- normalized per-unit comparisons for other pack sizes;
- nearby variants in the same line;
- partial confirmations from snippets when live cards are blocked.

## Evidence labels worth using

- `подтверждено по живой карточке`
- `подтверждено только по сниппету`
- `карточка заблокирована / anti-bot`
- `найден похожий вариант, но это не тот же товар`

## Example failure pattern

Source item was a 40-pouch mix.
Search results quickly surfaced many 26-pouch listings from the same brand and line.
Those were useful for market context, but they should not lead the answer when the user explicitly asked for the same item in other stores.
