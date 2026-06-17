# Runtime env and acceptance account

Когда local-first web контур уже почти выровнен, последние ложные падения часто идут не из продукта, а из смеси трёх вещей: legacy-порты в вспомогательных скриптах, устаревшие demo-логины и onboarding-modal, который перекрывает живую навигацию.

## Что сохранять как durable-паттерн

### 1. Канонический contour должен собираться из одного env-слоя

Минимальный набор переменных:
- bind host
- frontend port
- backend port
- sidecar/runtime port

Из них должны вычисляться:
- frontend URL
- backend base
- backend API URL
- CORS allow-origin
- runtime/sidecar URL
- smoke/browser base URLs

Практическое правило:
- не держать эти значения отдельно в launcher-скриптах, `vite.config.js`, sidecar entrypoint, acceptance smoke и debug probes;
- предпочитать один `runtime_env.sh` или эквивалентный слой композиции.

### 2. Нельзя считать runtime portable, пока не проверен alternate-port путь

Недостаточно, что contour работает на текущих `8791/8793/8794`.

Нужно отдельно подтвердить:
- что derived URLs действительно собираются из переменных;
- что server deploy с другими портами не потребует правок по нескольким файлам;
- что acceptance и sidecar не содержат скрытых legacy-литералов.

### 3. Для live acceptance не полагаться на исторический demo-admin

Если база уже живая и `demo_mode=false`, связка вроде `admin@demo.local / demo123` не должна считаться бессрочным smoke-инвариантом.

Устойчивый путь:
- завести или найти отдельный acceptance-аккаунт;
- использовать его в browser smoke через env;
- не менять основной admin-пароль только ради приёмки.

### 4. После логина сначала проверь overlay/onboarding

Симптом:
- кнопки `Задачи`/`Управление`/`Профиль` видимы,
- но click не проходит,
- Playwright пишет, что `.modal-backdrop-react` intercepts pointer events.

Типовая причина:
- onboarding-modal вроде `Давай настроим, как с тобой взаимодействовать`.

Устойчивый acceptance-path:
- сначала искать кнопку `Позже`;
- кликать именно её;
- только потом идти в admin/jobs/profile flows.

Не полагаться только на:
- `Escape`;
- клик по backdrop;
- повторение того же nav-click без DOM-проверки.

### 5. Если policy/admin smoke говорит, что UI пустой, сначала проверь live DOM

Сначала снять:
- реальные `id` control-элементов;
- `data-source-key` или текущие атрибуты selectable items;
- тексты живых кнопок сохранения;
- заголовок секции в текущем UI.

Только потом чинить automation.

Типичный drift:
- старый smoke ожидает `Сохранить policy` и старый layout;
- текущий UI уже показывает `Сохранить и включить` / `Сохранить и выключить` и другую структуру секции.

Вывод:
- это не обязательно продуктовый дефект;
- это часто просто drift acceptance-контракта.
