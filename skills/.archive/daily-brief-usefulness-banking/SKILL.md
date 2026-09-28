---
name: daily-brief-usefulness-banking
description: Use when daily briefs get abstract or repetitive. Keep ac...
version: 1.0.0
author: Hermes Agent
license: MIT
created_by: agent
---

# Purpose

Use this skill when creating, repairing, or reviewing short daily brief messages, especially Telegram-style morning briefs where quality depends more on the usefulness bank and anti-repeat logic than on one-shot prompting.

This skill exists for cases where the user wants:
- a short fixed format;
- concrete useful actions;
- high variation without fake novelty;
- no management-speak, motivational filler, or pseudo-useful abstractions.

# When to use

Use this skill when:
- a recurring daily brief keeps repeating the same ideas;
- the user says the brief is too abstract, too smart-sounding, too verbose, or too empty;
- the brief should stay short, but usefulness must remain high;
- there is a curated bank of ideas or one should be introduced.

# Core rule

A good daily-brief idea is an action, not a reflection.

Preferred shape:
- "сделай ..."
- "посмотри ..."
- "почитай ..."
- "разбери ..."
- "проверь ..."
- "ответь ..."
- "закрой ..."

Bad shape:
- reconsider priorities;
- inspect focus;
- check what is truly important;
- revisit a pattern;
- meta-advice about attention, inertia, layers, contours, signals, capacity, or root causes.

If the reader has to ask "что именно мне сделать?", the line is bad.

# Bank-first workflow

## 1. Separate candidate bank from working bank

Never place fresh ideas directly into the live daily bank.

Use two layers:
- candidate list;
- validated working bank.

Only validated items may feed the real brief generator.

## 2. Validate every new idea before inclusion

Each candidate must pass all of these:
- contains a concrete action;
- understandable without interpretation;
- not motivational or managerial prose;
- not pseudo-smart;
- not "good for good's sake";
- has a visible finish state or obvious next step;
- not a semantic duplicate of an existing bank item.

Reject if:
- it can be pasted into almost any day for almost any person;
- it becomes useful only after an explanation paragraph;
- it sounds better than it works.

## 3. Validate the bank itself regularly

Do not trust a curated bank forever.

Banks drift toward abstraction over time. Run periodic checks for:
- stale abstractions;
- repeated semantic families;
- kantselyarizm / office-speak;
- over-clever wording;
- weak verbs;
- too many generic nouns.

## 4. Dedupe ideas semantically, not cosmetically

Do not allow this failure mode:
- old idea kept;
- wording changed;
- same advice presented as new.

Track repetition at three levels:
- exact phrase;
- same concrete object;
- same idea family.

If one idea already appeared recently, use a different idea, not a paraphrase.

# Writing rules for the final brief

## Keep the old compact shape

When the user prefers the old short daily format, do not inflate the message into an essay just to sound richer.

Short is fine.
Empty is not.

## Preserve usefulness under compression

If a line becomes too abstract after shortening, rewrite the line, not the whole format.

The compact version should still tell the user what to do.

## Keep main and support lines concrete

Both lines should be literal actions.
At least the main line must survive a rewrite test:
- can it be rendered almost verbatim from the validated bank item?
- if the generator turns it into something safer and vaguer, reject the output.

## Avoid pseudo-useful vocabulary

Default ban list for this class of task:
- приоритет;
- фокус;
- инерция;
- внимание;
- контур;
- верхний слой;
- сигнал;
- ёмкость;
- первопричина.

These words are not forbidden in all writing forever, but in short daily briefs they usually signal pseudo-usefulness.

## Prefer visible finish states

Better:
- make a 10-minute stretch;
- close one old tab group;
- answer one delayed message;
- check one route;
- read one short text to the end;
- clear one bag.

Worse:
- reassess priorities;
- inspect your focus layer;
- reconsider what matters;
- reflect on a persistent pattern.

# Weather rule for daily briefs

Weather should read like directly fetched factual text, not like synthetic confidence.

Prefer:
- current condition explicitly visible on the source page;
- at most one conservative forward note.

If part of the line comes from inferred hourly data, keep wording cautious:
- "дождь возможен"
not
- "дождь точно будет".

# Testing and acceptance

Do not accept a fix from one decent sample.

For recurring daily briefs:
1. validate the bank;
2. run the preflight;
3. render several same-date test outputs;
4. verify that the selected lines remain concrete and do not drift back into abstraction;
5. verify that the brief is short and stable.

Acceptance bar:
- validated bank passes;
- rendered outputs stay concrete;
- no repeated stale anchors;
- no pseudo-useful management language;
- short format preserved.

# Pitfalls

## Pitfall: fixing the prompt while leaving a bad bank intact

If the bank is dirty, the renderer will keep producing polished garbage.

## Pitfall: confusing variety with paraphrase

Changing wording is not new value.

## Pitfall: preserving elegance instead of usefulness

A line may sound elegant and still be useless.

## Pitfall: shortening into emptiness

A shorter line is worse if it removes the action.

## Pitfall: using examples that poison the generator

If the prompt includes bad example lines, the model will copy them back.
Only keep examples that would be acceptable as final output.

# References

Add session-specific cleanup notes, validation scripts, or example banks under `references/` when this skill evolves.
