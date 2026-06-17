# Generated-file output contract: prevent valid `.docx` files with invalid content

Use this when a chat/backend flow has a `generate new content + attach file` mode.

## Failure pattern

A live check can show all of the following as green while the result is still wrong:
- `message_kind=file_response`
- attachment exists and downloads over HTTP
- `Content-Type` is correct for `.docx`
- file signature is valid (`PK\x03\x04`)

But the document body is still invalid because the backend packaged model chatter instead of document content, for example:
- apology text
- tool transcript like `<tool_code>` or `write_file(...)`
- retry chatter (`I will now retry...`)
- parameter errors (`required 'path' parameter`)

## Diagnostic checks

For generated-file paths, verify all three layers:
1. Routing layer
   - confirm this is actually `generated_file_response`, not `message_export`
   - inspect metadata such as `source`, `generated_from_request`, `exported_message_id`
2. Content layer
   - inspect `preview_excerpt`
   - reject tool/service transcript markers
   - compare against the user request to ensure the text is a real document body
3. File layer
   - download the attachment
   - verify MIME type and magic bytes
   - if needed, inspect extracted text or preview text from storage metadata

## Durable fix pattern

If generated-file mode leaks tool transcript into the attachment, do not treat it as a mere prompt-quality issue.

Preferred fix:
- split generated-file mode from ordinary chat generation
- send a dedicated instruction that asks for only the final document body
- forbid tool chatter, apology text, logs, XML/JSON/Markdown fences, and file-creation narration
- add backend-side validation before packaging the attachment
- convert invalid generated text into a short file-specific error instead of a successful artifact

## Good acceptance criteria

A fix is only complete when all of these are true in live runtime:
- generated-file request returns `source=generated_file_response`
- attachment downloads successfully as a real `.docx`
- `preview_excerpt` begins with substantive document content
- `preview_excerpt` does not contain apology/tool transcript markers
- regression test exists for transcript rejection
