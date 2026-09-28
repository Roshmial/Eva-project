---
name: bank-first-daily-brief-design
description: Use when daily briefs need a bank-first rebuild.
---

# Purpose

Use this skill when a recurring daily brief, morning message, or compact proactive digest starts sounding artificial, repetitive, or "smart-looking but not useful".

This skill is for the class of problems where the issue is not one bad sentence but the whole contour:
- the bank contains weak ideas;
- the renderer paraphrases selected items into mush;
- anti-repeat only checks history, not the current message shape;
- prompt edits keep treating symptoms instead of replacing the pipeline.

# When to use

Trigger this skill when the user says or clearly implies things like:
- stop repeating the same idea;
- the problem is not the format, it is that you keep dragging the same thought;
- good advice should be a concrete action;
- this still sounds like meta-advice, motivation, or management prose;
- do not keep patching this, rebuild it from scratch.

# Core rule

A good daily-brief item should read close to `сделай ...`.

If a candidate line needs explanation, interpretation, or justification before it sounds useful, it is not ready for the working bank.

# Design principles

1. Bank-first, not vibes-first.
- Do not improvise the message from general prompt style alone.
- Keep a curated bank of concrete candidate actions.
- The renderer should mostly emit selected lines, not invent the day's logic from scratch.

2. Validate before admission.
- New ideas go to a candidate stage first.
- Only validated ideas enter the working bank.
- Never place a weak idea into the bank and hope the final wording pass will rescue it.

3. Reject abstract-management language at the bank level.
- Bad families include: priorities, focus, importance, inertia, attention, layers, contexts, signals, root causes, capacity, and similar meta-language.
- If the line sounds like advice about self-management rather than a direct action, reject it.

4. Prefer visible finish states.
- Good lines let the user see what "done" means.
- Examples: do a short stretch, answer one delayed message, clear one bag, read one short text, check one route, remove one stale tab group.
- Avoid lines that sound portable across almost any day without changing the object.

5. Anti-repeat must work on two levels.
- Cross-day repetition: do not repeat recent ideas or paraphrase them as if they were new.
- Intra-brief repetition: do not let the main and support lines fall into the same action family, such as two cleanup tasks or two digital-hygiene tasks.

6. Same-date reruns should be stable.
- If you rerun on the same day while tuning style, the contour should prefer the same selected actions unless a stronger reason forces change.
- Stability is better than fake novelty.

7. Simplify the renderer.
- Once preflight already chose the lines, the final prompt should demand near-verbatim rendering.
- Do not let the model "improve" the line into something broader, safer, or more polished.

# Recommended workflow

1. Reset the bank when contamination is structural.
- If the existing bank is full of abstract or pseudo-useful items, do not prune it one phrase at a time.
- Rebuild the working bank from scratch.

2. Split bank items into lightweight families.
- Use families such as body, reading, communication, digital, finance, life-admin, planning, notes, work, video, music, walk.
- Families are for selection logic, not user-facing output.

3. Add a validator.
- Check that each item has:
  - a concrete verb;
  - a direct object or visible finish state;
  - no banned abstract language;
  - short length;
  - correct lead-in shape for its role.

4. Make preflight select the pair.
- Choose the main item with recency and family cooldown.
- Choose the support item with extra guards:
  - not from the same family as main;
  - low token overlap with main;
  - not a recent repeat.

5. Keep the prompt thin.
- Weather/date line from source.
- Main line from selected main.
- Small line from selected small.
- No extra motivation, no reflective commentary, no re-interpretation.

6. Verify with repeated runs.
- Run the same-day generation several times.
- Confirm stability.
- Then simulate recent-history collisions and confirm the selector moves to different families when the recent tail already used the previous pair.

# Pitfalls

- Treating one bad output as a wording issue when the whole bank is rotten.
- Letting the model paraphrase selected concrete lines back into abstract management prose.
- Checking repetition only against previous days and forgetting that the two lines inside the current message can also duplicate each other semantically.
- Rewarding elegant phrases that still do not tell the user exactly what to do.
- Mistaking same-date stability for a bug. The bug is not stability; the bug is stale or duplicated selection.
- Keeping old poisoned examples alive in the prompt after the user explicitly asked for a rebuild.

# Verification checklist

Before calling the new contour good, verify:
- the bank passes a validator;
- bank items are concrete actions, not meta-advice;
- selected main and small belong to different families;
- same-day reruns stay stable;
- recent-history simulation pushes the selector to a different pair when yesterday already used the current family/object;
- final rendered output stays close to the selected bank items and does not drift back into abstraction.
