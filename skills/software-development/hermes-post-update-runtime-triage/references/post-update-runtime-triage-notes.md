# Post-update runtime triage notes

Короткая памятка по симптомам, которые полезно отличать при диагностике Hermes после обновления.

## Browser tools: ложноположительный navigate

Симптом:
- `browser_navigate("https://example.com")` возвращает success и целевой `title/url`;
- но `browser_console` показывает `about:blank`;
- `browser_snapshot` пустой;
- `browser_vision` видит белый экран.

Интерпретация:
- это не подтверждённая успешная навигация;
- подозревать нужно CDP attach, browser session reuse, tab state или локальный browser runtime.

Минимальный верификационный набор:
1. `browser_navigate`
2. `browser_console` с `location.href`, `document.title`, `document.readyState`, `document.body.innerText`
3. `browser_snapshot`
4. при необходимости `browser_vision`
5. при необходимости локальная проверка CDP endpoint и списка вкладок

## Hermes doctor: зависание после state.db exists

Если `hermes doctor` стабильно доходит до:
- `~/.hermes/state.db exists (N sessions)`

и потом больше не продвигается, полезно проверить код `hermes_cli/doctor.py` и вызов `_db_opens_cleanly()` из `hermes_state.py`.

Что внутри `_db_opens_cleanly()` важно:
- `PRAGMA journal_mode`
- `PRAGMA integrity_check`
- `SELECT COUNT(*) FROM sessions`
- rollback write probe в `sessions/messages`

Практическая эвристика:
- если `SELECT COUNT(*) FROM sessions` выполняется быстро;
- `BEGIN IMMEDIATE` выполняется быстро;
- а doctor всё равно зависает после строки про `state.db`;

то тяжёлый кандидат номер один — `PRAGMA integrity_check`, особенно на большой `state.db`.

## Что не путать между собой

Не склеивать в одну причину:
- browser runtime regression;
- long-running `state.db` integrity check в doctor;
- warning про `Config version outdated`;
- отсутствие OAuth login у необязательных провайдеров.

Итоговый отчёт после обновления должен разделять:
- подтверждённо рабочие функции;
- частично рабочие / подозрительные зоны;
- credential-зависимые части, которые не тестировались.
