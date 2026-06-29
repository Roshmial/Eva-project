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
- the user asks for a dashboard, analytics board, market overview, comparative picture, review/overview, trend view, segmentation, or evidence board;
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
1. Identify business function when the request is about operating metrics (for example sales, marketing, finance, operations, support, HR, product, procurement).
2. Identify analytical intent.
3. Estimate data shape and confidence.
4. Select 2-5 sections that best match the task.
5. Ensure at least one visible visual section when any meaningful quantitative slice exists.
6. Add a limitation/caveat block instead of pretending precision.

## Business-function axis for source-agnostic dashboards

When the user asks for a metrics dashboard, do not anchor the product concept to the source artifact (`file dashboard`, `CSV dashboard`, `CRM export dashboard`). The stable semantic layer should be:
- `business function` — what operating area is being analyzed;
- `analytic intent` — what question is being asked of the data;
- `source shape` — where the data came from and what its constraints are.

Use source only to explain evidence quality, freshness, and field availability. Use business function to decide which metrics and visuals are appropriate.

Practical rules:
- Prefer titles/subtitles/cards framed around the business function (`Продажи`, `Маркетинг`, `Финансы`) rather than around the transport (`по файлу`, `CSV`, `выгрузка`) when the dataset clearly represents an operating domain.
- Treat file-driven analytics as one input path into a shared `business_function_analytics` layer, not as a separate product mode with its own bespoke dashboard grammar.
- For function inference, weight explicit words from the user request more strongly than ambiguous column hints. Example: a marketing dataset may contain `leads`, but if the request is explicitly about campaigns/channels/marketing performance, the dashboard should stay in `marketing`, not slide into `sales`.
- Keep `analytic intent` and `business function` separate: `trend + marketing`, `comparison + procurement`, `evidence_board + finance`, and similar combinations should all be possible.
- Treat `review` as a first-class intent for overview-style requests (`обзор`, `что это такое`, `как устроено`, `как развивалось`, `общая картина`). Do not force such requests into `history` only or into generic `market overview` when the real ask is explanatory synthesis.
- When the source is weak or mixed, preserve the function label but downgrade certainty in notes/limitations rather than reverting to a source-centric dashboard identity.
- Prefer a reusable reference/spec layer for intent/function guidance over growing backend-only prompt strings. Backend should orchestrate; reusable grammar should live in policy/reference artifacts when possible.

Typical function-level metric grammar:
- `sales` → revenue, deals, average deal size, funnel/stage conversion, manager/channel contribution, period trend.
- `marketing` → leads, campaign/channel mix, cost, conversion, contribution by channel/campaign, period trend.
- `finance` → income, expenses, margin, budget-vs-actual, deviations by category, period trend.
- `operations` → throughput, SLA attainment, cycle time, backlog/load, bottlenecks.
- `support` → tickets, first response, resolution time, backlog, category mix, SLA breaches.
- `hr` → headcount, hires, attrition, retention, funnel/time-to-hire, breakdown by team/location.
- `product` → activation, adoption, usage, retention, feature contribution.
- `procurement` → spend, supplier concentration, lead times, deviations, vendor breakdown.
- `it_analytics` → incidents, availability/uptime, latency/performance, MTTR, deployment/change quality, service breakdown.
- `security` → vulnerabilities, incidents, control coverage, access risk, severity distribution, remediation trend.

## User-facing metric design rules

When the dashboard is built from datasets or mixed structured evidence, do not stop at technical column summaries such as `main metric = <column_name>` or generic bars with no interpretation. The dashboard must explain what the metric means for the user.

Practical rules:
- Prefer user-facing metric labels over raw field names. Example: `incident_count` should surface as `Инциденты`, `uptime` as `Средняя доступность`, `latency_ms` as `Типичная задержка`, `mttr_hours` as `MTTR` or `Среднее время восстановления`, `control_coverage` as `Покрытие контролей`.
- Summary cards should include short explanatory `note` text that answers `что это значит` or `как это читать`, not only provenance.
- Section-level `note` text should explain the purpose of the visual: what pattern the user is supposed to see and why it matters.
- Prefer dynamic metric derivation from detected domain signals over a hardcoded one-column fallback. The system should inspect available numeric fields and pick the most relevant metrics for the inferred business function.
- If the dataset exposes a weak proxy rather than a canonical KPI, present it as a proxy with a caveat instead of pretending it is the official metric.
- Use best-effort derivations that remain understandable: totals, averages, concentration, distribution by severity, availability, incident trend, latency profile, backlog size, coverage level, and similar patterns. Avoid pseudo-precision that looks mathematically rich but is not explainable to the user.
- When direct KPI columns are missing, prefer a semantic mapping pass before giving up: look for `plan/fact`, numerator/denominator rate pairs, ageing buckets, and cohort/retention structures. This is the next layer above plain column-marker matching.
- If a semantic pattern is found, surface it with user-facing labels and explanatory notes rather than raw structural names. Example: `resolved/opened` -> `Resolution rate`, `budget/actual` -> `Plan vs Actual`, `overdue_0_30/31_60/...` -> an ageing section, `retention + cohort` -> retention card plus cohort timeline.
- After that v1 layer, prefer a second semantic pass for multi-column business constructs: funnel step chains (`lead -> qualified -> won`, `signup -> activated -> retained`), inflow/outflow backlog pressure (`created/opened` vs `completed/resolved` plus backlog), and concentration/risk patterns (top vendor/channel/feature/team share). These patterns should produce dedicated cards/sections rather than hide inside generic category bars.
- For funnel semantics, build both a section with stage totals and a user-facing card for end-to-end conversion when at least two meaningful stages are present.
- For inflow/outflow semantics, prefer explicit pressure-oriented cards such as `Inflow vs Outflow`, `Flow clearance rate`, and `Pressure on backlog` instead of showing backlog alone.
- For concentration semantics, compute the share of the largest category and expose it as a dependency/risk signal only when that concentration meaningfully implies operational dependence.
- Then prefer a v3 semantic pass when the dataset supports it: grouped `plan/fact` sections (not only row-level delta), grouped concentration across slices (`period -> channel`, `category -> vendor`, `period -> team`, `period -> feature`), and explicit source-shape bridging (`file_export`, `web_structured`, `structured_source`) that adds context without reverting to a source-centric dashboard identity.
- Treat that v3 layer as shared semantic infrastructure, not as a dataset-only flourish. If external or web-structured dashboards are normalized through the same product surface, they should also expose the same semantic envelope where possible: `business_function`, source-shape context, and honest summary cards such as `Функция` and `Форма источника`.
- When bridging dataset path and external dashboard path, keep source shape in the subtitle/context layer (`source shape: ...`) and in summary cards, but do not let it replace the business framing. `source shape` explains evidence provenance; `business_function` explains what the dashboard is about.
- For external market/procurement/vendor dashboards, do not rely on a tiny set of Russian-only markers. Intent detection should explicitly recognize market-language variants such as `market`, `landscape`, `игрок`, `конкурент`, `vendor landscape`, `supplier landscape`, otherwise honest market-overview requests may degrade into `evidence_board` or overly generic review flows.
- When shares and percentages are mixed in the same dataset (`0.42` next to `48`), normalize them to one user-facing percent scale and round them before payload emission so the dashboard avoids floating-point noise and unstable assertions.

### Function-specific expectations for explainable metrics

For `it_analytics` dataset dashboards:
- Prefer dynamic cards for incidents, availability, latency/performance, and MTTR when matching numeric fields exist.
- If a date/period field exists, add a trend section for incidents or other operational load over time.
- Performance sections should distinguish the typical level from the heavy-tail / degraded cases; a user must understand whether the issue is constant slowness or rare spikes.

For `security` dataset dashboards:
- Prefer dynamic cards for vulnerability backlog, control coverage, and average/peak risk signals when matching numeric fields exist.
- If severity/priority/criticality exists, add a dedicated distribution section so the user sees whether risk sits in a few critical issues or in a broad medium backlog.
- Explain control coverage in plain language: what is covered, what is not, and why a higher percentage matters.

## Extending business-function coverage without drift

When adding a new business-function dashboard pack, extend the routing/spec layer and the reusable guidance layer in the same pass.

Practical rule:
- if backend function detection lives in a policy/spec artifact (for example `business_dashboard_functions.json`), and prompt guidance lives in a reusable reference dataset (for example `dashboard_grammar`), update both together;
- do not add a new function only to routing or only to prompt guidance, because that creates semantic drift where the system can classify a request into a function the agent has no dedicated grammar for, or the reverse;
- add at least one regression that checks function detection and one regression that checks prompt/reference guidance for the new function.

This dual-layer update pattern is especially important once dashboard coverage grows beyond business basics into adjacent operational domains such as `it_analytics` and `security`.

Typical intents:
- review / overview
- market overview
- trend / dynamics
- comparison
- segmentation
- evidence board
- history / evolution

## UX rules

- No accordion, collapsed sections, or hidden meaning.
- Important content must be visible immediately.
- KPI cards alone are not enough when a visual slice is possible.
- If numbers are weak, still keep a minimal visual scaffold plus explicit caveats.

## Intent-aware fallback and normalization rules

When upstream collection or LLM synthesis is weak, do not fall back to technical stubs like `Минимальная визуализация`, cards about `source_mode/global_only`, or a chart whose only payload is the connector/source label. Those blocks may be technically valid JSON, but they are analytically useless and degrade user trust.

Use intent-aware minimal content instead:
- `market_overview` → players, market signals, positioning, constraints;
- `comparison` → criteria, differences, trade-offs;
- `trend` → dynamics, turning points, drivers;
- `segmentation` → segments, distinctions, grouping criteria;
- `history_evolution` → stages plus shifts in role/practice/architecture;
- `evidence_board` → what is confirmed, what is missing, source-backed examples.

Practical rules:
- Summary cards should describe the analytical focus and constraints, not backend routing internals.
- Fallback sections should preserve meaning even when the payload is thin; they must not merely prove that a renderer can draw a section kind.
- `comparison` should usually elevate `matrix_list` into the primary visual set; a plain text summary plus low-priority bars is usually the wrong default.
- `evidence_board` should prefer `post_list`/evidence-style sections and explicit gaps over generic visual placeholders.
- `history_evolution` must avoid duplicating the same text in both `timeline_list` and `matrix_list`; the matrix should show a different analytical slice (for example shifts by role, architecture, or operating model), not a second numbering of the same stages.
- If there is not enough evidence for a real quantitative chart, prefer a contentful text/matrix/post fallback with clear caveats over fake chart-like filler.

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
- Do not build fake visual sections from technical routing/policy metadata such as `source_mode`, `global_only`, connector labels, or source names when those fields are not the analytical data the user asked to see. A `bar_list` or `pie_list` whose only payload is the source label and a policy token is not a dashboard — it is a misleading fallback.
- If the collected evidence is too thin for a real visual slice, prefer an honest evidence/text board with explicit caveats over placeholder charts.
- For web-collected dashboards, do not treat “some fetched pages exist” as sufficient evidence. Source relevance is part of dashboard honesty: if the fetched pages are off-topic, the correct behavior is to reject the evidence set or continue searching, not to produce a formally pretty dashboard on irrelevant documents.

## Source relevance rules for web-collected dashboards

When the dashboard depends on open-web collection:
- validate the chain `query -> candidate URLs -> fetched documents -> dashboard sections`, not just the final JSON envelope;
- score URL candidates against the analytical subject before fetch, especially for short IT acronyms and hybrid Russian/English subjects such as `BI`, `ERP`, `CRM`, `OLAP`, `DSS`;
- expand important acronyms into domain terms when building search intent (for example `BI -> business intelligence`, `OLAP -> online analytical processing`, `DSS -> decision support system`), otherwise search may drift into irrelevant generic pages;
- for historical / evolution requests, prefer focused domain queries (for example `"business intelligence" history evolution OLAP DSS data warehousing`) over the raw full user sentence;
- do not stop at the first non-empty candidate set. Compare candidate sets across queries and select the most relevant set, because the first query may return generic or polluted results while a later focused query returns the actual domain sources;
- after fetch, require at least one subject match in the document set. If nothing relevant survives, fail honestly instead of building a dashboard on irrelevant help pages, generic support articles, or unrelated product docs.

## Runtime / product pitfalls

- Distinguish a renderer bug from a bad dashboard payload. If the UI shows a "bullshit dashboard", first inspect the actual stored `dashboard_result` payload for the affected user/thread. A formally valid envelope can still contain semantically fake sections.
- Treat short follow-up complaints like "где сам дашборд?", "это не дашборд", or similar as repair signals for the previous dashboard result, not automatically as a brand-new dashboard request based only on the latest short user message. Reuse the prior user request and previous dashboard payload when deciding whether to rebuild, repair, or clarify.
- For live acceptance, validate the full chain `user request -> collected sources -> analytics payload -> rendered dashboard`. Do not stop at "the container rendered" when the user is complaining that the dashboard content is wrong.

## References
- `references/business-dashboard-reference-layer-and-review-intent.md` — how to introduce a reusable dashboard grammar/reference layer and when to use a first-class `review` intent for overview/explanatory dashboards.
- `references/business-function-metrics-layer.md` — how to evolve dashboards from file-centric analytics to source-agnostic business-function routing, including function-vs-intent-vs-source separation and function inference pitfalls.
- `references/dashboard-fallback-and-followup-routing-lessons.md` — pitfalls from live debugging where a dashboard looked present in UI but backend had produced a pseudo-dashboard from thin evidence and mishandled a short follow-up complaint.
- `references/web-source-relevance-and-historical-dashboard-lessons.md` — lessons for open-web dashboards where the envelope looked valid but source acquisition was off-topic; includes query-shaping and candidate-set selection guidance.
- `references/intent-aware-contentful-fallbacks.md` — practical fallback grammar for market/comparison/trend/segmentation/history/evidence dashboards; covers anti-stub rules and how to keep weak payloads analytically useful.
- `references/dynamic-explainable-metrics.md` — practical rules for turning dataset fields into user-facing metrics with explanatory notes, dynamic derivation, and function-aware examples for IT analytics and security.
- `references/semantic-metric-mapping-v1.md` — semantic layer above plain column matching: plan/fact, derived rates, ageing buckets, and cohort/retention patterns for dataset dashboards.
- `references/semantic-metric-mapping-v2.md` — next semantic layer for multi-column business constructs: funnel chains, inflow/outflow backlog pressure, and concentration/risk patterns.

- `references/semantic-metric-mapping-v3.md` — grouping-aware semantic layer for dataset dashboards: grouped `plan/fact`, concentration across slices, mixed share/percent normalization, and source-shape bridging.
- `references/shared-semantic-core-and-source-shape-bridging.md` — how to unify dataset and external dashboards under one semantic envelope (`business_function` + `source shape` + shared guidance) without sliding back into source-centric dashboard identity.

- `references/adaptive-v1-implementation-notes.md` — implementation notes for turning the grammar into a backend/frontend contract, including normalization, fallback behavior, and a tunnel/gateway diagnostic note.
- `references/telegram-stacked-day-chart-lessons.md` — lesson note for period dashboards where one combined day-by-day stacked chart is required instead of separate day objects or duplicated auxiliary sections.

## Verification checklist

- [ ] The result uses the stable envelope.
- [ ] Sections are chosen by task intent, not by habit.
- [ ] At least one visual section is present when quantitative structure exists.
- [ ] Limitations are explicit when precision is weak.
- [ ] No collapsed/placeholder-only sections.
