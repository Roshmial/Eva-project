# Hermes Web React 8792 — acceptance lessons

Контекст сессии:
- Live-приёмка шла на `http://127.0.0.1:8792`.
- Ключевые хвосты: file open `404`, welcome/onboarding, runtime references в `Как отвечать`, micro-UX chat/profile.

Полезные конкретные уроки:
- Проверять `download_url` и frontend URL normalization: путь `/api/...` нельзя повторно префиксовать `API_BASE`, иначе получается `/api/api/...`.
- `bootstrap.references` может приходить не как массив, а как объект с `items`; helper options должен это поддерживать.
- Для first-run onboarding нужна проверка на реально пустом пользователе; отсутствие modal у текущего пользователя не является доказательством бага.
- Полезный финальный polish-пакет для chat/profile: warning separator, русский label вместо `Pinned`, явный статус `В архиве`, компактная action-группа `+ Новый чат / Все чаты`.
- Decision log обновлять только после полного live-pass по chat/profile contour.

Подтверждённый acceptance набор:
- new chat
- welcome card
- starter prompt
- send by Enter
- pending/final response
- archive/unarchive
- all chats modal
- profile response settings with runtime references
- onboarding auto-open for empty user
