# Daily usefulness bank and validation

Use this note when Misha says the morning daily is repetitive, abstract, or "smart-sounding but useless".

## Problem pattern

The failure mode is not only wording. The deeper issue is that the daily bank itself drifts toward pseudo-useful abstractions:
- meta-advice about priorities, focus, motivation, or causes;
- phrases that sound intelligent but do not tell the user what to do;
- slight paraphrases of the same old anchor objects;
- compact-but-empty lines after an overcorrection for brevity.

## Target quality bar

For this user, a good daily line is:
- short;
- concrete;
- literally actionable;
- visibly finishable;
- understandable without explanation.

Examples of the desired shape:
- make a stretch;
- watch one short video;
- read one concrete text;
- answer one message;
- clear one bag;
- check one route.

Bad shape:
- rethink a priority;
- inspect a focus layer;
- look at what really matters;
- revisit a pattern;
- find the root cause;
- check whether attention is allocated correctly.

## Bank design rules

1. Keep a curated YAML/JSON bank of candidate useful actions.
2. Track both main and small items separately.
3. Store explicit semantic bans for sticky fallback objects once they start recurring.
4. Prefer idea-level diversity, not only wording diversity.
5. Keep each line short enough for Telegram, but do not trade usefulness away for brevity.

## Validation heuristics

Run a lightweight check over the bank itself before trusting the generator.

Flag as bad:
- kantselyarizm;
- motivational filler;
- abstract management prose;
- phrases needing a follow-up explanation to become useful;
- weak placeholders like `focus`, `priority`, `root cause`, `attention`, `context layer`, `important thing`, `one idea` when they are not grounded in an action.

A practical validator can check:
- duplicate IDs;
- banned patterns;
- weak-word density;
- missing concrete action verbs for main lines.

## Prompt constraints

If preflight already selected a concrete useful line, the renderer must not replace it with a safer abstract paraphrase.

Useful constraint:
- if the final line sounds more general than `SELECTED_MAIN` or `SELECTED_SMALL`, reject it.

## Weather wording lesson

Even when the weather source is directly fetched, the rendered weather line should stay source-shaped and conservative.
Prefer:
- `в Москве сейчас +17 °C, переменная облачность; днём до +20 °C; дождь возможен`

Avoid synthetic confidence if the page only explicitly states the current conditions and the rest comes from parsed hourly blocks.

## Practical maintenance loop

1. Expand the bank.
2. Run validator.
3. Fix flagged lines.
4. Generate a test daily.
5. Compare the rendered output to the selected bank items.
6. If the renderer generalized them, tighten prompt rules.
7. Repeat until the final daily stays both short and concretely useful.
