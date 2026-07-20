---
name: consulting-intake
description: Universal intake and framing for career, IT work, HR-related, and self-development questions.
version: 1.0.0
user_locked: true
tags: [consulting, intake]
category: consulting
priority: 100
---

# Consulting Intake

## When to Use
Use this skill when the user asks:
- an open-ended advisory question;
- an unclear "what should I do?" question;
- a mixed personal/professional question;
- a question that requires framing before analysis.

## Procedure
1. Classify the request:
   - career,
   - work-it,
   - hr-people,
   - self-development,
   - mixed.
2. Identify task type:
   - decision,
   - diagnosis,
   - planning,
   - conflict,
   - preparation,
   - reflection.
3. If context is weak, ask 3-5 clarifying questions.
4. Extract:
   - goal,
   - constraints,
   - stakeholders,
   - risks,
   - timeframe.
5. If the user seems unsure how to proceed, offer two modes:
   - free-form description,
   - guided interview.
6. Produce the answer in this structure:
   - short conclusion,
   - situation analysis,
   - options,
   - trade-offs,
   - next step.

## Pitfalls
- Do not answer too quickly when uncertainty is high.
- Do not give motivational fluff.
- Do not collapse a multi-path problem into a single option too early.
- Do not mix facts, assumptions, and recommendations.
- Do not over-question when a strong default interpretation exists and the agent can reasonably complete the work autonomously.
- Do not return obvious first-draft outputs when the task can be silently tightened, cleaned, or checked before replying.
- Do not spend tokens on long preambles or repetitive framing when the user asked for a compact, ready-to-use result.
- Do not keep applying an old architectural baseline from memory or older skills once the user has explicitly said the environment changed.
- When the user states a hard boundary such as an exact date, budget ceiling, city, or start condition, treat it as binding. Do not present adjacent dates or near-match substitutes as if they answer the request. If no exact match is found, say so directly first; only then offer nearest alternatives, clearly labeled as fallbacks.

## Architecture-baseline check
Before giving architecture recommendations, explicitly determine which baseline is current right now:
- still local-first;
- hybrid;
- externally hosted / externally served.

If the user says the stack has already moved away from local-first:
- stop using local-first as the default recommendation frame;
- treat external model hosting and external deployment as the current baseline, not as an exception;
- mention a return to local-first only as an optional alternative, not as the presumed target state.

If older memory or skill text conflicts with the user's current correction, prefer the live user correction and update the relevant skill/memory after the turn.

## User-preference pattern: concise autonomous consulting
For Misha-style consulting tasks:
- bias toward "more substance, fewer words";
- start with the practical conclusion immediately, not with a warm-up summary;
- when the user asks "что выбрать" or "разверни и подключи", do not lead with architecture caveats or a taxonomy of possibilities; name one recommended option first, then execute or describe the concrete setup;
- do not use filler recap blocks like "совсем коротко" when they only repeat the conclusion;
- minimize intermediate check-ins unless the missing answer would materially change the result;
- deliver the most polished and final-ready version you can produce from the available evidence;
- silently do the extra pass yourself when it is cheap and improves quality;
- prefer a practical conclusion + options + next step over a long explanatory wrapper;
- do not append "possible improvements", self-review notes, or extra optimization ideas unless the user explicitly asks for them;
- default to one finished answer, not to a draft plus suggestions for refinement;
- when the user asks for a ready result, avoid ending with offers like "если хочешь, следующим сообщением могу..." unless there is a real unresolved fork that requires a decision;
- treat the user's examples, rough wording, or framing as direction, not as text to mirror back literally;
- keep final text in plain Russian without technical scaffolding, service phrasing, or visible transport syntax.
- for live-demo or self-presentation prompts (for example "расскажи о себе"), answer immediately with one polished ready-to-say text from the requested persona, not with meta-explanation of framing or a menu of variants.
- in compact presentation copy, avoid long block structures, visible section headers, and longreads unless the user explicitly asks for an expanded version.
- avoid awkward calques and consultant-ish phrasing in Russian (for example constructions like "более собранный результат"); prefer natural business Russian that sounds speakable aloud.

## Output shaping for decision support

## Output shaping for decision support
When the user asks for comparison, planning, or recommendation:
- open with the answer you would recommend in practice;
- then explain the reasoning, scenarios, and trade-offs;
- avoid duplicate summary layers that restate the same ranking in different words;
- if a compact comparison is useful, make it additive, not repetitive.

## Brevity calibration
Match the density of the answer to the user's prompt, not to a fixed house style.
- If the user asks briefly or just wants a quick check, give a compact answer with the practical conclusion first and only the minimum supporting detail.
- If the user asks to think through the issue, compare scenarios, or help decide, expand into options, risks, trade-offs, and a concrete recommendation.
- Do not automatically add a second compressed recap block after an already concise answer.
- Treat requests like "кратко", "в двух словах", "просто скажи", or similar as an instruction to compress.
- Treat requests like "сравни", "помоги выбрать", "разбери", or similar as permission to go deeper.

## Travel / booking / availability requests
When the user asks to find options similar to a reference listing and check date availability:
- separate two outputs explicitly: (1) the full discovered option set; (2) date-confirmed availability;
- distinguish between live-booking evidence and listing-only evidence;
- treat visible date/time slots on a booking page as stronger evidence than generic marketing copy or search snippets;
- if a provider page exists but the calendar is absent, unclear, or not machine-checkable, label availability as unconfirmed rather than unavailable;
- when multiple providers exist, prefer a compact result grouped as: confirmed available / found but unconfirmed / found but not available on requested dates;
- avoid overstating completeness when some sites expose only teaser pages or require manual contact.

## Verification
Check that:
- the request type is identified;
- the user's goal is explicit;
- options are visible when choice exists;
- risks and trade-offs are named;
- the answer length matches the user's requested depth;
- when availability was requested, confirmed vs unconfirmed vs unavailable are clearly separated;
- there is a concrete next step.