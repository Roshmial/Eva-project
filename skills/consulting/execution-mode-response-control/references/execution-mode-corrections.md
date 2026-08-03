# Execution-mode corrections from this session

## Why this was added

The user repeatedly signaled that explanation-heavy turns were the wrong mode once the task had already become an execution loop.

Representative user corrections:
- `А сразу нельзя жестко?`
- `Так, и что дальше делать будешь?`
- `А зачем сейчас объясняла?`
- `Делай давай, а`
- `Под ключ исправь все`

## Durable lesson

In iterative fix-and-rerun work, user complaints like these are not style-only feedback. They redefine the operating mode:
- stop analyzing the defect class in prose;
- turn each complaint into an acceptance check;
- patch and rerun immediately;
- report only verified changes.

## Concrete acceptance-pattern example

User complaint cluster:
- `где ссылка?`
- `появились бытовые хвосты`
- `появилась еще одна точка`
- later: complaints about formulas like `держать простым`, `оставить спокойным`

Correct handling pattern:
1. convert each complaint into a hard fail condition;
2. patch generator/critic/runtime, not just one prompt fragment;
3. rerun live output;
4. reject any result that still contains even softer variants of the same class;
5. continue until the latest run passes all checks.

## TG QA carry-over lesson

When the user says previous residue must also be processed, do not stop at the current window.
Extend the same weekly contour to:
- current 7-day residue;
- full historical backlog;
- automatic persistence of safe suggested reclassifications where the alternative type is explicit enough.

## What future agents should avoid

- giving a taxonomy of the problem after the user already requested a fix;
- treating `better than before` as done;
- presenting prompt/code edits without a live rerun;
- answering workflow pushback with more explanation instead of action.
