---
name: artifact-delivery-contract-hardening
description: Harden chat/file delivery flows so agents cannot claim a file, link, or export exists unless the runtime actually produced a deliverable.
---

# Artifact delivery contract hardening

## When to use
Use this skill when a chat product, agent surface, or automation flow can:
- promise a file, document, download link, export, attachment, or report,
- convert a previous answer into a downloadable artifact,
- mix free-form LLM generation with deterministic export routes,
- show user frustration like "you said the file is ready but nothing is attached".

Typical examples:
- chat asks like "пришли файл", "давай документ", "export this",
- assistant messages that say "document is ready" without an attachment,
- backend flows where export is sometimes deterministic and sometimes left to the model,
- systems with `message_kind=file_response`, attachments arrays, download URLs, or similar metadata.

## Core principle
Artifact claims must be backed by artifact evidence in the same response.

Allowed claim:
- "Собрала ответ в файл ..." only when the response actually contains an attachment, a local path to a generated file, or a download URL.

Disallowed claim:
- "Документ готов", "ссылка приложена", "финальный файл собран" when attachment metadata is empty or absent.

If no artifact was created, the system must either:
1. trigger the deterministic export path, or
2. answer honestly that the artifact is not yet created.

## Preferred architecture
Prefer local deterministic export routing over prompt-only behaviour.

Order of preference:
1. Detect explicit or generic file intent in backend/application logic.
2. Route to deterministic export of the latest eligible assistant content.
3. Attach artifact metadata and real download handle.
4. Only then allow wording that the file is ready.

Do not rely on the model alone to decide whether a file exists.

## Implementation checklist
1. Inspect real broken examples from storage/runtime, not just the UI.
   - Compare message text with message metadata.
   - Check fields like `message_kind`, `attachments`, `download_url`, `attachment_count`, `exported_message_id`.
2. Separate two failure classes:
   - export mechanism broken,
   - routing/prompt contract broken.
3. Strengthen the system prompt or backend instruction layer.
   - Add an explicit rule that file/link/attachment claims require a real deliverable in the same answer.
4. Expand generic file-intent detection.
   - Include natural user phrases, not only exact format names like `docx` or `pdf`.
   - Examples: "давай файл", "пришли документ", "отправь файл", "направь файл".
5. Keep explicit format handling intact.
   - `pdf`, `docx`, `xlsx`, etc. should still work exactly.
6. Add regression tests for both:
   - explicit export request,
   - generic export request.
7. Live-verify on the real runtime.
   - Create a temporary user/thread.
   - Produce a normal assistant answer.
   - Send a generic request like "Давай файл".
   - Confirm the final assistant message has real attachment metadata and a usable download handle.
8. Clean up temporary users, threads, and generated test artifacts if the product expects a clean surface.

## Pitfalls
- Mistaking a routing failure for a file-generation failure.
  - If old `file_response` messages with attachments already exist, the generator may be fine; the intent router is the likely bug.
- Fixing only the prompt.
  - Prompt tightening helps, but deterministic export routing is the real control point.
- Handling only explicit format names.
  - Users often say "давай файл" rather than "export to docx".
- Declaring success from text alone.
  - Verify attachment metadata, not just the assistant wording.
- Leaving a loophole where the model can still emit "file ready" with no attachment.
  - If risk is high, add a backend guard that downgrades or blocks such replies.

## Verification standard
Do not close the task until you have all of the following:
- code or config change applied,
- regression tests for generic + explicit file export paths,
- live runtime proof that a generic file request yields:
  - artifact message kind,
  - non-empty attachments,
  - real download URL or path,
  - correct exported format.

## Hermes Web / local-first note
In local-first chat systems, prefer hardening the existing backend message/export flow before adding new services or separate export daemons. Reuse the current message metadata contract and extend the current routing logic rather than introducing a second artifact pipeline.

## Support files
- `references/hermes-web-false-file-claims.md` — concrete evidence and acceptance pattern from a live Hermes Web case where the model claimed a file without attachments.
