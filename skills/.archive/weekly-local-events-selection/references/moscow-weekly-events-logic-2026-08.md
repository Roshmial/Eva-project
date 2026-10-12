# Moscow weekly events logic — 2026-08 correction pass

Session lessons captured for future weekly city-event digests:

## Defect patterns observed

1. One-source collapse
- The weekly Moscow list drifted into one institution because that source was easy to verify repeatedly.
- Venue bias and domain bias are separate failure modes and both need explicit caps.

2. Missing citywide trigger
- A weekly city digest missed Day of the City even though it was the dominant city-level event of that week.
- Citywide/official programs must be checked before venue-level backfill.

3. Weak museum backfill
- Long-running exhibitions were used to reach target list length.
- The better behavior is to return a shorter list of stronger items.

4. Date leakage past the requested week
- A later run included an event on 7 September while the requested window ended on 6 September.
- A final date-boundary audit against `week_end` is mandatory.

## Guardrails that improved output

- Default max 2 items from one venue.
- Default max 2 items from one source domain.
- 3+ allowed only for a clearly week-defining city/festival cluster.
- Last 1-2 items must clear a stricter bar than the top of the list.
- Prefer exact date/time for normal events.
- Accept vague range wording only for true citywide programs or soon-ending items.

## What a better output looked like

- Day-of-city programming was included explicitly.
- No MAMM domination.
- Picks came from several domains instead of one convenient source.
- All dates stayed inside the requested week.
- The list felt like "what to catch now" rather than filler.
