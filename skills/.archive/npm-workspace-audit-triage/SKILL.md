---
name: npm-workspace-audit-triage
description: Use when npm audit warnings remain after install/update.
---

# Когда применять

Используй этот навык, когда после `npm install`, `npm update`, `npm audit fix` или post-update проверки остаются npm warnings, особенно в workspace-монорепе.

Типичные сигналы:
- `npm audit` продолжает показывать high/critical warnings после частичной remediation;
- `npm audit fix` предлагает `--force`, major bump или странный downgrade;
- install прошло, runtime живой, но doctor/audit всё ещё ругается на `web` / `ui-tui` / dev-deps;
- нужно понять, это реальная runtime-дыра или build/dev advisory noise.

# Цель

Не делать слепой `npm audit fix --force`, пока не доказано, что:
1. warning действительно относится к текущей установленной версии;
2. remediation не ломает dependency tree;
3. residual issue нельзя безопасно отделить как dev/build-only хвост.

# Базовый порядок

## 1. Сначала приведи install tree в согласованное состояние

Минимум:
1. `npm install`
2. если есть allow-scripts warnings — `npm install-scripts ls --json`
3. при локальном self-hosted контуре и понятных пакетах допускается `npm install-scripts approve --all`
4. после approve ещё раз `npm install`

Важно:
- `approve --all` может записать `allowScripts` в корневой `package.json`;
- это уже не чисто временное состояние, а реальное изменение install tree;
- после approve проверяй `git diff` и явно фиксируй, что именно поменялось.

## 2. Раздели root audit и workspace audit

Проверяй отдельно:
- `npm audit --json`
- `npm audit --workspace <name> --json`

Смысл:
- root может смешивать desktop / packaging / optional / dev зависимости;
- workspace audit лучше показывает, где именно остался хвост.

## 3. Для каждой уязвимости делай factual verification через `npm ls`

После любого `npm audit fix` не доверяй только summary.

Проверяй фактическое дерево:
- `npm ls <pkg1> <pkg2> --workspace <name>`

Это нужно, потому что `npm audit` может:
- продолжать ругаться на advisory по semver range;
- предлагать misleading `fixAvailable`;
- советовать major bump или даже downgrade, хотя фактически уже стоят свежие patch/minor версии.

## 4. Разделяй классы хвостов

### A. Безопасно закрываемые install tails
- отсутствующий package после update;
- pending install-script approvals;
- stale lockfile, который чинится обычным `npm install` / точечным `npm audit fix --workspace ...` без ломки дерева.

### B. Dev/build advisory noise
- eslint/minimatch/brace-expansion цепочка в lint-only deps;
- packaging-only deps (`electron-builder`, `electron-winstaller`, etc.), если user-facing runtime от них не зависит прямо сейчас;
- warnings, которые doctor сам помечает как build-tool advisory.

### C. Отдельная maintenance ветка, не post-update хвост
- remediation требует `--force`;
- нужен major bump ключевой зависимости;
- появляется peer-dependency conflict;
- npm предлагает downgrade как якобы fix;
- после попытки fix дерево перестаёт резолвиться.

В классе C останавливай closeout и явно говори, что дальше начинается отдельная dependency-maintenance работа.

# Практический паттерн

Рабочая последовательность для self-hosted Hermes / похожей монорепы:
1. `npm install`
2. `npm install-scripts ls --json`
3. `npm install-scripts approve --all`
4. повторный `npm install`
5. `npm audit --workspace web --json`
6. `npm audit --workspace ui-tui --json`
7. точечный `npm audit fix --workspace <name>` только там, где это не требует force
8. `npm ls ... --workspace <name>` для подтверждения фактических версий
9. отделить оставшийся dev/build advisory от реального runtime риска

# Pitfalls

- Считать `npm audit` summary достаточным доказательством реального риска.
- Делать `npm audit fix --force` только ради нулевого счётчика.
- Не проверять, что `approve --all` изменил в `package.json`.
- Смешивать runtime-дыру и lint/build-only advisory в один общий "сломано npm".
- Подавать peer-conflict после fix как случайный шум, если он уже означает переход в отдельную maintenance-ветку.

# Что сообщать пользователю

В финале разделяй:
- что реально починилось в install/runtime;
- какие warnings остались только в dev/build contour;
- какие следующие fixes уже требуют отдельной dependency-maintenance ветки.
