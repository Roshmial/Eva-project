# BI dashboard follow-up routing and live acceptance notes

Use this note when a Hermes Web user says a dashboard is missing, empty, or "not on the topic" even though backend/task status looks green.

## What this incident showed

1. Separate three failure classes before changing code:
   - render/visibility defect: dashboard payload exists and reaches the client, but the UI fails to show it;
   - semantic payload defect: dashboard renders, but sections are placeholder/fallback content about the route or agent work instead of the subject;
   - follow-up routing defect: a short user follow-up such as "build a dashboard on this topic" is misrouted into a fresh web-collection path instead of transforming the previous substantive answer.

2. Resolve the exact acceptance target, not a loose "latest chat" idea.
   - If the user says "the latest new thread", resolve it by `user_id + title + updated_at`, then inspect the actual message sequence.
   - Do not switch to another user/account midway through diagnosis.
   - Distinguish "last thread overall" from "last thread named 'Новый чат'" or similar title-based buckets.

3. Verify the live HTTP payload as the actual user.
   - Create or reuse a session for the named live user.
   - Fetch `/api/threads/<id>` with that user's auth.
   - Confirm whether the assistant message includes `meta.dashboard`, `message_kind`, and the expected sections.
   - This proves whether the issue is before or after the transport boundary.

4. A dashboard can be transport-correct and still be semantically wrong.
   - In the BI incident, the payload was a real `dashboard_result`, but its sections were mostly fallback placeholders:
     - timeline fallback saying more historical sources were needed;
     - matrix fallback repeating the user's request;
     - "what we established" containing route/agent text rather than BI history.
   - Treat this as a backend semantic failure, not a UI success.

5. Short follow-ups like "по этой теме" must prefer previous substantive context.
   - If the prior assistant message is a substantive text analysis and the user then asks for a dashboard, the preferred behavior is `text -> dashboard` based on that answer.
   - If the runtime instead starts a fresh `web_collection` run and raises something like `web_collection_documents_irrelevant`, classify that as a follow-up routing bug.

## Durable acceptance pattern

When debugging a live dashboard complaint:
1. Resolve the exact thread under the exact user.
2. Inspect the last 4-6 messages in chronological order.
3. Classify each assistant message as one of:
   - placeholder/status;
   - semantic answer;
   - dashboard result;
   - processing error.
4. Fetch the thread via live HTTP as that user.
5. Compare:
   - DB meta payload;
   - HTTP payload;
   - frontend renderer expectations.
6. Only after that decide whether the fix belongs in UI rendering, dashboard normalization, or follow-up routing.

## Pitfall to encode in future fixes

Do not treat a green `dashboard_result` as proof that the user got a useful dashboard. Check whether the dashboard sections are subject-matter content or merely route/fallback scaffolding.