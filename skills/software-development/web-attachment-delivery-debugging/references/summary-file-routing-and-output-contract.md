# Summary/file routing and output-contract checks

Use this when a user says some variant of:
- "собери файл"
- "собери один файл, где будет суммаризация"
- "файл создался, но мне его не отдали"
- "вместо файла пришёл путь /home/hermes/..."
- "summary тянет хвост Рекомендация / Следующий шаг"

## Distinguish the two file routes

1. Export previous answer
- Typical user text: `Собери файл`, `Пришли файл`, `Выдай файл`
- Expected meta:
  - `message_kind = file_response`
  - `source = message_export`
  - `exported_message_id` points to an existing substantive assistant answer
- Failure class: wrong export target, often apology/technical text instead of the intended answer

2. Generate-and-attach new file
- Typical user text: `Собери один файл, где будет суммаризация`, `Сделай файл с суммаризацией`, `В одном файле собери итог`
- Expected meta:
  - `message_kind = file_response`
  - `source = generated_file_response`
  - `generated_from_request = true`
- Failure class: request falls back to plain chat text about a Markdown/local file instead of attachment delivery

## Live checks

For a suspected broken message, inspect:
- `message_kind`
- `source`
- `generated_from_request`
- `exported_message_id`
- `attachments[].download_url`
- `attachments[].preview_excerpt`

Interpretation:
- Attachment exists + `download_url` exists -> delivery chain likely intact; investigate UI/auth/download endpoint next
- No `file_response`, but assistant text narrates a local file path -> routing/output-contract bug, not attachment-download bug

## Output-contract contamination to watch for

### Local path leakage
User-facing assistant text must not expose raw runtime paths like:
- `/home/hermes/...`
- `/tmp/...`

If no real attachment was delivered, replace/scrub such paths before publishing the reply.

### Summary tail leakage
For summary-intent requests, final reply should stay a summary.
Red-flag tails:
- `Рекомендация по реализации:`
- `Рекомендация по следующему шагу:`
- `Следующий шаг:`
- `Если хотите, я могу помочь...`

These should be removed in summary-specific postprocessing.

### Generated-file instruction leakage
In `generated_file_response`, file content or `preview_excerpt` may accidentally include internal instruction text like:
- `Подготовь только финальное содержимое документа...`
- backend-side tool/output-contract prompts

Treat this as generated-content contamination. The file may be technically downloadable and still be semantically wrong.

## Practical lesson from this incident class

When the user says "file was created but not delivered", do not assume the download endpoint is broken.
First separate:
- attachment delivery failure
- export-target selection failure
- generate-file routing failure
- generated-content contamination
