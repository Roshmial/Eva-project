# CopilotKit → chat-first integration notes

Когда пользователь просит убрать CopilotKit-артефакты из интерфейса и оставить только внутренний runtime-слой:

## Что делать
- Убрать из UI явные компоненты CopilotKit (`CopilotPopup`, preview/dev console, чужие термины).
- Сохранить provider/runtime wiring, если он уже рабочий.
- Перенести entrypoint в обычный Hermes chat screen.
- Стартовые действия давать как backend-driven operations, а не как frontend-only строки.

## Минимальный продуктовый паттерн
1. Backend хранит chat-first операции в reference data.
2. `/api/bootstrap` возвращает:
   - `starter_prompts` для обратной совместимости;
   - `starter_prompt_cards` с `key/title/description/prompt_text` для нового UI.
3. Frontend:
   - умеет читать `starter_prompt_cards`;
   - при отсутствии карточек откатывается к старому `starter_prompts`;
   - по клику подставляет в composer полноценный `prompt_text`, а не только label.

## Проверка
- Проверить живой `/api/bootstrap` после логина, а не только helper-функцию в backend.
- Если `cards=0`, но код уже содержит `starter_prompt_cards`, искать ручную сборку JSON в route.
- Если новый backend не виден по HTTP, проверить PID на порту и исключить stale process before restart.

## Практический набор первых операций
- Разобрать задачу
- Подготовить черновик
- Проанализировать файл
- Сравнить варианты
- Настроить регулярную задачу

## Почему это полезно
- сохраняет chat-first UX;
- не тащит в Hermes Web чужой popup-паттерн;
- оставляет CopilotKit как внутренний runtime, а не внешний продуктовый слой.
