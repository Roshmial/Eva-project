# 178: attachment hardening + launcher/env drift

## Когда это вспоминать
- Пользователь говорит, что assistant «собрал документ, но он не открылся / не приложился / снова идёт текстом».
- После ручного restart `/api/health` зелёный, но обычные ответы модели внезапно падают.

## Что оказалось важным

### 1. Разделять два независимых дефекта
Один и тот же user-facing симптом `документ не работает` может состоять из двух слоёв:
- backend/file-generation defect: assistant-message завершился, но вместо attachment в `meta.attachments` сохранился обычный текст с локальным путём (`/home/hermes/...` или `sandbox:/home/hermes/...`);
- frontend/open-path defect: attachment уже есть, но открытие идёт без авторизации, и пользователь получает `auth_required`.

Нельзя закрывать тему после фикса только одного слоя.

### 2. Более жёсткая backend-нормализация для assistant-file replies
Для Hermes Web MVP полезен устойчивый fallback:
- парсить не только `MEDIA:/...`, но и голые локальные пути вида `/home/hermes/...`, `/tmp/...`, а также `sandbox:/home/hermes/...`;
- преобразовывать их в `meta.attachments`;
- убирать сырой путь из user-facing текста;
- если attachment найден, дописывать нейтральную формулировку вроде `Файл приложен к сообщению`, чтобы UI не жил только на тексте модели.

Это защищает от downstream-ответов, где модель или runtime вернули локальный путь текстом вместо ожидаемого structured attachment.

### 3. Download/open path лучше делать терпимым к transport-варианту auth
Если attachment открывается отдельным GET, полезен fallback-порядок auth:
- `Authorization: Bearer ...`
- auth cookie
- `access_token` в query для GET download/open route

Это особенно полезно для assistant-generated attachments, где UI может открывать файл новым окном/ссылкой, а не тем же JS fetch-путём.

### 4. Экспорт может казаться рабочим при сломанном model runtime
Сильный диагностический сигнал:
- export/docx flow проходит,
- но обычный assistant-answer падает с `hermes_api_key_missing`.

Это не противоречие. В таком контуре export-route может собирать файл локально из уже существующего message-content без нового вызова модели. Значит, root cause не в file-export как таковом, а в том, что backend после restart поднялся без полного runtime env.

### 5. Health недостаточно
После restart обязательна двойная проверка:
- `GET /api/health` или `/api/service-info`
- и один реальный model-backed message round-trip

Если второй шаг пропустить, легко принять сломанный после restart chat-runtime за рабочий контур.
