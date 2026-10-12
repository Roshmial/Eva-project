# Headless auth-shell binary search

Когда Playwright/Chromium в headless-режиме стабильно закрывает страницу или весь browser process сразу после логина, а анонимная загрузка страницы работает, не лечи это дальше как системную browser/runtime проблему. Это отдельный app-runtime класс дефекта.

## Устойчивый порядок локализации

1. Сначала отделить native browser/runtime от app-runtime.
- Если browser уже стартует, открывает login screen и проходит submit, missing `.so`/Playwright setup больше не главный подозреваемый.
- После этого не продолжать бесконечный цикл переустановки библиотек.

2. Подтвердить backend boot-path отдельно.
- Проверить поштучно, что после логина `auth/login`, `me`, `bootstrap`, `threads`, `files`, `jobs meta` и соседние boot-endpoint'ы отвечают `200`.
- Если boot-endpoint'ы чистые, а browser всё равно падает, корень вероятнее во frontend render path, а не в auth/session.

3. Отделить CopilotKit/runtime wiring от основного auth-shell.
- Если в проекте есть `CopilotKitProvider` или похожий runtime provider, временно убрать его из root render и повторить тот же login-probe.
- Если crash остаётся, не списывать проблему на provider по инерции.
- Для runtime-контуров параллельно проверить discovery-path вроде `/api/copilotkit/info` отдельным HTTP-запросом.

4. Сделать binary search по авторизованному shell.
- Временно заменить весь authenticated render на минимальный `auth ok`.
- Если crash исчез, проблема в одном из дочерних экранов/компонентов, а не в самом логине.
- Затем возвращать блоки по одному:
  - sidebar + пустой main;
  - конкретный screen (`chat`, `profile`, `jobs`, `admin`);
  - внутри screen — крупные зоны (`messages panel`, `composer panel`, modal layer);
  - внутри подозрительной зоны — минимальные интерактивные элементы по одному (`form`, `textarea`, `select`, `details`, file input).

5. Для chat-screen идти не по feature-именам, а по layout-зонам.
- Сначала отделить левую колонку сообщений от правой composer-панели.
- Если messages живут, а composer роняет browser — продолжать уже внутри composer.
- Минимальная развилка: голый shell панели -> только `textarea` -> `form`/submit -> `select` -> `details`/existing files -> file input.

6. Учитывать, что even minimal controlled input может быть триггером.
- Если crash воспроизводится уже на почти пустом composer с одним `textarea`, не обвинять сразу network/runtime provider.
- Проверять отдельно:
  - controlled vs uncontrolled `textarea`;
  - `onChange`;
  - `onKeyDown`;
  - CSS-контекст вокруг sticky/composer-card;
  - только потом более сложные вспомогательные блоки.

## Что считать хорошим промежуточным результатом

Нормально закончить итерацию выводом уровня:
- browser/runtime поднят;
- backend boot-path подтверждён;
- проблема локализована до конкретной screen-зоны или даже до `textarea`-ветки composer;
- CopilotKit provider исключён как первопричина, если его временное удаление не меняет симптом.

Это уже качественно лучше, чем общий статус `после логина падает headless`.

## Как формулировать пользователю

Разделяй:
- что уже точно не является причиной;
- до какого именно компонента/ветки удалось сузить crash;
- какой следующий binary-search шаг логичнее.

Хорошая формулировка: `Проблема уже не в браузерных библиотеках и не в общем auth-flow; crash локализован до composer/textarea-ветки chat-screen`.
