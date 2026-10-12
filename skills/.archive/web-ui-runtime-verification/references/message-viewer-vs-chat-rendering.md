# Message viewer vs chat bubble: runtime triage

Use this when the user reports that a message still looks wrong in production, but screenshots do not match the in-chat bubble layout.

## Strong signal that you are looking at the wrong surface

If the screenshot shows a white document-style page with its own heading/title, large page margins, `HERMES` branding, or a bottom timestamp, do **not** assume the defect is in the chat bubble renderer.

Treat it as a likely **message export / preview / viewer** path and split the investigation:

1. Chat bubble rendering in the main thread UI.
2. Message viewer / export rendering for the same message id.

Do not close the incident after fixing only one of those paths.

## Required debugging sequence

1. Identify the exact affected message ids.
   - Verify whether the message is a normal `chat_response` or a `job_delivery` / recurring result.
2. Inspect live serialized payload for the message.
   - Check `display_text`, `meta.display_text`, `meta.recurring_summary`, `assistant_result_kind`, `output_mode`, `message_kind`.
3. Inspect the export/viewer functions on the live backend.
   - Check whether HTML/Markdown export is built from raw `message_row['content']` or from the cleaned display body.
4. Compare both surfaces explicitly.
   - A chat fix is not enough if the viewer still renders stale raw content.

## Durable pitfall

A common false conclusion is:
- "frontend bundle is stale"
- or "markdown parser in chat is broken"

when the real issue is that the **viewer/export path bypasses the cleaned serializer path** and uses raw saved content.

Typical symptoms:
- reasoning-preface disappears in chat but remains in the viewer;
- digest planning/instruction text disappears in chat but remains in the viewer;
- markdown tables are rendered correctly in chat but appear as raw `| ... |` text in the viewer.

## Repair pattern

For message preview/export paths:

1. Introduce one shared helper for the user-facing message body.
   - For assistant messages: prefer cleaned `display_text` logic.
   - For recurring/job-delivery messages: prefer cleaned `recurring_summary.summary/status_detail`.
   - For user messages with attachment wrappers: prefer `meta.user_text` when present.
2. Make both Markdown and HTML export consume that shared cleaned body.
3. If HTML preview should preserve markdown structure, render markdown to HTML instead of escaping plain text line-by-line.

## Verification checklist

For a markdown-heavy message:
- HTML contains `<table>` when the source contains a markdown table.
- HTML contains `<strong>` for bold segments.
- HTML no longer contains raw `|---` separators.
- HTML no longer contains removed reasoning-preface text.

For a recurring digest message:
- export body starts from the final digest title, not from planning text.
- HTML contains working `<a href=...>` links.
- HTML does not contain planning fragments like prompt-analysis prose.

## Dependency note

If live HTML export still falls back to plain paragraphs after the code fix, verify the runtime Python environment actually has the markdown renderer dependency installed. Capture the fix as a setup/troubleshooting step, not as a permanent claim that the viewer "does not support markdown".
