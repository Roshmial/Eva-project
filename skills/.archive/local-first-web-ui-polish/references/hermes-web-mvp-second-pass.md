# Hermes Web MVP second-pass lessons

Короткая session-specific выжимка для задач по полировке local-first web UI.

## Jobs detail / `Unexpected token '<'`

Симптом:
- при выборе Hermes job frontend показывал `Unexpected token '<', "<!doctype ..." is not valid JSON`.

Рабочая интерпретация:
- frontend ждал JSON, а backend отдал HTML-страницу ошибки.

Корень, который стоит проверять первым:
- mixed id types;
- local jobs могут быть numeric;
- Hermes jobs могут быть string id;
- нельзя сначала насильно искать string job id в local DuckDB таблице с `INT64`-ключом.

Практический урок:
- сначала исправь backend route branching;
- затем добавь в frontend `api()` явную ошибку на случай не-JSON ответа.

## Admin UX

Устойчивое правило для Миши:
- `Создать пользователя` — отдельный сценарий;
- `Редактировать` — только из строки пользователя;
- user/reference формы должны открываться overlay/modals поверх таблицы, а не под ней.

## Chat UX

Не путать две задачи:
- sticky/introduction behavior верхней чат-плашки;
- порог появления кнопки `Вверх`.

Правильная эвристика:
- кнопку `Вверх` показывать, когда intro/welcome блоки ушли из viewport;
- поведение верхней плашки проверять относительно chat screen, а не как глобальный sticky всего окна.

## Overview

Если пользователь просит `дашборды`, не считать KPI-карточки достаточным выполнением.
Нужны именно визуальные графические блоки по web-first данным: пользователи, чаты, сообщения, задачи, события.
