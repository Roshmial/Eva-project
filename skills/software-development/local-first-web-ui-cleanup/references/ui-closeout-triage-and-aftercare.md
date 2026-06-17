# UI closeout: triage + aftercare pattern

Использовать после крупного UI cleanup-pass в local-first web MVP.

## Когда это особенно полезно

- после живой browser-приёмки, если до этого были ложные следы между runtime и product bugs;
- когда полезные Playwright/probe-скрипты сначала родились в `tmp/`, а потом контур надо довести до чистого project-state;
- когда пользователь просит "добить всё красиво и до конца", а не оставить рабочий, но захламлённый проект.

## Практический пакет

1. Сделать канонический smoke/run path
- `scripts/browser_runtime_env.sh`
- `scripts/run_ui_acceptance_smoke.sh`
- root `package.json` script для smoke
- README с явным launch path

2. Сделать быстрый triage до полного smoke
Покрыть короткой проверкой:
- frontend HTTP;
- backend `/health`;
- login `/auth/login`;
- bootstrap `/bootstrap`;
- profile `/me`;
- browser probe без product-flow.

Идея triage: быстро ответить, что именно сломано — runtime, auth/bootstrap или сам UI-flow.

3. После стабилизации вынести official scripts из `tmp/`
- временные probe-файлы либо удалить, либо оставить только один доказанный regression-scenario в постоянном месте;
- `tmp/` очистить от debug-хвостов и локального `node_modules`;
- оставить `tmp/README.md` и `.gitkeep`, если нужен пустой временный каталог.

4. После cleanup перепроверить всё ещё раз
Минимум:
- syntax check;
- backend smoke;
- quick triage;
- full UI acceptance smoke.

## UX-уроки из closeout-pass

- Профиль лучше выглядит как одна спокойная summary-плашка + компактные summary tiles, чем как тяжёлая вложенная сетка карточек.
- Для списков файлов полезен короткий meta-text над списком: сколько элементов показано и почему.
- В админских справочниках payload JSON и история изменений не должны постоянно висеть на экране — их лучше сворачивать через `details`.

## Что фиксировать в decision-log

- канонический runtime-launch path;
- канонический quick triage path;
- канонический UI smoke path;
- факт cleanup `tmp/` и повторной проверки после уборки.
