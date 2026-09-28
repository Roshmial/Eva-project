# Proposal composition trigger guard

Use this when a local-first chat/runtime can both:
1. collect data into rows/files, and
2. compose a second-stage proposal/cost/resource artifact.

## Core lesson

Do not trigger proposal composition from a bare mention of `КП` or `проект КП` in the request subject.

Bad trigger:
- `Собери из файлов в csv по теме проект КП ...`

Good triggers:
- `Подготовь КП по этим материалам`
- `Сформируй проект КП`
- `Подготовь коммерческое предложение`
- `Оцени стоимость`
- `Оцени ресурсы / состав команды`

## Durable pattern

1. Keep two layers separate:
   - dataset/file collection
   - proposal/cost/resource composition
2. Add an explicit intent detector for proposal composition.
3. Require action + proposal/estimate phrasing, not only noun presence.
4. If explicit proposal intent is present, let composition-format default (typically `md`) win over generic export heuristics like `в файл` / `документ`.
5. Preserve the normal collection route for requests where proposal words appear only inside the topic or source materials.

## Verification pattern

Add regressions for both sides:
- positive: explicit `подготовь проект КП ...` creates composition artifact
- negative: ordinary collection like `в csv по теме проект КП ...` stays on dataset/file path

## Runtime caution

When deploying this class of change to prod, restart the backend through the canonical runtime env bootstrap, not a raw process relaunch with partial env. Otherwise the process can come back in the wrong mode and invalidate the acceptance result.
