# Hermes Web MVP: UI cleanup + local jobs migration checklist

Короткая session-specific заметка для cleanup pass, где UI и API переводятся с read-only jobs на локальный jobs engine.

Что менять вместе:
- frontend UI-контракт: навигация, кнопки, visible actions, тексты экранов;
- frontend logic: create/edit job, subscribe/unsubscribe, recipients, chat→cron draft;
- backend API-контракт: `/jobs/meta`, `/jobs`, `/jobs/<id>`, `/subscribe`, `/unsubscribe`, `/run`;
- smoke и acceptance scripts;
- backend smoke-tests.

Типовые регрессии:
- UI smoke ищет старый `.nav-btn[data-screen="profile"]`, хотя профиль уже вынесен в отдельную topbar-кнопку;
- backend smoke продолжает ждать `400` на create/update jobs после переключения на writable local-first contract;
- frontend показывает action-кнопки, но `row_to_job_dict()` не отдаёт `is_subscribed` или role-поля, нужные для реального состояния;
- `jobs/meta` использует несуществующие label/order константы вместо явного weekday-словаря;
- success-banner остаётся как ложный индикатор завершения, хотя нужен нейтральный info-state или тихое обновление интерфейса.

Минимальная проверка после cleanup:
1. syntax check frontend/backend;
2. backend smoke под новый writable contract;
3. UI smoke под новый navigation contract;
4. create job from jobs screen;
5. create cron draft from active chat;
6. subscribe/unsubscribe;
7. run job now;
8. admin health: messages + token usage + jobs.
