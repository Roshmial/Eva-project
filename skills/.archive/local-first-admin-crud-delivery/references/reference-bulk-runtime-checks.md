# Hermes Web MVP: reference bulk runtime checks

Класс задачи: доведение admin-справочников до паритета с users по bulk UX и live runtime-приёмке.

## Что подтвердилось как полезный устойчивый паттерн

1. Для справочников bulk-паритет нужно проверять отдельно от users, даже если код писался по аналогии.
- Наличие общего паттерна selection-state не гарантирует, что все helper-имена и DOM hooks совпали.
- В этом проходе `safeText(...)` в новом reference flow не существовал в реальном frontend bundle; синтаксис и backend smoke были зелёными, а live UI падал с `ReferenceError`.

2. После cache-busting URL не надо восстанавливать админку через setup-flow.
- Для Hermes Web MVP правильный путь восстановления текущей сессии — `restoreSession()`.
- `bootstrapAdmin()` — это не «повторно открыть админку», а initial setup/create-admin flow.

3. Для справочников полезно разделять три отдельных уровня приёмки.
- selection UX: чекбоксы, master checkbox, summary, disabled/enabled bulk buttons;
- edit/create UX: живое название, скрытый raw JSON, автосборка payload;
- destructive mutation path: backend route для `bulk inactive/delete` + readback/history.

4. Если новый backend route даёт HTML 404, а unit/smoke уже зелёные, первым делом подозревай stale runtime.
- Особенно в схеме `frontend 8790 -> backend 8788`.
- Это не повод сразу переписывать frontend parsing или route path.

## Минимальный live checklist для reference bulk

1. Открыть админку и восстановить сессию штатным путём.
2. Открыть конкретный dataset detail.
3. Проверить:
- row checkboxes;
- master checkbox;
- наличие bulk-кнопок;
- стартовый summary `Ничего не выбрано.`
4. Прогнать безопасный selection-pass:
- `Выбрать всех`;
- снять выбор у одной строки;
- `Снять выбор`;
- проверить summary и disabled-state кнопок.
5. Открыть карточку редактирования существующего элемента и подтвердить:
- subtitle с живым названием справочника и элемента;
- отсутствие видимого JSON textarea;
- корректный status text.
6. Создать или обновить тестовый элемент без ручного JSON и сделать readback.
7. Только потом проверять destructive bulk route и history.

## Когда писать в decision-log

Писать итог по reference bulk только после явного разделения уровня готовности:
- либо подтверждён полный live path, включая mutation-route;
- либо явно зафиксировано, что принят только selection/edit UX, а backend mutation-path ещё блокирован stale runtime или другим live-дефектом.
