---
name: voice-transcription-response-handling
description: Handle messaging-platform voice transcripts so the agent responds to content first, not to the meta fact that audio was transcribed.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Voice transcription response handling

Use this skill when working on Hermes gateway behavior for Telegram or other messaging platforms where user voice/audio is auto-transcribed and injected into the model context.

## Problem this skill prevents

A common UX failure is that the gateway prepends voice transcripts as a meta note like "the user sent a voice message" and the model answers the meta question (for example, explaining that it can transcribe audio) instead of responding to the actual content of the spoken message.

This shows up especially in two cases:
1. The user is testing STT quality.
2. The user speaks an actionable request like creating an event or reminder.

## Core rule

When injecting a successful transcript into the user message, frame it so the model treats the transcript as the user's actual message.

Good pattern:
- explicitly say the transcript below is the user's actual message;
- instruct the model to respond to the content first;
- if the user appears to be testing transcription quality, instruct the model to show the recognized text first.

Example injection shape:

`[The user sent a voice message. Treat the transcript below as the user's actual message and respond to its content first. If the user is checking transcription quality, first show the recognized text. Transcript: "..."]`

## Implementation guidance

1. Keep STT success handling separate from STT failure handling.
2. On STT success, prefer one compact instruction block plus the transcript.
3. Avoid playful or indirect phrasing like "Here's what they said" when the transcript must drive downstream task execution.
4. Preserve failure branches for:
   - no STT provider configured;
   - transcription failure;
   - unexpected runtime exception.
5. After changing gateway transcript injection, restart the Hermes gateway so the new behavior is live.

## Verification checklist

After the patch, test at least these scenarios:

1. Transcription-check message
- Example voice content: "Проверь, как ты меня распознала."
- Expected behavior: assistant first prints the recognized text, then comments on transcription quality.

2. Actionable request
- Example voice content: "Поставь встречу в календаре завтра в шесть вечера."
- Expected behavior: assistant first interprets the request itself, then asks only for genuinely missing fields or proceeds via the calendar workflow.

3. No-auth downstream tool path
- If the spoken request requires an integration that is not authenticated, the assistant should still acknowledge the recognized text first and then explain the missing auth/config step.

## Pitfalls

- Do not optimize only for STT correctness; optimize for post-transcription response behavior.
- Do not store the lesson as "voice is broken" if STT succeeded and the failure was actually prompt framing.
- Do not rely on a generic conversation-level instruction alone when the real issue is the injected transcript wrapper.

## When to reuse

Reuse this skill for any future work on:
- Telegram voice UX;
- gateway transcript enrichment;
- STT-to-task handoff bugs;
- cases where the agent responds to audio metadata instead of the spoken request.
