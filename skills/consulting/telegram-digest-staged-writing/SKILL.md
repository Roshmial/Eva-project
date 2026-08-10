---
name: telegram-digest-staged-writing
description: Use when Telegram briefs sound generated. Rebuild them.
---

# Purpose

Use this skill when a recurring daily/weekly brief is structurally correct but still sounds dead, generated, overly polished, or like planning software prose.

This skill is for wording quality rescue, especially when repeated prompt bans and small edits are no longer improving the output.

# When to use

Trigger this skill when one or more of these signals appear:
- the user says the wording is artificial, watery, dry, or not alive;
- the structure is acceptable, but the phrases still sound like AI;
- you keep banning phrases, but the model keeps inventing new surrogate phrasings;
- the user explicitly asks not to be dragged through intermediate iterations and wants the agent to keep refining until the live output improves.

# Core idea

Do not treat this as a prompt-polishing problem.
Treat it as a writing-pipeline problem.

A strong recovery pattern is:
1. pick the actual recommendations first;
2. express them through a curated bank of living line patterns;
3. run a final editor pass;
4. hard-reject surrogate phrasing;
5. if the candidate still sounds generated, throw it away and rebuild from an earlier stage.

# Recommended staged flow

1. Context / day picture
- Gather only the context needed to know what kind of day this is.
- Build a compact internal picture: day type, city, weather basis, one main constraint, optional evening/leisure support, and recent anti-repeat exclusions.
- Do not write the user-facing text yet.

2. Task picker
- Choose exactly:
  - 1 main item with a clear done-state;
  - 2 smaller support items.
- The support items must not be paraphrases of the main item.
- At least one support item should usually be non-work.

3. Line bank first
- Before inventing new sentences, consult a small bank of proven live patterns.
- Reuse a strong pattern and substitute today’s object/action.
- Only write from scratch if no pattern fits.

4. Candidate assembly
- Build several full candidates from the chosen tasks.
- Keep the structure fixed, but vary the rhythm slightly.
- Do not let every candidate become a weather paraphrase.

5. Final editor pass
- Shorten each task line.
- Remove explanation tails, balancing clauses, decorative glue, and fake optimization phrasing.
- Read each line as if it just arrived in Telegram from a familiar person.

6. Hard reject pass
- If a line contains surrogate nouns, editorial scaffolding, or AI-polished filler, reject the entire candidate.
- Regenerate from task-picker or line-bank stage instead of cosmetically repairing a dead sentence.

# Bank-first writing rule

When quality is the problem, a curated line bank beats open-ended invention.

Preferred pattern families:
- `Я бы сегодня ...`
- `Можно днём ...`
- `На вечер можно ...`
- `Если будет настроение, ...`

These are usually better than:
- `Сегодня стоит ...`
- `На сегодня предлагаю ...`
- `Главным сегодня пусть станет ...`
- `Сюда хорошо влезает ...`
- `Сюда просится ...`

# Reject-list design

Build and enforce a hard reject list for this class of work.

Reject immediately when a line contains:
- surrogate nouns instead of a normal thought: `вещь`, `точка`, `момент`, `история`, `кусок`, `блок`;
- planning-software phrasing;
- soft editorial scaffolding;
- fake optimization language;
- explanation tails after an already understandable task;
- wording that a real person would almost never type quickly by hand.

Important rule:
If a line hits the reject list, do not trim it. Replace it.

# Turnkey iteration rule

When the user says `сделай под ключ`, `не дёргай меня на промежуточные итерации`, or equivalent:
- do not stop for intermediate reviews;
- run the loop yourself: patch -> run -> inspect latest live output -> patch again;
- report only after a materially better live result or a real blocker.

# Pitfalls

- Treating a wording-quality problem as if one more ban list will solve it.
- Polishing the same weak candidate again and again.
- Accepting a sentence that is merely a shortened bad AI sentence.
- Letting the model replace one banned phrase with another surrogate phrase.
- Confusing formal correctness with live phrasing quality.
- Using dry bare-imperative lines that technically work but lose Eva’s human voice.
- Asking the user to review every intermediate rerun after they explicitly asked for turnkey refinement.

# Verification checklist

Before considering the rewrite successful, verify:
- the fixed structure is preserved;
- the latest live output is the one being judged;
- none of the three recommendation lines hits the reject list;
- at least one candidate was rebuilt from an earlier stage rather than endlessly polished;
- the result sounds like a Telegram message from a smart familiar person, not a productivity app;
- the user’s strongest complaint from the session is directly addressed by the pipeline, not just by a ban phrase.
