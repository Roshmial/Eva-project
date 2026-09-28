# dashboard_result chat render drift

Use this reference when Hermes Web users say they asked for a dashboard but only got plain text in chat.

## Symptom shape

- User asks for a dashboard in chat.
- Backend task completes successfully.
- Stored assistant message has `message_kind = dashboard_result`.
- Message metadata contains a structured `dashboard` object with cards/sections/sources.
- Chat UI still shows only the textual `content` field, so the user concludes "there is no dashboard".

## Durable lesson

This is a frontend-backend contract drift, not necessarily a model or routing failure.

The decisive check is to split the system into three layers:

1. Stored message payload
   - Inspect the live DB or API response for the exact message.
   - Confirm `meta.message_kind`, `meta.dashboard`, attachments, and any artifact paths.

2. Chat component render branch
   - Read the actual message renderer (`MessageBubble` or equivalent).
   - Check whether it branches on `message_kind === dashboard_result` or renders `meta.dashboard` directly.
   - If it only renders `content`, attachments, and artifact links, the visual dashboard is being dropped at render time.

3. Styling versus reachability
   - Search CSS for dashboard classes such as summary grids, section lists, bar/pie layouts.
   - Existing CSS is not proof of support.
   - Verify there is a live React branch that can reach those classes from message metadata.

## Concrete pattern observed

In Hermes Web:

- Backend stored `dashboard_result` with `meta.dashboard.kind = external_research_dashboard` and structured sections.
- Frontend chat `MessageBubble` rendered only:
  - text content
  - attachments
  - request policy strip
  - optional dashboard artifact path link
- Frontend did **not** render `message.meta.dashboard`.
- Result: user saw plain text even though the dashboard had already been built.

## Recommended fix shape

- Add an explicit renderer for structured dashboard messages in the chat surface.
- Branch on either:
  - `message.meta.message_kind === 'dashboard_result'`, or
  - presence of `message.meta.dashboard`.
- Reuse the existing dashboard grammar shape (`summary_cards`, `sections`, section kinds like `bar_list`, `pie_list`, `text_list`) instead of inventing a second parallel contract.
- Verify against one real production message, not only mock data.

## Verification checklist

- Real stored message contains `meta.dashboard`.
- Frontend component reads that key.
- Built bundle includes the render branch.
- Live runtime shows visual dashboard blocks instead of plain text only.
- User-facing repro thread now displays the same message as a dashboard without changing the backend payload.
