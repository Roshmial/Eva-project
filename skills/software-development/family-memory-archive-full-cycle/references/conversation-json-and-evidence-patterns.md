# Conversation JSON and evidence patterns

Use this pattern when a family memory archive must include переписки alongside media.

## Practical JSON normalization
Accept permissive source shapes:
- `conversation.title` or `chat.name`
- `messages` or `items`
- sender from `sender_name` / `from` / `author` / `sender`
- text from `text_content` / `text` / `message` / `body`
- timestamp from `sent_at` / `date` / `timestamp` / `created_at`

## Episode assembly rule
Episodes should be able to carry:
- media attachments;
- people attachments;
- message attachments.

This keeps Q&A grounded in both files and remembered dialogue.

## Acceptance rule
A real full-cycle acceptance pass should verify:
1. conversation JSON imports successfully;
2. messages are searchable;
3. person-message candidates can be generated;
4. accepted messages can be attached to the chosen episode;
5. episode Q&A cites message evidence in the final answer.

## Stability rule
If richer semantic matching is not ready, ship a simpler deterministic heuristic first, but keep provenance explicit and visible in the answer text.
