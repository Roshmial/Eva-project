# Operational backend DB vs analytical DuckDB hub

Use this pattern when a local web/backend product and an analytical Hermes data hub begin to overlap.

## Core rule
Do not let one DuckDB file serve both as:
- the live application database for frontend/runtime CRUD;
- the long-horizon analytical hub for Hermes history, parsed artifacts, and operator notes.

Even if separate schemas technically work, the ownership boundary becomes muddy and future cleanup gets harder.

## Better split
- Application DB:
  - separate DuckDB file;
  - owned by backend code;
  - contains auth, users, sessions, messages, jobs, feedback, and other operational state.
- Analytical hub:
  - separate DuckDB file;
  - owned by refresh/import scripts;
  - contains Hermes history, Telegram/tender parsings, source-file registry, derived views, and decision-support datasets.

## What to move into the analytical hub
Besides raw parsings and Hermes history, it is often worth ingesting stable operator context files:
- `interaction-notes.md`
- `decision-log.md`

Treat them as first-class datasets and add small query-friendly views rather than rereading raw files in every session.

## Useful analytical views
Examples:
- current interaction notes view;
- latest decision-log entries view;
- session completion-status view;
- unresolved Hermes user requests view.

## Status modeling pattern
For faster operator diagnostics, add explicit status fields during refresh:
- message-level request status: `done` / `not_done`;
- session-level completion status;
- optional pointers to last user and last assistant messages.

This is better than inferring unresolved work from ad-hoc transcript reading each time.

## Transfer rule
If app data must appear in the analytical hub, copy it by explicit ETL/refresh.
Do not keep runtime coupling where the backend boot path depends on the analytical hub being present or shaped a certain way.

## Cleanup rule
If a transitional copy remains in the hub during migration verification, mark it as temporary and retire it after a short observation window.
