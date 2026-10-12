# DuckDB backup-first salvage during live acceptance

Use when a local-first web runtime fails live acceptance because the canonical DuckDB file is corrupt or partially unreadable, but the current task still needs a grounded verdict.

## What to separate

Two truths can coexist:
1. the current product slice is implemented and passes build/code-level verification;
2. the live contour is still blocked by storage/runtime corruption.

Do not collapse (1) into "nothing is done" just because (2) is true.

## Safe recovery sequence

1. Stop the live backend.
2. Copy the canonical DuckDB file to a quarantine backup with timestamp.
3. Open the source DB read-only and confirm which tables are still readable.
4. Create a new clean DuckDB file with the app schema.
5. Clear any seed/bootstrap rows from the fresh DB before copying real data.
6. Bulk-copy readable tables into the clean DB.
7. Recreate or reset sequences so new inserts start above current max ids.
8. Swap the repaired DB into the canonical path only after counts/basic queries look sane.
9. Restart backend and verify at least: login, bootstrap, thread list, thread detail.
10. Only then resume feature acceptance or message-send validation.

## Common trap

A repaired DB can restore reads but still fail writes if sequence objects remain at their bootstrap start values. Treat sequence reset as part of the repair, not optional polish.

## Scope boundary

This pattern fixes storage/runtime integrity problems. It does not prove the upstream LLM/runtime path is healthy. After DB repair, re-check whether later failures are actually due to missing model/API contour rather than the database itself.
