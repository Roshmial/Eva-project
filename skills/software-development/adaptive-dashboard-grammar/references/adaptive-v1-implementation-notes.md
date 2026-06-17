# Adaptive Dashboard Grammar v1 — implementation notes

Use this reference when turning dashboard-like answers into a product-stable UI contract.

## Core idea

Do not force one universal dashboard template.

Use three layers:
1. Stable envelope
2. Typed section grammar
3. Selection policy based on intent and data shape

## Stable envelope

Keep these fields stable even when inner composition changes:
- `kind`
- `title`
- `subtitle`
- `summary_cards`
- `sections`
- `sources`
- `notes`

## Recommended intents

- `trend`
- `segmentation`
- `comparison`
- `market_overview`
- `evidence_board`

## Recommended section kinds

- `text_list`
- `bar_list`
- `pie_list`
- `bubble_list`
- `post_list`
- `timeline_list`
- `matrix_list`

## Backend responsibilities

The backend should not trust model output as-is.

Minimum backend post-processing:
- normalize unknown section kinds to allowed ones;
- coerce sparse items into renderer-safe shapes;
- ensure `summary_cards`, `sections`, and `sources` always exist;
- add fallback sections when the model returns too little structure;
- keep explicit caveats when numbers are weak;
- stamp a grammar version marker in metadata.

## Frontend implications

Frontend should render the stable envelope and supported section kinds only.
If grammar evolves, renderer support must be extended deliberately instead of silently ignoring new section types.

## UX rule for this class of task

Avoid pseudo-dashboards made of headers with no visible payload.
If the data is weak, still show a minimal visual scaffold plus a clear caveat block.

## Operational note

If the user reports a message like `no tunnel here :(`, treat it as likely tunnel/proxy/gateway-layer output unless proven otherwise. That string is not inherently a Hermes dashboard error and may indicate the request never reached the app.
