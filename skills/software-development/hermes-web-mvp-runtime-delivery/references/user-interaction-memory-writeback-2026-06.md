# User interaction memory writeback — 2026-06

When Hermes Web appears to "use memory" but does not accumulate new durable facts from chat, treat this as an architecture gap between profile personalization and interaction-derived memory.

## Problem pattern
- `pinned_json` / `assistant_profile_json` already exist and are read into prompt personalization.
- Users expect the agent to remember stable preferences or working rules from ordinary dialogue.
- No auto-write path exists after assistant responses, so the system only reuses manually edited profile data.

## Preferred fix in this stack
Use a separate user-scoped store for interaction memory instead of mixing auto-derived memory into manual profile fields.

Recommended fields on `users`:
- `interaction_memory_json` — normalized list of durable memory items derived from dialogue.
- `memory_last_processed_message_id` — cursor for periodic/background processing.

## Delivery pattern
1. Keep manual profile memory (`pinned_json`, `assistant_profile_json`) separate from auto-derived memory.
2. Add a periodic backend worker inside the existing Hermes Web backend process; do not introduce a separate external service unless there is a proven need.
3. The worker should:
   - scan new user/assistant messages after the stored cursor;
   - extract only durable, user-scoped facts/preferences/work-rules;
   - update `interaction_memory_json`;
   - advance `memory_last_processed_message_id`.
4. Extend personalization assembly so prompt injection uses both:
   - manual profile memory;
   - interaction-derived memory.
5. Prefer periodic/asynchronous writeback over synchronous writeback in the chat response path to avoid slowing replies and to keep retries/idempotence simple.

## Verification checklist
- Confirm DB writeback: `interaction_memory_json` becomes non-empty and the cursor advances.
- Confirm prompt path: personalization builder includes interaction memory in the assembled block.
- Add at least two tests:
  - memory writeback from a short user/assistant exchange;
  - personalization includes interaction memory after writeback.
- For live verification, use a temporary user/thread, run the periodic pass, verify DB state, then clean up test data.

## Pitfalls
- Do not write auto-derived memory into `pinned_json`; that field is for curated/manual notes.
- Do not block the normal chat reply on memory extraction unless there is a strong reason.
- Do not treat every message as memory; store only durable guidance and stable preferences.
- Do not rely on UI-only verification; confirm both DB writeback and prompt inclusion.
