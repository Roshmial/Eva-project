# Research dashboard routing notes

Use this reference when chat routing drifts from user intent into backend intake mechanics.

## Anti-pattern

A user asks:
- `Проанализируй рынок ... и построй дашборд`
- `Собери информацию из интернета`

Backend responds with blocking clarification like:
- `откуда собираем`
- `что именно собирать`
- `какие поля обязательны`

This is usually a misclassification from `research/dashboard request` into `dataset contract intake`.

## Preferred routing behavior

1. If the request is analytical/research-oriented and the deliverable is `dashboard`, allow `web` or open sources as the default source when topic is recognizable.
2. Do not require mandatory result columns for dashboard delivery unless the user explicitly asks for a dataset/export.
3. Treat short source-only follow-ups (`из интернета`, `по открытым источникам`, `с сайта`) as context completion for the previous substantive user request.
4. Extract the subject from the actual dashboard topic (`дашборд по ...`), not from service phrases like `данные в интернете`.
5. Avoid accidental history routing from year tokens alone (`2024`, `2025` are not enough to mean `history_evolution`).

## Regression ideas

- `Проанализируй рынок автомобилей Geely в России в 2024-2025 годах и построй дашборд`
  - expected: action-ready web/dashboard route
  - not expected: blocking clarification about mandatory fields

- previous user request about a market/topic + follow-up `Собери информацию из интернета`
  - expected: merged effective request based on previous topic
  - not expected: fresh empty intake
