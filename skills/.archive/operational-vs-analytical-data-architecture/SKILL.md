---
name: operational-vs-analytical-data-architecture
description: Audit and clean up local-first systems where runtime/application data and analytical DuckDB or reporting layers have become blurred, duplicated, or contradictory.
---

# Purpose

Use this skill when a local-first product has both an operational data store and an analytical/reporting hub, and the real problem is not "too many databases" but unclear source-of-truth boundaries.

Typical signals:
- The UI, backend, and analytics layer appear to show the same entities from different places.
- There is pressure to merge databases just to reduce visual complexity.
- A reporting hub has grown shadow copies of runtime tables.
- Jobs, ACL, users, messages, or similar entities exist both as operational tables and as lightly transformed copies in analytics.
- The right instruction is "do not touch UI until the data roles are clarified."

# Outcome

A clean architecture with:
- one canonical runtime source of truth;
- a separate analytical layer fed by explicit ETL/snapshots;
- no ambiguous shadow operational copies inside analytics;
- verification by code inspection and SQL counts;
- documented decisions and one non-duplicated refresh mechanism.

# Core rule

Do not treat an analytical hub as a second operational master.

If the application already has a functioning backend DB and API, prefer:
1. runtime truth in the application DB;
2. analytics as explicit imported raw snapshots plus analytical views;
3. UI unchanged until the data contract is clear.

# Workflow

1. Establish the real runtime path
- Inspect backend code to identify where CRUD and runtime reads actually happen.
- Inspect frontend code only enough to confirm whether it reads through backend API or directly from analytics.
- Name the canonical runtime DB/schema explicitly.

2. Separate facts from assumptions
Record:
- what tables exist in runtime;
- what tables/views exist in analytics;
- whether analytics contains shadow operational copies;
- whether analytical projections for the entity actually exist.

3. Decide source-of-truth boundaries
For each contested entity (jobs, ACL, etc.):
- choose exactly one runtime source of truth;
- decide whether analytics should keep:
  - no copy,
  - raw imported snapshot tables,
  - analytical views/materializations.

Preferred pattern:
- runtime DB: operational tables;
- analytics hub: `*_raw` imported snapshots + analytical views.

4. Remove transitional ambiguity
- Delete or stop rebuilding schemas/tables that act like a second runtime master inside analytics.
- Avoid keeping both legacy and new analytical paths alive unless there is a short, explicit migration window.

5. Build explicit ETL into analytics
Preferred sequence:
- attach runtime DB read-only;
- import required runtime tables into analytics raw tables;
- detach source DB;
- build analytical views on top.

Name tables and views so their role is obvious, for example:
- `app_*_raw` for imported runtime snapshots;
- `*_catalog`, `*_summary`, `*_matrix`, `*_open` for analytical projections.

6. Verify with facts, not vibes
Minimum verification:
- runtime row counts vs analytics raw row counts;
- schema presence/absence checks for deprecated layers;
- sample query from the new analytical view;
- syntax or compile check for refresh code;
- one full refresh run.

7. Automate refresh with one scheduler
- Pick one scheduling mechanism.
- Remove duplicate refresh jobs in other schedulers.
- Verify the actual execution path, not just the config file.

Important: the durable lesson is scheduler deduplication and execution verification, not any machine-specific interpreter path.

8. Document and log decisions
Update:
- architecture doc explaining operational vs analytical roles;
- README for the hub or data folder;
- decision log with context, agreed rule, and rejected alternatives.

# Pitfalls

- "Let’s merge everything into one DB for simplicity" when the real issue is role confusion.
- Leaving a reporting schema that still looks operational.
- Touching UI before the backend/runtime contract is clarified.
- Calling two different storage layers the source of truth for the same entity.
- Keeping two refresh mechanisms alive at once.
- Reporting success without row-count or query-level verification.

# Recommended deliverable structure

When Misha asks to fix or redesign the data contour "под ключ", do not artificially split the work into a sequence like "first a matrix, then later the real redesign" if the agent already has enough context to complete the architecture in one pass.

Default expectation for this user:
- deliver the real target data contour, not a preparatory artifact disguised as progress;
- include the full artifact set needed for implementation-quality closure: runtime source-of-truth boundaries, analytical projections, refresh logic, verification, architecture/docs updates, and the practical PMBook-like implementation artifacts implied by the change;
- use intermediate matrices only as an internal thinking aid or as a compact embedded section inside the final result, not as the stopping point.

If the target state is a "clean first launch" or production-like bootstrap, do not leave demo noise behind just because it helped during MVP exploration. In this mode the expected finish state is:
- minimal operational runtime data;
- one explicit bootstrap/admin user if required;
- reference dictionaries and configuration surfaces only;
- Hermes/runtime information shown as downstream truth;
- no synthetic chats, demo messages, demo jobs, or other fake activity whose main purpose is to make the UI look populated.

Add this as an explicit verification step when relevant:
- verify the runtime DB contains only the intended bootstrap entities after cleanup;
- refresh analytics and confirm summary views reflect the cleaned operational layer instead of stale demo state.

Summarize results in this order:
1. canonical runtime source of truth;
2. what was removed from analytics;
3. what ETL/raw tables were added;
4. what analytical views were added;
5. how refresh is automated;
6. what was verified by actual counts/queries;
7. what docs/decision-log entries were updated.

If the request implies a development deliverable rather than a pure advisory note, the task is not complete until the code, refresh path, and documentation reflect the new contour.

# References

See `references/runtime-analytics-boundary-checklist.md` for a concise checklist and naming guidance.
