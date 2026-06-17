# Headless post-login crash: two-column grid shell vs flex shell

Контекст класса задач: local-first React/Vite UI, где headless Playwright/Chromium стабильно закрывается после логина уже внутри authenticated shell.

## Симптом, который легко неверно интерпретировать

На first-pass кажется, что:
- ломает `ChatScreen`;
- или ломает `textarea`/composer;
- или виноват `Sidebar`;
- или это CopilotKit/provider/runtime баг.

Но binary search по shell может показать более узкий корень: editable control падает только в desktop two-column layout на CSS grid.

## Рабочая последовательность локализации

1. Подтвердить, что анонимная страница жива, а crash начинается только после логина.
2. Заменить authenticated shell на `auth ok`.
3. Вернуть `Sidebar + пустой main`.
4. Проверить отдельно:
   - messages column;
   - composer column;
   - минимальный editable control.
5. Затем проверить один и тот же control в трёх structural режимах:
   - без sidebar;
   - stacked layout (`sidebar` сверху, editor ниже);
   - two-column desktop shell.
6. Если stacked живёт, а two-column grid падает, проверить ту же структуру на `flex`.

## Ключевой вывод

Если:
- `textarea` без sidebar живёт;
- stacked layout живёт;
- placeholder sidebar + `textarea` в two-column `grid` падает;
- тот же shell на `flex` живёт,

то это не "textarea bug" и не "sidebar bug" по отдельности.
Это layout-конфликт authenticated shell: two-column CSS grid рядом с editable control в headless Chromium.

## Правильный fix-класс

Предпочтительный путь:
- сохранить product-level desktop shell;
- перевести authenticated `app-layout`/эквивалент с `display: grid` на безопасный `display: flex`;
- у sidebar зафиксировать ширину через `width` + `flex-basis`;
- не деградировать UI временными урезаниями вроде:
  - замены `textarea` на `input`;
  - удаления sidebar;
  - постоянного stacked desktop-layout.

## Что не считать доказанным слишком рано

Недостаточно одного факта, что:
- composer падает;
- `textarea` упоминается в последнем working diff;
- browser console пустая.

Отсутствие JS errors здесь не оправдывает версию про React exception. Это может быть именно browser/layout crash.

## Формулировка промежуточного отчёта пользователю

Разделяй:
- что доказано: `grid`-two-column auth shell вызывает headless crash;
- что уже изменено: product `App.jsx` восстановлен, structural CSS-fix внесён;
- что ещё нужно: финальная runtime-приёмка полностью восстановленного UI и визуальная проверка без регрессии качества.
