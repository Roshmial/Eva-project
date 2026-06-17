# False-positive file-intent cases in Hermes Web

Класс проблемы:
обычный текстовый запрос или обсуждение багов вокруг файлов ошибочно попадает в file-flow (`generated_file_response` / `message_export`) вместо обычного assistant reply.

## Что проверять в live runtime

1. Позитивный кейс
- `Собери файл`
- `Пришли файл`
- `Выдай мне итоговый файл`

Ожидаемо:
- `message_kind=file_response`
- non-empty `attachments`
- реальный `download_url`

2. Негативные кейсы
- `Исправь баг с некорректной генерацией файлов`
- `Я не просил ничего собирать, задача была — включи лог`
- `Почему снова ответ в формате word?`
- обычный текст с нейтральным словом `экспорт` или `выгрузка`

Ожидаемо:
- НЕ `file_response`
- НЕ `generated_file_response`
- нет attachments
- нет claim-ов «собрала файл»
- нет локальных путей вроде `/home/hermes/...` в публичном ответе

## Практический признак root cause

Если прямой запрос `собери файл` работает, но фразы про баги/логирование внезапно создают `.docx`, проблема почти точно в слишком широком file-intent detector, а не в download endpoint и не в frontend rendering.

## Полезные live поля для сверки
- `meta.message_kind`
- `meta.source`
- `meta.attachments`
- `meta.exported_message_id`
- `meta.generated_from_request`
- `content` assistant message

## Типовые ошибочные триггеры
Слишком широкие маркеры вроде:
- bare `экспорт`
- bare `выгруз`
- любое вхождение `word`
- любое вхождение `файл` без проверки контекста

## Минимальный acceptance standard
Фикс нельзя считать завершённым, пока не проверены оба направления:
- positive intent: direct file request даёт attachment;
- negative intent: discussion about file bugs does not enter file-flow.
