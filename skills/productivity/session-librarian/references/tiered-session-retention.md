# Tiered session retention

Use this when session-history cleanup is motivated by database growth rather than by a user wanting particular conversations erased.

## Retention model

Choose age thresholds from observed access patterns and available disk; do not hard-code universal numbers.

- Hot: raw sessions remain online and fully searchable.
- Warm: raw messages may remain online with rebuildable or bulky tool payloads compacted; preserve decisions and artifacts exactly.
- Cold: reusable conclusions remain in the canonical decision log while raw sessions live in a compressed, verified archive.
- Protected: pinned, active, unresolved, compliance-relevant, or explicitly important sessions remain raw regardless of age.

## Decision-coverage contract

Do not create a permanent summary per source session by default; that produces a second competing knowledge base. Group continuation sessions by normalized topic and use compact extracts only during the audit. Promote reusable knowledge into one canonical topic record containing:

- current decision and scope;
- reasons and material trade-offs;
- rejected alternatives worth not reopening;
- facts, constraints, and durable user preferences;
- verified actions/results, clearly separated from hypotheses or unmeasured effects;
- artifacts and durable handles;
- unresolved questions and revisit conditions;
- exact session/message evidence or another stable source pointer.

Classify each affected topic/session as `covered`, `missing`, `superseded/conflict`, or `no reusable knowledge`. Do not copy full logs or long tool output. Preserve exact identifiers and result status.

## Efficient audit recipe

1. Select an exact cutoff and enumerate affected sessions.
2. Normalize continuation titles and group by topic.
3. Deduplicate repeated handoff context and large tool payloads while retaining IDs and raw-source access.
4. Balance audit batches by bytes/tokens; begin with 1–3 parallel workers rather than a wide fan-out.
5. Have workers write candidate reports only. A single parent/editor validates evidence and changes the canonical log.
6. Validate every cited `message_id` and its actual `session_id` against the read-only source database; child summaries are hypotheses, not proof.
7. Run an independent deterministic sample across direct sessions and cron/tool noise to falsify the coverage claim.

## Safety gates before pruning raw online data

1. Create a transactionally consistent raw archive or bounded exports.
2. Verify archive integrity with the format's checker and a checksum.
3. Complete the topic-level coverage audit without modifying source sessions.
4. Consolidate missing conclusions into canonical decision-log records; resolve conflicts/supersession.
5. Verify known-topic retrieval and exact evidence pointers.
6. Inspect/restore a raw sample and independently verify a deterministic `noise` sample.
7. Run the prune command in dry-run mode and review protected-session exclusions.
8. Obtain explicit approval for destructive pruning.
9. Prune in bounded batches, then rebuild indexes or VACUUM only when appropriate.
10. Re-measure size, integrity, search quality, and restoreability before deleting temporary snapshots.

## Failure handling

- If coverage is incomplete or contradictory, retain the raw online session.
- If a whole-database export exhausts memory, split by session/time range or archive a consistent database snapshot; never prune against a partial export.
- If a candidate report conflicts with raw history, correct the canonical log from raw evidence and record the conflict disposition.
- If archive restore or evidence traceability has not been tested, call the archive/coverage unverified and do not prune.
