# Chat upload panel and glyph-send smoke drift

Concrete React/Hermes Web drift pattern:

## Old smoke assumption

- file input is present immediately on chat screen
- message placeholder is a long phrase such as `Напишите сообщение для текущего чата…`
- send action is a button named `Отправить`

## New live UI contract

- the file input may exist only after clicking `Файлы`
- the composer placeholder may be simplified to `Сообщение`
- the send action may be a glyph-only button such as `↑`
- admin sections may move from data attributes like `data-admin-section` to visible text buttons (`Пользователи`, `Операции`, `Справочники`)

## Maintenance rule

When this happens, update the smoke to reproduce the real user flow:
1. open chat
2. open `Файлы`
3. wait for the file input to attach
4. attach file
5. fill the current placeholder text
6. click the visible send action actually present in the UI
7. navigate admin/profile sections by current visible labels if the old synthetic attributes are gone

Do not call this a product regression if the live UI still works and only the automation contract drifted.
