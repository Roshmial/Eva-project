# Session note — daily brief quality rescue via bank-first staged writing

Context:
- The user was not asking for a new structure; he wanted daily self-development briefs with wording quality around 9/10.
- Repeated direct prompt edits improved correctness but kept producing dead phrasing.
- The explicit user correction was: stop surfacing intermediate iterations; keep refining autonomously.

What changed the trajectory:
1. Stop treating the problem as "one more bad phrase to ban".
2. Split the writing into stages:
   - task picker;
   - line bank;
   - line writer;
   - final editor;
   - hard reject list.
3. Prefer a living line-bank pattern over open-ended generation when the model keeps inventing AI-ish surrogate phrasings.
4. Reject entire candidates that still sound generated instead of cosmetically shortening them.

Useful reject signals from this session:
- `главная вещь`
- `полезная точка`
- `сюда хорошо влезает`
- `сюда просится`
- `сегодня стоит`
- `на сегодня предлагаю`
- `оставить себе`
- dry bare imperative when it kills Eva's voice

Better direction signals from this session:
- `Я бы сегодня ...`
- `Можно днём ...`
- `На вечер можно ...`
- short live lines with no decorative explanation tails

Turnkey rule reinforced by the user:
- If the user says some version of `сделай под ключ` and `не дёргай меня на промежуточные итерации`, the refinement loop should continue silently until there is a materially stronger live result or a real blocker.
