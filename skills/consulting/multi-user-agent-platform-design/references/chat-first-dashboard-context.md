# Chat-first dashboard context

## When to use
Use this pattern when:
- chat is the broad-audience entry point;
- users may discuss data, conclusions, or business questions in free form first;
- the product should be able to convert discussion into a dashboard without turning the whole chat into a BI screen.

## Core idea
Do not build a dashboard directly from raw chat text.

Instead use:
1. chat conversation;
2. structured `dashboard_context` extracted from the conversation;
3. explicit user action such as `Build dashboard`;
4. backend enrichment / computation;
5. dashboard rendering.

## Why this matters
Without an intermediate context object, the system tends to:
- overfit to the latest chat turn;
- mix facts, guesses, and narrative fragments;
- present inferred numbers as if they were canonical data;
- surprise the user with opaque visualisations.

## Recommended object shape
A minimal `dashboard_context` should capture:

- `topic`: what the dashboard is about;
- `question`: the current analytical question;
- `time_range`: explicit or inferred period;
- `entities`: users, chats, jobs, channels, projects, etc.;
- `metrics`: requested or discovered measures;
- `confirmed_values`: values already backed by source data;
- `computed_values`: values derived from confirmed data by a known rule;
- `hypotheses`: interpretations or tentative statements;
- `sources`: backend endpoints, files, datasets, message ids;
- `filters`: relevant slices and constraints;
- `gaps`: what is still missing;
- `suggested_widgets`: cards, lines, bars, lists, heatmaps, comparisons;
- `confidence`: optional coarse confidence marker.

## Provenance discipline
Every number or claim in the rendered dashboard should fall into one of three groups:
- confirmed: directly from backend/files/source data;
- computed: produced from confirmed data by a deterministic calculation;
- inferred: interpretation, estimate, grouping, or hypothesis.

This distinction should be available to the UI and visible to the user when relevant.

## UX flow
Recommended MVP flow:
1. user discusses the topic in chat;
2. agent incrementally accumulates or refreshes `dashboard_context`;
3. `Build dashboard` button is always available;
4. on click, show a short preview:
   - topic;
   - period;
   - metrics found;
   - confirmed data available;
   - missing pieces;
5. if enough is known, render the dashboard;
6. if not enough is known, ask for the smallest missing input or explain the limitation.

## Product guardrails
- Do not auto-open dashboard mode on every analytical-looking chat turn.
- Do not send the entire raw thread into the visual layer unless a summarisation step explicitly bounded it.
- Do not let the LLM fabricate numeric fills for missing backend data.
- Do not hide uncertainty when the dashboard is partly hypothesis-driven.
- Do not make Copilot the source of truth; backend remains the source of truth.

## Good first MVP positioning
Best framing:
- chat is where the question and context are formed;
- dashboard is where the current understanding is made visual and inspectable.

Good button labels:
- Build dashboard
- Visualise discussion
- Open analytics view

Less ideal framing:
- magical auto-dashboard from any message;
- treating the whole chat as a dashboard definition without user confirmation.
