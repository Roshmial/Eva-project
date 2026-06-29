# Generated-file follow-up continuity for structure/format refinements

Use this when a chat already contains a substantive request to create a file or presentation, and the user then sends a short follow-up such as:
- "по слайдам"
- "по страницам"
- "по таблицам"
- "в формате документа"
- "в docx"
- "в pptx"

## Durable rule

Treat these short follow-ups as refinements of an existing artifact-generation task, not as new standalone requests.

The routing layer should restore the last substantive user request and combine it with the short follow-up before choosing between:
- generate-and-attach-file
- export previous answer
- generic chat reply

## Why this matters

Without continuity restore, the system tends to:
- answer in chat with plain text instead of producing a file result;
- package a meta-reply like "document prepared and saved" into `docx`/`pptx` instead of the real discussion content;
- over-index on the last short message and lose the original task subject;
- drift into English or generic boilerplate at the end of the file-generation path.

## Recommended implementation pattern

1. Add a dedicated helper for generated-file follow-ups, parallel to dashboard/collection follow-up restore.
2. Detect short structure/format refinements with a dedicated allowlist.
3. Restore the source request from the latest substantive user message that is not itself a short follow-up.
4. Pass the restored request into downstream route selection before export/generate decisions are made.
5. Strengthen the generated-file prompt so it includes:
   - the original substantive user request;
   - the substantive material already developed in the thread;
   - an explicit language requirement when the task should stay in Russian;
   - an explicit ban on meta-claims like "file prepared/saved" when the runtime needs the actual document body for packaging.

## Prompt contract hardening

For generated-file content prompts, explicitly instruct the model to:
- produce only the final document content;
- stay on the user's language unless another language was explicitly requested;
- use the thread's substantive material rather than only the final short follow-up;
- preserve requested structure when the user says "по слайдам" / "по страницам" / "по таблицам";
- avoid tool chatter, XML/JSON wrappers, and promises about creating or saving files later.

## Regression coverage to keep

Keep targeted tests for:
- clarification follow-up that must preserve `pptx` intent;
- structure-follow-up restore from "по слайдам" back to the original artifact request;
- generated-file prompt composition including source request + substantive source answer + explicit Russian requirement;
- `process_chat_task` route selection using the restored follow-up request;
- actual file-reply packaging where the environment supports the target format.

## Specific pitfall

Do not classify any full request containing `pptx`/`docx` as a short format-only follow-up just because the format keyword is present. A real source request such as "Сделай презентацию в pptx по итогам обсуждения ..." must remain eligible as the substantive source request for later continuity restore.
