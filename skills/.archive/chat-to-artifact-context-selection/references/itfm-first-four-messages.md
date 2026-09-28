# ITFM chat-to-slides case

## What happened
The generated PPTX/document route kept inheriting noisy late-thread content instead of the real source discussion.

Symptoms:
- slide content reflected placeholder replies like "Текст по слайдам подготовлен"
- follow-ups like "По слайдам" influenced the content source too much
- deck structure drifted away from the first substantive user/assistant exchange

## Durable lesson
For discussion-to-artifact requests, the backend should often select a small early substantive window instead of replaying the whole thread.

## Concrete pattern used
Focused window:
- first 4 substantive user/assistant messages

Excluded from primary source:
- format-only follow-ups
- placeholder assistant acknowledgements
- processing-status / file-response chatter

## Why this matters
Late-stage export chatter is usually about packaging, not substance. If it becomes the source context, the generated document or deck becomes a summary of the export process instead of a reconstruction of the original discussion.

## Verification shape
Useful regression assertions:
- prompt contains the first substantive problem framing
- prompt contains the first assistant synthesis
- prompt excludes "Текст по слайдам подготовлен"
- prompt excludes export-format-only follow-up as source material
