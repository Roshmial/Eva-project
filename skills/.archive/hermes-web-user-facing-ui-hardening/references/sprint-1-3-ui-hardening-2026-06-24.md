# Hermes Web Sprint 1–3 UI hardening — 2026-06-24

## User-facing lessons

- Файлы диалога должны открываться как отдельная вкладка внутри чата по кнопке.
- Не надо делать thread files постоянным боковым блоком.
- Не надо прятать thread files в composer file picker как основное место доступа.
- В профиле раздел файлов должен означать все файлы пользователя по всем диалогам.

## Rendering lessons

- Text-only ответы не должны выглядеть как contract/status cards.
- Не выводить в default surface поля типа `Тип результата`, `Режим вывода`, `Причина`, `Доставка`, `Получатели`, если они не нужны пользователю.
- Не дублировать статус и в summary-card, и в bubble-meta.
- Если основной смысл уже в card, не оставлять пустой bubble-placeholder.

## Verification lessons

- `npm run react:build` обязателен, но недостаточен.
- Отдельно проверять, что live frontend реально отдаёт новый asset bundle.
- Полезный быстрый признак: проверить наличие новых строк-маркеров в `index-*.js` на live URL.
- Для files UX нужен backend regression на `GET /api/threads/<id>` и `thread_files` с обоими типами: user file и assistant result.
- Если Playwright/browser automation пришёл в blank/login/skeleton state, это не засчитывается как visual acceptance нужного экрана.

## Runtime diagnosis pattern

Когда UI кажется пустым после выкладки:
1. Проверить, отдают ли live URL новый bundle.
2. Проверить, живы ли `me / threads / files / bootstrap / jobs/meta`.
3. Отделить проблему renderer от проблемы auth/bootstrap choreography.
4. В отчёте явно писать, что подтверждено build/API-level, а что не подтверждено final visual acceptance.
