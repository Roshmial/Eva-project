# Tiered session retention

Use this when session-history cleanup is motivated by database growth rather than by a user wanting particular conversations erased.

## Retention model

Choose age thresholds from observed access patterns and available disk; do not hard-code universal numbers.

- Hot: raw sessions remain online and fully searchable.
- Warm: raw messages may remain online with rebuildable or bulky tool payloads compacted; preserve decisions and artifacts exactly.
- Cold: a thesis-style summary remains online and searchable while the raw session lives in a compressed, verified archive.
- Protected: pinned, active, unresolved, compliance-relevant, or explicitly important sessions remain raw regardless of age.

## Summary contract

Create one summary per source session with stable fields:

- source session identifier and archive locator;
- original task and relevant context;
- decisions with reasons;
- rejected alternatives and why;
- facts, constraints, and user preferences learned;
- verified actions and results, clearly separated from hypotheses;
- artifacts, file paths, URLs, commits, and other durable handles;
- unresolved questions and next actions;
- message identifiers or ranges supporting important claims.

Do not copy full logs or long tool output. Preserve exact identifiers and status semantics such as implemented, unmeasured, failed, or pending.

## Safety gates before pruning raw online data

1. Create a transactionally consistent raw archive or bounded per-session exports.
2. Verify archive integrity with the format's own checker and a checksum.
3. Generate summaries without overwriting source sessions.
4. Validate schema completeness and check that important decisions and artifacts survived.
5. Search for several known topics through summaries.
6. Follow summary pointers into the raw archive and inspect or restore a sample.
7. Run the prune command in dry-run mode and review protected-session exclusions.
8. Obtain explicit approval for destructive pruning.
9. Prune in bounded batches, then rebuild indexes or VACUUM only when appropriate.
10. Re-measure size, integrity, search quality, and restoreability before deleting temporary snapshots.

## Failure handling

- If summarization fails or is incomplete, retain the raw online session.
- If a whole-database export exhausts memory, split by session/time range or archive a consistent database snapshot; never prune against a partial export.
- If a summary conflicts with raw history, correct the summary and keep the raw record authoritative.
- If archive restore has not been tested, call the archive unverified and do not prune.
