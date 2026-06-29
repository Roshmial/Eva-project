---
name: chat-to-artifact-context-selection
description: Choose and compress the right chat context before generating files, documents, decks, or structured exports from prior discussion.
---

# Chat-to-artifact context selection

## When to use
Use this skill when a user asks to turn an existing chat or discussion into an artifact:
- presentation / PPTX
- document / DOCX / PDF
- slide outline
- report, brief, memo, summary deck
- any generate-and-attach-file flow where the source material is a prior conversation rather than a single clean prompt

Typical user phrases:
- "по итогам обсуждения"
- "из чата"
- "пересобери по слайдам"
- "сделай документ из переписки"
- "возьми только начало обсуждения"
- "там важны только первые сообщения"

## Core principle
For chat-to-artifact tasks, the best source is often **not the whole thread**.

Late thread content frequently contains:
- format-only follow-ups
- confirmations like "по слайдам" / "в документ"
- placeholder assistant text like "текст подготовлен"
- retries, repair chatter, export explanations, routing noise

If that noise is fed back into generation, the artifact inherits secondary chatter instead of the original substance.

## Default approach
1. Identify whether the request is asking to transform a discussion, not answer a fresh question.
2. Find the **substantive discussion window**.
3. Prefer the earliest coherent user/assistant exchange that contains the actual problem framing and core answer.
4. Exclude format-only follow-ups, placeholder acknowledgements, processing-status messages, and previous file-delivery chatter.
5. Pass the focused window to the model as the primary source block.
6. Keep the final user request only as formatting instruction, not as the main content source.

## Good selection heuristics
Prefer messages that contain:
- the original analytical question
- the first real assistant synthesis
- clarifying user follow-up that deepens substance
- second assistant answer that completes the core model

Often the right window is only 2-6 messages.

## Messages to exclude by default
Exclude these from the primary source block unless the task explicitly needs them:
- "по слайдам"
- "в формате документа"
- "сделай в pptx/pdf/docx"
- "давай файл"
- placeholder assistant replies like "текст подготовлен"
- processing / pending / retry / failure boilerplate
- previous export wrappers and file-response text
- model limitation or tool chatter

## User-specific pitfall captured from this session
When Misha asks to rebuild slide content from a chat, do **not** re-summarize the whole noisy thread and do **not** treat the latest formatting follow-up as the content source.

In this class of task, if he points to the first few messages as the meaningful material, treat that as a product requirement, not as optional guidance.

## Backend implementation guidance
In a local-first backend route:
- add a focused-context selector before the LLM call
- keep generic full-history behavior for ordinary chat
- switch to focused context only for discussion-to-artifact requests
- store the focused window as an explicit prompt block, e.g. "ключевой фрагмент исходного обсуждения"
- keep deterministic export and attachment logic unchanged

## Testing requirements
Add regression tests that verify:
1. the focused prompt includes the intended early substantive turns
2. the focused prompt excludes late placeholder / format-only turns
3. normal generated-file behavior still works for non-focused cases
4. export rendering tests still pass after the prompt-selection change

## Pitfalls
- Using the last assistant message as the source answer when it is only a placeholder
- Treating "по слайдам" as substantive content
- Feeding the entire thread back to the model after the conversation accumulated export/debug chatter
- Fixing this only in prompt wording instead of adding a backend source-selection step
- Overfitting to one thread title instead of matching the class of discussion-to-artifact requests

## Verification standard
Do not close the task until you have:
- backend source-selection logic applied
- regression coverage for focused-window behavior
- confirmation that export generation still passes existing artifact tests

## Support files
- `references/itfm-first-four-messages.md` — concrete session note showing when the first 4 substantive chat messages should override later export chatter.

## Relationship to nearby skills
This skill complements:
- `artifact-delivery-contract-hardening` — ensures a claimed file actually exists
- PPTX/document export skills — shape the artifact itself

This skill is specifically about choosing the right **source conversation slice** before artifact generation begins.
