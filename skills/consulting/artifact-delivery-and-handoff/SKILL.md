---
name: artifact-delivery-and-handoff
description: Deliver documents, runbooks, and other generated artifacts in the exact form the user asked for, with attachment-first behavior and minimal chat duplication.
---

# Purpose

Use this skill when the user asks for a file, handoff package, runbook, documentation artifact, or any deliverable that should exist as a concrete file rather than just chat text.

# Trigger

Apply when the user says or implies any of the following:
- "сделай файл"
- "скинь файлом"
- "сюда файл"
- "отправь в Telegram"
- "нужна инструкция / документация / runbook / handoff"
- "не текст, а файл"

# Core rule

When the requested deliverable is a file, the job is not complete until the file exists and is delivered in file form.

# Workflow

1. Produce the requested artifact as a real file in the requested format.
2. Verify that the file exists at the final path.
3. Deliver the file directly in the response using the platform delivery mechanism.
4. Keep the chat response short.
5. Summarize the contents only if the user asks for a summary.

# Response pattern

Default pattern:
- one short sentence if needed
- then the actual file delivery handle

For platforms that support local file delivery in chat, send the file directly instead of pasting the full body.

# Pitfalls

- Do not paste the full document into chat if the user asked for a file.
- Do not switch to another format just because it is convenient.
- Do not offer a file after already dumping the full contents, unless the user explicitly asked for both.
- Do not treat "сюда файл скинь" as a request for a preview; it is a delivery request.

# User-specific preference captured from practice

This user expects documentation and handoff artifacts to be delivered as files immediately when requested. If she asks for a file in chat or Telegram, attachment-first delivery is the correct default.

# Examples

Instead of:
- pasting the whole handoff into chat
- then asking whether to send a file

Do:
- create the `.txt` or `.md`
- reply with the file attachment/path immediately

# Related skills

- This overlaps with brief response / delivery-style skills. If both apply, prefer artifact-first delivery and short chat text.
