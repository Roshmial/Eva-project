# Full-cycle acceptance pattern for a named remote host

Use this when the user asks for a live end-to-end proof on a real server.

## Minimal sequence

1. Prepare one deterministic fixture entity on the target host.
2. Run the whole chain only through shipped product endpoints or UI actions.
3. Persist a machine-readable report with:
- imported item count;
- created person/entity id;
- created episode/object id;
- processing/job statuses;
- final user-facing answer/result.
4. Mention the report path in the final reply.

## Why this matters

Passing tests and a green service status are not enough for turnkey delivery. A future session should leave behind one concrete successful round-trip on the real target.
