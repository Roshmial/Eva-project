# Style and rollout notes

Session distilled: May 2026 refinement of Eva's self-development cron messages for Misha.

## Durable user-facing requirements

- Morning message opens with `Доброе утро, Миша!`.
- Tone: economical, natural, polished, practical.
- Avoid sounding like an info-product coach or inspirational channel.
- Fewer explanations about meaning or importance; more direct framing of the day.
- Daily message should feel like one realistic day plan, not a mini-essay.

## Daily content shape

Target structure:
1. short contextual opening for today;
2. 1 main goal;
3. 2 small supporting goals;
4. optional compact closing line only if it adds value.

Interpretation rules:
- On weekdays, the main goal is usually work/productivity-oriented.
- On weekends, the main goal is usually reset, clarity, recovery, or self-development.
- Small goals should be lighter and should not compete with the main goal.
- Small goals must be concrete and explicit, with one action per goal.
- Avoid menus inside a small goal and avoid vague placeholders like "что-нибудь", "куда-нибудь", or "например".
- Prefer naturally spoken wording over abstract helper phrases.
- Do not use artificial transitions like `сменить контекст`.

## Relevance enrichers

- Use Moscow weather by default.
- Small-goal selection should react to both weather and weekday/weekend mode.
- If weather is poor, do not default to outdoor walking suggestions.
- If adding a Moscow leisure option, include only one concrete option with one link.
- Prefer a specific current event from a reliable organizer over a generic landing page.
- If nothing clearly good is available, omit the leisure suggestion.
- Leisure lead-ins should sound conversational, for example: `Если захочется куда-то выбраться` or `Если будет настроение выйти`.

## Rollout discipline

- Test with `deliver=local` first.
- Manual test runs and scheduled live runs can look like duplicates to the user; verify before assuming a scheduler problem.
- Do not keep test and live self-development jobs active in parallel.
- Promote to live delivery only after explicit user approval.

## Example of acceptable weekly compactness

The weekly review can stay brief if each section is 1–2 short sentences:
- Что получилось.
- Что мешало.
- Главный фокус следующей недели.
- Две поддерживающие вещи.
- Один короткий вывод от Евы.

The goal is a grounded weekly checkpoint, not a reflective essay.
