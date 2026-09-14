---
name: telegram-user-facing-copy
description: Craft short Telegram-native posts, captions, and story-style copy that sound human and fit the visual.
version: 1.0.0
author: Eva
---

# Telegram user-facing copy

Use this skill when the task is to write or refine:
- Telegram posts
- image captions
- story-style short copy
- short channel messages that should feel native to Telegram
- user-facing messages where formatting and tone matter as much as content

## Goal

Produce copy that feels like a real person wrote it, matches the image or context, and is ready to send without cleanup.

## Core workflow

1. Start from the visual or concrete context, not from an abstract theme.
2. Check whether the line refers to something actually visible or emotionally present in the image.
3. Write the final post as a finished artifact, not as commentary about options.
4. Prefer one best version by default. Offer alternatives only if the user asks.
5. Keep the text short enough for Telegram captions unless the user explicitly wants a longer post.

## Style rules

- Write in plain Russian.
- Do not add technical markup or delivery scaffolding in the user-facing text.
- Do not wrap the result in labels like "Подпись:", "Текст:", or "Вариант:" unless the user explicitly asks for that format.
- Do not quote the user's draft back as the final answer.
- Treat the user's rough wording as a direction, not text to echo.
- Prefer natural phrasing over conceptual or "smart-sounding" phrasing.
- Avoid inflated, philosophical, or generic motivational language unless the user explicitly wants that tone.
- If the image is quiet and minimal, keep the line grounded and simple.
- Do not mention objects, themes, or metaphors that are not actually supported by the image.

## Common pitfalls

### 1. Technical leakage into the message

Wrong pattern:
- including delivery markers, raw attachment notation, or explanatory labels inside the user-facing copy

Correct approach:
- give the finished post text cleanly; if media delivery syntax is required for the tool, keep it out of the prose itself

### 2. Echoing the user's draft too literally

Wrong pattern:
- polishing the user's rough line but keeping its awkward structure

Correct approach:
- preserve the intent, then rewrite from scratch in a more natural voice

### 3. Caption does not match the image

Wrong pattern:
- talking about "привычные вещи" or other unseen elements when the image shows only mood, space, light, or atmosphere

Correct approach:
- anchor the caption in what the image actually carries: pace, mood, entry into the week, pause, focus, calm, movement

### 4. Too much philosophy for a short story/post

Wrong pattern:
- abstract lines about worldview, transformation, destiny, or inner reinvention when the user wants a living, readable caption

Correct approach:
- choose short, breathable lines that sound like a person, not a manifesto

## Heuristics for choosing the best single line

Choose the option that is:
- easiest to say aloud without stumbling
- emotionally coherent with the image
- simpler than your cleverest draft
- specific in mood, even if not specific in objects
- calm enough to feel lived-in

## For this user's workflow

- By default, return one best option, not a list.
- If asked to make a post "под ключ", provide the final ready-to-send artifact immediately, without a follow-up block of possible improvements.
- Do not append optional continuation offers like "если хочешь, следующим сообщением могу..." when the user asked for the finished post already.
- When the user gives an image, mood, or rough phrase, treat it as direction, not as text to echo back literally.
- Prefer natural Russian phrasing over abstract or translated-sounding constructions; if a line feels slightly literary, philosophical, or "not quite Russian", simplify it.
- For story/post captions, first match the actual visual in the image. Do not build the line around objects, ideas, or motifs that are not present in the frame.
- For image posts in Telegram, the preferred format is two separate messages: first the image, then the caption as plain text.
- In the final user-facing post, do not add technical markup, raw MEDIA syntax, markdown image placeholders, labels like "Подпись:", or framing like "Это от меня, Евы" unless the user explicitly wants that wording inside the post.
- If the user asks for a live post delivery flow, the clean payload matters more than commentary: send or present the exact post content, not transport traces, logs, or service messages.


## Output patterns

### Image + short caption

[image]

Short caption line.

Name/signoff only if the user explicitly wants it.

### Story-style line

One or two short lines maximum.

## Reference notes

See `references/misha-telegram-post-lessons.md` for concrete lessons from a session where the user corrected technical formatting, over-literal reuse of his drafts, and captions that did not match the image.
