---
name: react-runtime-acceptance-polish
description: "Live-приёмка и финальная полировка local-first React UI после функциональных фиксов: runtime-проверка, onboarding, runtime-справочники, decision log."
---

# Когда использовать

Используй этот skill, когда React UI уже в целом работает, но нужно честно подтвердить live-приёмку, быстро закрыть мелкие UX-хвосты и довести экранный контур до product-level baseline перед переходом к другим разделам.

# Цель

Не просто собрать проект без ошибок, а довести экранный контур до состояния, в котором основные пользовательские сценарии проходят end-to-end, нет стыдных runtime-дефектов, а итог фиксируется в decision log только после live-подтверждения.

# Порядок работы

1. Сначала подтвердить runtime-контекст
- Проверить, какой runtime является источником истины: порт, актуальные процессы, active session.
- Не смешивать старые логи, старые процессы и новый runtime.

2. Отделить кодовую готовность от продуктовой готовности
- Успешная сборка обязательна, но недостаточна.
- После каждого смыслового пакета правок делать live-pass по DOM и реальным сценариям.
- Если runtime пустой или body не монтируется, сначала снять console/runtime errors и найти JS exception или shape mismatch.

3. Acceptance-pass вести по сценариям
- Для chat/profile contour минимум проверить:
  - zero-state и welcome card;
  - starter prompts;
  - send-flow, включая Enter, disabled/pending state и финальный ответ;
  - file-open flow;
  - archive/unarchive/list-all chats;
  - profile response settings;
  - first-run onboarding у нового или пустого пользователя.

4. Runtime-справочники считать подключёнными только при реальном использовании
- Недостаточно, что backend отдаёт datasets.
- Нужно подтвердить, что форма реально использует эти данные в select/combobox/summary/defaults.
- Проверить фактический shape данных: это может быть массив или объект вида `{ items: [...] }`.
- Helpers для options должны поддерживать оба варианта.
- Сохранять fallback на текущее пользовательское значение, если оно историческое и уже не входит в текущий справочник.
- Если локальный код уже исправлен, а live UI всё ещё показывает старые label/type/placeholder, не списывай это сразу на browser cache или неудачную сборку. Сначала проверь, не живёт ли этот dataset в persisted runtime-справочнике (`reference_items`/аналог) и не продолжает ли backend отдавать старую версию через `/api/bootstrap`.
- Для встроенных system datasets вроде `job_templates` проверяй не только кодовый source-of-truth, но и синхронизацию persisted данных при старте. Однократный seed без последующего refresh — частая причина, почему live форма продолжает рендерить старые поля даже после корректного frontend patch.
- Если UI подозрительно показывает старый form-contract, делай тройную проверку: (1) что backend live bootstrap реально отдаёт нужные label/type/rows/layout; (2) что frontend после reload читает свежий payload; (3) что финальный DOM формы действительно рендерит нужный control (`textarea` vs `input`) и нужные размеры.

5. Для structured UI-артефактов проверять последний mile renderer, а не только backend contract
- Если backend уже возвращает `message_kind` вроде `dashboard_result`, `clarification_request` или другой structured payload, этого недостаточно для product-готовности.
- Нужно отдельно проверить, что экранный renderer реально читает нужный `message.meta.*` ключ, а не показывает только `content` fallback.
- Сигнал разрыва контракта: в данных есть полноценная структура (`summary_cards`, `sections`, `sources` и т.п.), а пользователь на экране видит только обычный текстовый пузырь.
- При такой диагностике сначала ищи gap в message/component renderer, а не объясняй проблему ограничениями LLM или пользовательским запросом.
- Если visual browser-pass временно заблокирован окружением, не останавливайся на `build ok`: дополнительно проверь live-served bundle/asset, что новый renderer действительно попал в отдаваемый production JS, и честно пометь verification как частично ограниченную средой.
- Для chat/file/recurring UX допустим fallback-путь приёмки: подтвердить affected payload через live HTTP/API, проверить что frontend уже отдаёт новый production asset с нужными renderer markers, а для спорного path временно seeded acceptance-thread создать и затем удалить после проверки, чтобы не оставлять мусор в runtime.

6. Onboarding проверять отдельным тестовым пользователем
- Отсутствие modal у текущего пользователя не доказывает баг и не доказывает фикс.
- Для first-run сценария использовать пустого пользователя без целей, ограничений и контекста.
- После проверки по возможности вернуть runtime в стандартный тестовый аккаунт; если не удаётся, честно отметить, под кем осталась инструментальная сессия.

6. Мелкие UX-хвосты не откладывать
- Если acceptance выявил маленькие, но реальные дефекты, чинить их сразу тем же циклом.
- Особенно: склеенный label/copy, английский текст в русском UI, неявный архивный статус, слипшаяся action-группа.

7. Разделять визуальную правду и текстовый слой
- Если визуально блок уже исправлен, но innerText или accessibility snapshot всё ещё выглядит неидеально, фиксировать отдельно визуальный результат и отдельно остаток в текстовом слое.
- Не выдавать одно за другое.

8. Decision log обновлять только после финального live-pass
- Сначала закрыть фактические хвосты.
- Потом коротко зафиксировать: контекст, что было критичным, что реализовано, что подтверждено live и какой честный verdict по качеству.

# Чек-лист приёмки

- Сборка проходит.
- Runtime загружается без JS errors и пустого mount.
- File open/download не даёт ложный 404.
- Welcome/onboarding/copy выглядят нормально и не слеплены.
- Runtime references реально используются в форме.
- Новый пустой пользователь получает first-run onboarding.
- Send-flow проходит end-to-end.
- Archive/list state понятны в UI.
- Только после этого обновлён decision log.

# Частые ловушки

- Считать данные из backend автоматически используемыми во frontend.
- Путать отсутствие onboarding у старого пользователя с неисправностью first-run flow.
- Полагаться на старые логи после рестарта runtime.
- Считать один успешный build доказательством product readiness.
- Оставлять мелкие UX-артефакты на потом.

# Артефакты

Session-specific примеры и конкретные проверки держать в `references/`.
Для Hermes Web React 8792 см. `references/hermes-web-react-8792-acceptance.md`.
Для combined recurring/file UX см. `references/combined-recurring-file-acceptance.md`.
Для кейсов, где live UI продолжает показывать старый form-contract из persisted runtime-справочника, см. `references/runtime-reference-sync-and-live-form-verification.md`.
