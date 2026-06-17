---
name: adaptive-dashboard-grammar
description: Use when Hermes must build dashboard-style responses without relying on one fixed template. Enforces a stable envelope, section grammar, and selection policy based on task intent and data shape.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [dashboard, analytics, grammar, local-first, hermes-web]
    related_skills: [turnkey-local-first-mvp-delivery, misha-response-delivery]
---

# Adaptive Dashboard Grammar

## Lessons from Hermes Web dashboard selection

- Для visual-first дашбордов по умолчанию отдавай приоритет графическим секциям над длинными текстовыми списками. Текст — это поясняющий слой, а не основной объём результата.
- Если вопрос про доли/структуру/распределение рынка между 3–8 игроками, одним из первых visible blocks должен быть `pie_list` или `donut_list`. `bar_list` полезен вторым слоем для точного сравнения, но не должен вытеснять composition-визуализацию.
- Если в данных есть факторный анализ с весами, приоритетами, вкладом факторов или хотя бы approximate importance, не ограничивайся перечислением факторов текстом: добавляй отдельную диаграмму, обычно `bar_list`, чтобы пользователь видел не только состав факторов, но и их относительную силу.
- Для user-facing delivery считай anti-pattern'ом дашборд, который можно было бы показать как графически насыщенный, но он всё равно приходит как `bar_list + text_list + длинные абзацы`. Если есть количественная структура, вытаскивай её в визуальные секции первыми.

## Overview

This skill is for dashboard-like analytical answers where one canonical dashboard layout would be too rigid. Instead of forcing a single template, Hermes should keep a stable outer envelope and choose the most useful sections for the task.

## When to use

Use when:
- the user asks for a dashboard, analytics board, market overview, comparative picture, trend view, segmentation, or evidence board;
- the response should be visibly structured in UI, not just a long prose answer;
- the available data shape may differ from one request to another.

Do not use when:
- the user only needs a plain textual answer;
- there is not enough data even for a minimal structured board and a clarification is more honest.

## Stable envelope

Keep the outer contract stable:
- `kind`
- `title`
- `subtitle`
- `summary_cards`
- `sections`
- `sources`
- `notes` or limitations when confidence is constrained

The envelope should be product-stable even if the inner section mix changes.

## Section grammar

Prefer a composable grammar of blocks rather than hand-made full dashboards.

Core section types:
- `text_list` — facts, caveats, takeaways
- `bar_list` — comparisons, rankings, simple quantitative slices
- `pie_list` — composition / share structure
- `bubble_list` — relative weight / salience
- `post_list` — examples, evidence, source snippets, top items
- `timeline_list` — chronology, trends, turning points
- `matrix_list` — segments × criteria, grouped comparison

## Selection policy

Choose sections in this order:
1. Identify analytical intent.
2. Estimate data shape and confidence.
3. Select 2-5 sections that best match the task.
4. Ensure at least one visible visual section when any meaningful quantitative slice exists.
5. Add a limitation/caveat block instead of pretending precision.

Typical intents:
- market overview
- trend / dynamics
- comparison
- segmentation
- evidence board

## UX rules

- No accordion, collapsed sections, or hidden meaning.
- Important content must be visible immediately.
- KPI cards alone are not enough when a visual slice is possible.
- If numbers are weak, still keep a minimal visual scaffold plus explicit caveats.

## Delivery contract for Hermes Web dashboards

When the user asks for a `dashboard_result` or gives an explicit JSON schema:
- return only the JSON object with no prose before or after it;
- keep the envelope exact and product-stable;
- prefer visibly rich sections over placeholder headings or prose-heavy filler;
- never hide key meaning behind clicks, collapses, or deferred reveals.

## Intent-specific guidance: trend / dynamics

For trend-oriented requests:
- prioritize `summary_cards`, `timeline_list`, and at least one comparative visual block such as `bar_list`;
- if there are at least two quantitative slices, include at least two visible visual sections rather than only KPI cards;
- explicitly call out turning points, slope changes, and what likely caused them;
- when the user asks for shares but the public market only exposes partial signals, you may provide an analytical estimate only if it is clearly labeled as an estimate in `note`/`meta`/`notes` and not presented as an audited fact.
- if the user asks for a grouped/combined histogram by periods and categories, do not flatten the payload into one long `bar_list` with labels like `day — type` unless the renderer explicitly knows how to regroup it. A flat list may be formally valid JSON but is product-wise the wrong visualization.
- safe pattern for grouped bars: each item may still live in `bar_list`, but must carry an explicit series marker such as `meta: series=<category>; total_day=<n>`, and the renderer should regroup by the primary bucket (for example day) before drawing. If that regrouping path does not exist yet, do not pretend the chart is already solved — either add the renderer support or choose a simpler visual form honestly.
- when the user asks for a single combined chart, do not render one card/object per primary bucket. The correct UX target is one combined chart object containing multiple buckets inside the same visual.
- the primary axis may be numeric or categorical; the inner composition should be rendered as categorical stacked segments inside each bucket.
- if one combined stacked chart already tells the main story, do not keep auxiliary sections that duplicate the same picture unless the user explicitly asked for them.
- for top-N category compression in combined dashboards, do not drop non-top categories to zero. Aggregate the remainder into an explicit `прочее` series so bucket totals stay truthful.

## Honesty rules

- Do not invent metrics.
- Do not convert weak signals into certain conclusions.
- If local data is absent or insufficient, say so directly and either ask for scope/source clarification or switch to external overview mode if policy allows.

## References

- `references/adaptive-v1-implementation-notes.md` — implementation notes for turning the grammar into a backend/frontend contract, including normalization, fallback behavior, and a tunnel/gateway diagnostic note.
- `references/telegram-stacked-day-chart-lessons.md` — lesson note for period dashboards where one combined day-by-day stacked chart is required instead of separate day objects or duplicated auxiliary sections.

## Verification checklist

- [ ] The result uses the stable envelope.
- [ ] Sections are chosen by task intent, not by habit.
- [ ] At least one visual section is present when quantitative structure exists.
- [ ] Limitations are explicit when precision is weak.
- [ ] No collapsed/placeholder-only sections.
