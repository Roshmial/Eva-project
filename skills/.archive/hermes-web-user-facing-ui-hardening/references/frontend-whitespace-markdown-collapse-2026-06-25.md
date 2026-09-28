# Frontend whitespace normalization collapsing markdown blocks (2026-06-25)

## Симптом

- В `KPI` длинный structured answer приходил с чистым `display_text`, но в live UI рендерился почти как сырой массив.
- Обычные assistant-ответы типа `Расскажи о себе` тоже теряли читаемость: абзацы, списки и подзаголовки схлопывались в простыню.
- В DOM у проблемного `KPI`-сообщения почти весь ответ оказывался внутри одного `message-md-paragraph`; `---`, `###` и markdown-таблица оставались сырым текстом внутри paragraph.

## Root cause

Причина была не в backend `display_text` и не в основном markdown parser, а во frontend-нормализации текста перед `marked.lexer(...)`.

Проблемная логика:

```js
.replace(/\s{2,}/g, ' ')
```

Такой regex схлопывает не только лишние пробелы, но и переводы строк, потому что `\s` включает `\n`.

Из-за этого до markdown parser доходил уже испорченный blob:
- `\n\n` между абзацами исчезали;
- heading'и и `---` прилипали к предыдущему paragraph;
- markdown-таблицы теряли block boundary и больше не распознавались как table block.

## Безопасный fix

Сохранять переводы строк и схлопывать только горизонтальные whitespace-символы.

Рабочая замена:

```js
.replace(/[\t\f\v\u00a0 ]{2,}/g, ' ')
.replace(/\n{3,}/g, '\n\n')
```

## Как проверять

Не ограничиваться build'ом. Нужна live DOM-проверка user-facing message:

1. Взять реальное проблемное assistant-сообщение.
2. Сравнить backend `display_text` с тем, что видит UI.
3. Посмотреть DOM последнего bubble:
   - до фикса: почти всё внутри одного `message-md-paragraph`;
   - после фикса: должны появиться отдельные `hr`, `message-md-heading-*`, `message-md-table`, `message-md-list`.

## Вывод

Если markdown внезапно "весь стал plain-text paragraph", сначала проверь frontend whitespace normalization до parser'а. Это отдельный класс дефекта и его легко ошибочно принять за проблему parser'а, reasoning-cleanup или backend serialization.
