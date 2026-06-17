---
name: travel-roadtrip-planning
description: Plan short road-trip vacations by balancing route load, destination content, and accommodation quality; use fallback travel aggregators when the preferred source is unavailable.
version: 1.0.0
author: Eva
---

# Travel road-trip planning

## When to use
- The user asks to plan a vacation or long weekend by car.
- The task mixes route design, what-to-see shortlisting, and accommodation selection.
- The user already has a baseline route but is unsure between two destination regions.
- The preferred booking source cannot be fully verified and you need grounded fallbacks.

## Core principle
Do not treat route planning as only a mileage problem. For short vacations, the real decision is the ratio between:
- road fatigue,
- density of worthwhile stops,
- quality of the final base,
- and the type of vacation the user actually wants.

A route that is technically feasible may still be a poor vacation if it compresses the stay too hard.

## Output structure
Default structure for this class of task:
1. Short conclusion: which direction looks stronger and under what assumption.
2. Facts verified from tools: distances, drive times, confirmed accommodation snippets, confirmed source limitations.
3. Assumptions/hypotheses: where ratings, availability, or seasonal access were not fully verified.
4. Destination content shortlist: what is actually worth seeing, separated into must-see / worthwhile / optional.
5. Accommodation shortlist: clearly label source of rating or whether only the object existence/format was verified.
6. Decision lens: what type of vacation each option creates.
7. Recommended next step: narrow to one scenario and then do a final booking pass.

If the user asks to "form a program/itinerary" rather than compare directions, default to one coherent end-to-end route with dates, overnight stops, and daily plan. Do not dump multiple scenarios unless the user explicitly asks for options.

## Workflow
1. Clarify the anchor constraint:
   - trip dates,
   - return deadline,
   - number of people,
   - car vs train/flight,
   - preferred accommodation type,
   - whether the user values route variety or final-base quality more.
2. Check drive times with tools rather than intuition.
3. If the user already reports lived route experience, respect it and update the framing. Do not keep arguing from generic routing assumptions.
4. Separate two questions:
   - logistics: can this be done without turning the trip into a march;
   - content: is there enough interesting material near the base for 3-5 days.
5. For each destination region, describe the *type of vacation* it creates, not only the list of sights.
6. For accommodation:
   - try the user’s preferred source first;
   - if unavailable, use alternative aggregators;
   - never present an unverified rating as confirmed fact.
7. Prefer a short, decision-ready shortlist over a long dump.

## Source hierarchy for accommodation
1. User-requested source, if accessible.
2. Alternative aggregators such as Ostrovok, 101Hotels, Tripadvisor, official property pages.
3. Search snippets only as a lead source, never as fully confirmed booking truth.

When a fallback source is used, say so explicitly.

## Rating and verification rules
- Distinguish these states clearly:
  - rating confirmed on requested platform,
  - rating confirmed on alternative platform,
  - only object existence confirmed,
  - format inferred from description or photos but not fully checked.
- Do not translate one platform’s 10-point score into another platform’s 5-point or 100-point system.
- If a source is blocked or partially accessible, say that the limitation exists and continue with other sources.

## Destination-content method
For each region, build three layers:
- Anchor object: the one place that justifies the direction.
- Supporting day trips: realistic half-day or full-day outings.
- Atmosphere layer: what the vacation feels like between landmarks.

This avoids recommending a destination with one famous place but too little surrounding content.

## User-specific pitfall learned
When the user already knows a route is feasible from prior driving experience, do not keep optimizing around generic fatigue assumptions. Shift quickly to what the region offers, what deserves a full day, and whether the destination produces the kind of rest the user wants.

## Common pitfalls
- Overfitting to the first baseline route and missing a better destination framing.
- Confusing a scenic transit city with a meaningful stop; if the user says a stop has no value for them, stop selling it.
- Giving long accommodation lists without marking what is actually verified.
- Treating a single iconic attraction as enough content for a 4-5 day base.
- Recommending a destination because it is easier to route, even when the final accommodation/product is weaker.
- When giving a tap-to-open route link for Google Maps, do not assume Cyrillic place names in a deep link will render correctly on mobile. If the app shows raw `%D0%...` strings or fails to resolve the route, rebuild the link with ASCII/English place names (for example `Moscow, Russia`) and prefer that version for user-facing delivery.

## Map-link delivery rule
If the user asks for a route "on a map" or wants a ready navigation link:
1. You may provide a local HTML map for visualization.
2. For Google Maps deep links, prefer robust place strings that are unlikely to break mobile decoding.
3. If a Cyrillic route link renders incorrectly in the app, regenerate the same route using English/ASCII city names and send only the corrected link as the primary user-facing version.

## Good comparison frame
Compare options by:
- anchor attraction strength,
- number of worthwhile short trips nearby,
- accommodation quality in the desired format,
- driving burden,
- and vacation character: calm retreat vs varied northern route vs dense sightseeing.

## References
- See `references/fallback-sources-and-comparison.md` for practical notes on fallback sources, source labeling, and how to compare destinations by vacation character.
