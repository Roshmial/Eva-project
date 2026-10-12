# August 2026 daily-plan quality corrections

Session lesson: for Misha's morning daily, the hard problem was not the presence or absence of an event. The hard problem was wording quality. The brief kept degrading into either:
- event-centric narration (`есть событие / нет события` as the whole logic), or
- dry pseudo-productivity phrasing (`зависший кусок`, `остальное входящее`, `один рабочий материал`, etc.).

## Durable corrections

### 1. The brief is a plan, not a mood note
The user explicitly restored the original contract:
- exactly 1 main goal;
- exactly 2 small goals;
- the output must tell him what to do today.

Do not drift into atmospheric lines, day classification, or commentary about the shape of the day.

### 2. Event presence is not the main axis
Bad framing:
- if event exists -> external recommendation
- if no event exists -> work surrogate

Better framing:
- identify the day type only as hidden context;
- still produce 1 main + 2 small tasks;
- if there is no concrete external hook, do not replace it with meta-lines about the day.

### 3. Ban meta-day classification in user-facing prose
These felt artificial and should be treated as hard failures:
- `сегодня без отдельного внешнего сюжета`
- `без специального сюжета`
- `обычный рабочий день`
- similar "служебная классификация дня вслух" phrasing.

### 4. Ban pseudo-productivity wording
Hard-failure family:
- `один зафиксированный результат`
- `зависший кусок`
- `остальное входящее`
- `вход обратно в работу`
- `довести до отправки один рабочий текст или схему`
- `короткая запись`
- similar phrases that sound like compressed planning-software language instead of normal chat.

### 5. Water is the enemy even when the structure is correct
A line is bad if it explains itself instead of simply proposing an action.

Examples of water / explanatory tails to cut:
- `на сегодня предлагаю`
- `оставить себе 25–30 минут`
- `по действительно важной теме`
- `которое потом уже не нужно будет...`
- `чтобы день закончился...`
- `пока сухо и не жарко`
- `короткий тихий слот без экрана`

Editing heuristic:
- if a task line can be shortened by 20–40% without losing the action, it is not ready.

### 6. Structure alone is not success
Even with the correct 1+2 structure, the user may still reject the result if the texture is not alive enough.

Therefore, after selecting the best candidate, run a final edit pass with this question:
- would a familiar person plausibly type this line by hand in Telegram?

If the answer is no, the candidate is still bad.

### 8. When prompt healing stalls, move the logic into cron structure
The user explicitly pushed back that the prompt was no longer the right lever.

Structural fix:
- let the preflight script emit `structured day anchors`, `task families`, `suggested raw tasks`, and `render constraints`;
- keep the agent-layer mostly as a renderer and rejector of dead variants, not as the place that re-decides the day from scratch;
- if there is a close confirmed next-day personal anchor, it is acceptable for one of the two small tasks to point at it directly.

### 9. "Под ключ" means no intermediate quality bargaining
If the user says "сделай под ключ" and gives a 9/10 quality bar:
- do not stop to report that the current version is 8/10 or "already much better";
- keep iterating silently on your own;
- only surface a result once the latest live output actually clears the bar, or name a real blocker.
