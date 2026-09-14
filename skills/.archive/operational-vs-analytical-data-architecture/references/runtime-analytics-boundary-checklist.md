# Runtime vs analytical boundary checklist

Use this checklist when a local-first app has both an application DB and an analytical hub.

## 1. Runtime truth

Confirm with code and live DB inspection:
- Which backend DB/schema serves writes?
- Which backend endpoints serve the entity?
- Does frontend call backend API or analytics directly?

Write down one sentence:
- `Canonical runtime source of truth for <entity> is <db/schema/table family>.`

## 2. Analytical role

For each entity, choose one:
- no analytical copy needed;
- imported raw snapshot needed;
- analytical views/materializations needed.

Preferred naming:
- raw imported tables: `<source>_<entity>_raw`
- catalog/list view: `<entity>_catalog`
- rollup view: `<entity>_summary`
- matrix view: `<entity>_access_matrix`, `<entity>_delivery_matrix`
- filtered operationally-interesting view: `<entity>_open`

## 3. Transitional cleanup

Look for these anti-patterns:
- old analytics schema still rebuilt during refresh;
- analytics contains tables that pretend to be the app runtime;
- both old and new paths survive without a written migration window.

If found, remove the transitional layer from the refresh path.

## 4. ETL pattern

Preferred local-first pattern:
1. attach runtime DB read-only;
2. copy required tables into analytics raw tables;
3. detach runtime DB;
4. build analytical views;
5. record refresh metadata and row counts.

## 5. Verification pack

Minimum evidence before declaring done:
- deprecated schema absent or no longer rebuilt;
- raw count parity between runtime and analytics for imported entities;
- one sample query from the new analytical views;
- refresh script syntax/compile check passes;
- one full refresh run succeeds;
- scheduled refresh mechanism is active;
- duplicate schedulers removed.

## 6. Documentation updates

Update all three if they exist:
- data-layer README;
- architecture note;
- decision log.

Recommended decision-log fields:
- Context
- Agreed
- Rejected
- Model / stack / tools
- Reflection

## 7. What not to encode as a durable rule

Do not turn session-specific environment quirks into permanent rules, for example:
- a temporary missing package in one interpreter;
- a path mismatch fixed during setup;
- a one-off service failure that disappeared after the correct runner was used.

Capture the general lesson instead:
- verify the scheduler’s real execution path;
- avoid duplicate refresh mechanisms;
- verify with SQL counts and live runs, not only config inspection.
