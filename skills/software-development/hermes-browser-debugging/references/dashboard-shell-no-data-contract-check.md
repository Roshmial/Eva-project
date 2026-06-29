# Dashboard shell renders but content is empty

Use this when the UI visibly renders the dashboard/container/card, but the inner sections appear empty or nearly empty.

## Core diagnosis
If the shell is present, the browser/runtime layer is often already good enough. The next check is application-contract shape:

1. Capture the live backend payload for the exact message/thread.
2. Verify where the dashboard lives (`message.meta.dashboard`, `dashboard_artifact`, another key).
3. Compare the exact payload shape with what the frontend renderer reads.
4. Pay special attention to section grammar, not just top-level existence.

## High-value comparison points
Check whether the live payload uses any of these forms:

- `section.kind = "text_list"` with `items` as plain strings
- `section.kind = "text_list"` with `items` as objects like `{ text, meta }`
- `section.kind = "bar_list"` with chart rows under `items`
- `section.kind = "pie_list"` with chart slices under `items`
- metric values encoded as `ratio`, `meta`, or string values instead of numeric `value`

A common failure mode is that the renderer only supports structures like:
- `section.bar_list`
- `section.pie_list`
- `section.bullet_list`
- `{ label, value, description }`

while runtime actually sends grammar-first sections through `section.kind + section.items`.

## Practical repair pattern
When the mismatch is confirmed, prefer a narrow UI fix:

- branch on `section.kind`
- normalize `items` into the component-friendly shape
- support plain strings and `{ text, meta }` objects in text-list sections
- support chart sections whose rows live under `items`
- preserve the old path too, so legacy payloads still render

## Example from this session class
A live dashboard had real data:
- `summary_cards len > 0`
- `sections len > 0`
- `sources len > 0`

But the UI showed only the dashboard shell because sections arrived as:
- `kind: "text_list"`, `items: ["..."]`
- `kind: "text_list"`, `items: [{"text": "...", "meta": "..."}]`
- `kind: "bar_list"`, `items: [...]`
- `kind: "pie_list"`, `items: [...]`

The renderer was looking for `section.bar_list`, `section.pie_list`, and rich bullet objects, so it silently rendered almost nothing.

## Decision rule
Once the shell is visible, do not keep reinstalling browser libraries or re-diagnosing CDP first unless a new browser symptom appears. Treat "shell yes, data no" primarily as a payload-shape / renderer-contract investigation.
