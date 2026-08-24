# August 2026 — link-aware daily reset

Use this note when the user says the daily brief should be rebuilt from scratch rather than patched.

## Trigger pattern

Typical complaints:
- the brief keeps sounding smart but useless;
- the bank is polluted with abstractions like priorities, focus, importance, attention, layers, causes;
- anti-repeat only checks old outputs but does not stop main/support from collapsing into the same type of action;
- external-resource suggestions are requested, but links disappear in rendering or are glued as ugly tails.

## Rebuild contract

When doing a reset:
1. rebuild the bank from zero instead of editing old lines in place;
2. keep only literal action lines, close to `сделай ...`;
3. add explicit `family` fields so main and support can be forced apart;
4. keep linked suggestions as first-class bank items, not post-processing;
5. emit pre-rendered authoritative fields from preflight so the renderer copies, not re-decides.

## Bank structure that worked

Each item carries:
- `id`
- `family`
- `text`
- optional `has_link: true`

Linked items keep the markdown link inside `text`, for example:
- `Я бы сегодня открыла [Nine Short Essays](https://www.gutenberg.org/ebooks/3108) ...`
- `На вечер можно посмотреть одно короткое [документальное видео](https://www.youtube.com/playlist?list=...)`

## Selection logic that worked

Main selection:
- avoid recent `id` reuse;
- avoid recent `family` reuse;
- keep same-date deterministic stability.

Support selection:
- avoid recent `id` reuse;
- forbid same `family` as main;
- reduce token overlap with main;
- prefer linked items when they do not conflict.

## Rendering contract that worked

Preflight should emit:
- `DAY_LINE_RENDERED`
- `SELECTED_MAIN_RENDERED`
- `SELECTED_SMALL_RENDERED`

Then the final prompt should copy those almost verbatim.

This avoids:
- day/date retranslation drift;
- loss of inline links;
- the model "improving" a concrete line into abstract management prose.

## Validation additions

The validator should check:
- abstract-ban vocabulary;
- concrete verbs;
- `has_link=true` implies a real markdown link inside `text`;
- markdown link inside `text` implies `has_link=true`;
- minimum non-trivial population of linked items.

## Outcome to aim for

A good rebuilt brief looks like:
- one plain concrete action;
- one support action, sometimes linked;
- no raw URL;
- no priority/focus/profoundness wording;
- stable same-date reruns.
