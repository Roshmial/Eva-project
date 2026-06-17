# Chat-driven analytics dashboards in local-first CopilotKit flows

When the goal is to add analytics or dashboard generation into an existing chat-first web app, prefer an inline artifact pattern over a separate parallel UX unless the user explicitly wants a second surface.

## Durable pattern

1. Keep the current chat as the primary interaction surface.
2. Detect the analytics intent on the backend from the user message or explicit action.
3. Build analytics locally from the existing stack and local data sources before introducing any external services.
4. Return two things from the assistant route:
   - normal assistant text for the conversational summary;
   - a structured artifact in assistant message metadata, for example `meta.dashboard`.
5. Render that artifact inside the existing message bubble on the frontend.

This keeps CopilotKit acting as the orchestration/backend layer while the product UX stays chat-first and local-first.

## Verification order

Validate in this order:

1. Backend route/unit or smoke test for the analytics trigger.
2. Frontend build after JSX changes.
3. End-to-end runtime scenario in the chat.

Do not treat a backend pass as completion if the frontend build is broken.

## Editing pitfall discovered in live work

When source files were previously read with tools that include line-number prefixes like `1|...`, never feed that content back into a rewrite path. Rewriting code from line-numbered output corrupts the source and can truncate files. For source edits, prefer patch-based edits or raw file reads that preserve exact file bytes.

## User-specific preference relevant to this class of task

If the user says the naming/user-facing label problem was already solved, do not spend cycles re-discussing naming. Treat naming as settled and focus on functional integration, rendering, and verification.
