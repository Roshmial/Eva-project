# User-space fontconfig + multipart smoke reference

## Когда это пригодилось

Симптомы в Linux-окружении без root:
- Playwright Chromium то поднимался, то закрывал page/context на `goto` или `reload`
- Hermes browser tools через CDP иногда работали, затем снова становились нестабильными
- UI smoke давал противоречивые результаты: часть побочных эффектов происходила, но в браузере всё ещё виделся сбой

## Стабилизирующий приём

Вместо установки системного браузера был использован существующий Playwright Chromium, а недостающий шрифтовой слой собран в user-space runtime.

Принцип:
1. Скачать без root пакеты с `fontconfig` и базовыми шрифтами.
2. Распаковать их в пользовательский каталог.
3. Запускать Chromium с env:
   - `FONTCONFIG_PATH`
   - `FONTCONFIG_FILE`
   - `XDG_DATA_DIRS`
4. После этого повторять проверку page open, auth boot и CDP attach.

## Что дало на практике

После добавления user-space `fontconfig` и базовых шрифтов:
- plain Playwright Chromium открыл localhost стабильно
- authenticated boot стал воспроизводимым
- Hermes browser tools снова смогли работать через CDP на localhost

## Важный паттерн проверки

Если UI smoke с загрузкой файла ведёт себя странно:
- не ограничиваться browser-side наблюдением
- обязательно воспроизвести multipart-запрос напрямую против API

Почему это важно:
- в кейсе UI уже успевал показать сохранённый файл и часть диалога
- но API на самом деле возвращал `500`
- реальный корень оказался в backend response path, а не в browser runtime

## Конкретный backend smell

Обнаруженный дефект класса:
- после `INSERT ... RETURNING id` код выполнил ещё один `execute()` и только потом вызвал `fetchone()` у результата insert
- итог: downstream row/ID оказался недоступен, а сериализация ответа упала

Практический вывод:
- если handler как будто успевает записать данные, но падает при формировании ответа, проверь порядок чтения `RETURNING` немедленно

## Рекомендуемая последовательность будущей отладки

1. Проверить plain localhost open в браузере.
2. Проверить auth bootstrap с token preseed до первой загрузки.
3. Проверить Hermes CDP path.
4. Прогнать UI smoke.
5. Если file/chat flow выглядит неоднозначно — повторить его прямым API-вызовом.
6. Если API падает, локализовать traceback в handler до дальнейших UI-правок.
