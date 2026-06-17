# Non-blocking onboarding, mobile Jobs nav, and chat refresh

Когда пригодится:
- onboarding modal формально полезен, но пользователь жалуется, что вкладки/кнопки не нажимаются;
- на mobile исчезает важный раздел из навигации;
- чат отправляет сообщение, но новые ответы появляются только после ручного refresh.

## Симптомы

1. В desktop runtime кнопка `Задачи` визуально есть, но клик не доходит.
2. В mobile runtime `Задачи` вообще отсутствуют в nav.
3. После отправки сообщения pending bubble появляется, но реальный assistant reply не подтягивается сам.

## Форензика / как распознать

- Playwright/runtime evidence для desktop:
  - `locator('.nav-btn-jobs')` существует,
  - но click падает с перехватом pointer events от `.modal-backdrop-react`.
- CSS smell для mobile:
  - breakpoint-правило вида `.nav-btn-admin, .nav-btn-jobs { display: none; }`.
- Chat refresh smell:
  - UI умеет optimistic pending state,
  - но не делает `getThread(...)`/`getThreads(...)` после входа в чат или пока ответ ещё pending.

## Рабочий фикс

### 1. Onboarding overlay не должен блокировать app navigation

Надёжный паттерн:
- выделить onboarding в собственные классы, например:
  - `interaction-setup-backdrop`
  - `interaction-setup-modal`
- backdrop сделать неблокирующим:
  - `pointer-events: none`
- modal-контейнер оставить интерактивным:
  - `pointer-events: auto`
- при ручной навигации по разделам явно закрывать onboarding:
  - `setInteractionSetupOpen(false)` внутри `handleNavigate(...)`

### 2. Если mobile `Задачи` нужны — не скрывать их CSS-ом

Паттерн:
- скрывать только admin-nav,
- `jobs` оставлять видимым,
- mobile nav держать в 3 колонках (`Чаты`, `Профиль`, `Задачи`) при узком экране, если это часть пользовательского сценария.

### 3. Для chat delivery нужен базовый polling

Минимальный рабочий контур:
- `useEffect(...)` на `authenticated + screen === 'chat' + activeThreadId`
- немедленный `refreshChatState()` при входе в активный чат
- poll чаще, пока есть `assistant.meta.pending`
- poll реже в idle-режиме
- в refresh подтягивать минимум:
  - `getThreads()`
  - `getThread(activeThreadId)`
  - при pending-сценарии ещё и `getFiles()` если UI завязан на новых attachments/profile files

## Что проверять после фикса

1. Desktop:
- `Задачи` нажимаются даже если onboarding ещё виден.

2. Mobile:
- `Задачи` есть в nav,
- admin можно по-прежнему скрывать.

3. Chat:
- после отправки сообщения UI сам заменяет pending-состояние на реальный ответ,
- не требуется ручной refresh экрана.

## Связанные правки

- Для мобильных контейнеров удобно одновременно перевести основные layout-блоки на `100dvh`, чтобы chat/messages/composer не терялись из-за browser chrome.
- Если acceptance идёт через внешний Playwright/Chromium runtime на Linux без системных библиотек, полезно запускать браузер через проектный runtime-wrapper (`scripts/browser_runtime_env.sh`).
