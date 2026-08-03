# Digest output hard gates for Misha

Use this reference when a daily/digest/recommendation stream keeps producing texts that are formally acceptable but still feel weak, generic, or over-explained.

## When to switch into hard-gate mode

Switch immediately when at least one of these happens:
- Misha points to exact bad phrases instead of broad style complaints.
- The same class of defect survives more than one live rerun.
- The assistant starts explaining what is wrong instead of shipping a clean rerun.
- The user asks to fix everything `под ключ` or explicitly asks why you are still explaining.

## Fail-closed release blockers

Do not accept a run if any of these survive in the emitted text.

### 1. Missing concrete anchor
If there is already a valid external anchor in context (event, venue, route, helper suggestion), the final text must use it directly unless it conflicts with the day.

### 2. Missing link
If a concrete place/event/video is recommended, include the link in the final text. A naked title is not enough.

### 3. Soft-control language
Block phrases like:
- `держать день простым`
- `оставить вечер спокойным`
- `держать день коротким`
- `не делать из дня маршрут`

These phrases manage the day rhetorically but add little practical value.

### 4. Vague-control or evaluative tails
Block phrases like:
- `вряд ли нужен`
- `хорошо ложится`
- `нормальный вариант`
- `подходит на сегодня`

Prefer one concrete fact from the source over an evaluative filler line.

### 5. Household pseudo-concreteness
Block lines that pretend to be concrete but are just generic after-trip domestic filler unless the user explicitly brought them in:
- `сумка, стирка, разобрать вещи`
- `бытовые хвосты`
- `всё после дороги`

### 6. Conditional wrappers around the recommendation
Block recommendation wrappers like:
- `если захочется`
- `если выберешься в город`
- `можно сходить`
when the recommendation can be stated directly.

Prefer direct delivery:
- `На сегодня есть [TITLE](URL) — <one concrete fact>.`

## Source-grounded fact preference

When a helper/source block already contains usable facts, prefer them over commentary:
- date range
- start time / opening window
- registration requirement
- free entry / ticket note
- exact venue

Bad pattern:
- link + soft evaluation

Better pattern:
- link + one concrete operational fact from the source

## Execution rule

When a rerun still fails quality:
1. identify the exact surviving phrase class;
2. promote that class into an explicit reject rule at the highest active surface;
3. rerun immediately;
4. do not present the task as done until the emitted artifact is clean.
