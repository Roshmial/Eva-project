# Message viewer vs chat rendering split

Use this when the user reports that a message still looks wrong after a chat-render fix, especially when screenshots show a standalone document-style page rather than an in-thread bubble.

## Fast classification

Symptoms that point to viewer/export instead of chat bubble:
- white standalone page with product header / timestamp / document layout;
- markdown appears as raw `|---|`, `**bold**`, `[link](url)` even though chat payload was already cleaned;
- recurring/job-delivery digest still shows planning/instruction blob in preview even though the main thread bubble looks corrected.

## Common root cause

The app has two user-facing paths:
1. chat bubble / thread renderer;
2. message export or viewer renderer.

A frequent split is:
- chat path already uses normalized assistant text (`display_text`, recurring summary, sanitized digest body);
- export/viewer path still reads raw persisted `content` and escapes it as plain text.

## Verification pattern

Check these separately:
- serializer output for the live message;
- frontend bubble render branch;
- export/viewer builder path (`build_message_export_html`, `build_message_export_markdown`, similar helpers);
- whether JSON export exposes only raw `content` or also a normalized body field.

## Durable fix pattern

- Introduce a canonical helper for export/viewer body, e.g. `build_message_export_body(message_row)`.
- For assistant messages, prefer normalized display text over raw content.
- For recurring/job-delivery messages, prefer cleaned recurring summary body over raw content.
- In export payloads, expose a normalized field such as `display_content` so downstream consumers do not fall back to raw `content`.
- Add regression tests for both:
  - assistant markdown export renders HTML table/strong and strips reasoning preface;
  - recurring digest export starts from cleaned digest body and excludes planning/instruction text.

## Environment note

If HTML export still degrades to plain paragraphs after the code fix, verify that the runtime environment actually has the markdown-rendering dependency installed. Capture this as a setup/deploy step, not as a permanent claim that the renderer is broken.
