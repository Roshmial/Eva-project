---
name: live-chat-rendering-debugging
description: Diagnose and fix live chat UI incidents where assistant messages render with stale text, duplicate surfaces, missing markdown, or recurring/job-delivery mismatches between backend payload and frontend bubbles.
---

# Когда использовать

Используй этот skill, когда в chat-first UI есть симптомы вроде:
- assistant message показывает reasoning/internal planning вместо пользовательского ответа;
- одно и то же сообщение отображается дважды разными способами;
- markdown приходит, но в UI выглядит как plain text;
- recurring/job-delivery результат выглядит иначе, чем обычный chat bubble;
- backend «вроде исправлен», но live UI всё ещё показывает старое или странное представление.

Это skill именно про last-mile debugging живого rendering path, а не только про локальный код.

## Главный принцип

Для live chat-rendering инцидентов всегда разделяй минимум четыре слоя:
1. сырое сохранённое `content`;
2. сохранённое `meta.display_text`;
3. финальный API serializer output, который реально уходит во frontend;
4. конкретную frontend render-ветку, которая решает: plain bubble, recurring-card, file-card, dashboard-card, clarification-card и т.д.

Не считай проблему "frontend-only" или "backend-only", пока не сравнил эти четыре слоя на одном и том же message id.

# Рабочий протокол

## 1. Зафиксируй affected message

Нужны:
- `thread_id`;
- `message_id`;
- точное пользовательское наблюдение: reasoning leak, duplicate render, missing markdown, wrong card type.

Если пользователь прислал скрин, трактуй его как evidence о живом UI, а не как второстепенную иллюстрацию.

## 2. Сравни три серверных представления сообщения

Для одного и того же message проверь:
- `content` в БД;
- `meta_json` / `meta.display_text`;
- `serialize_message(...)` output.

Типовые выводы:
- `content` плохой, а serializer хороший → проблема может быть уже только на frontend/runtime-state;
- `meta.display_text` stale, а `content` нормальный → нужен read-time sanitizer/normalizer;
- serializer уже хороший, но UI всё равно странный → ищи не в БД, а в render-path.

## 3. Для recurring/job-delivery отдельно проверь derived contract

Для recurring/job-delivery сообщений отдельно ответь на вопросы:
- хранится ли `recurring_summary` в сыром `meta_json` или достраивается только в serializer;
- используется ли одновременно обычный assistant `display_text` и derived `recurring_summary`;
- есть ли attachments, file-card, detail-preview, compact card или другой второй surface.

## 4. Для дублей recurring/job-delivery сначала проверь dual-render одного message

Если пользователь говорит "одно и то же сообщение показывается дважды", сначала проверь не только наличие двух записей в thread, но и более частый сценарий:
- в БД это один `job_delivery`/recurring message;
- во frontend он одновременно проходит через plain assistant text path и через recurring summary card.

Это особенно вероятно, если `recurring_summary` строится на лету в serializer, а frontend всё ещё имеет fallback на `display_text` или `meta.display_text`.

## 5. Для recurring/job-delivery устраняй дубль на двух слоях сразу

Если recurring message должен показываться только как специальная карточка, делай две защиты:

### Frontend
- suppress plain assistant text для любых messages с `meta.recurring_summary`;
- не ограничивай suppression условием `attachments.length > 0`, если продуктовая модель требует special-card и для text-only recurring results.

### Backend serializer
- если для assistant message построен `recurring_summary`, не отдавай параллельный обычный `display_text` как самостоятельный bubble source;
- очищай не только top-level `display_text`, но и `meta.display_text`, чтобы старые fallback paths не подхватили stale plain-text снова.

Это важный pitfall: если очистить только frontend или только top-level `display_text`, старый fallback всё равно может повторно нарисовать сообщение.

## 6. Для missing markdown не останавливайся на payload inspection

Если пользователь видит plain text вместо markdown:
- проверь exact `display_text`, который приходит с live backend;
- прогони этот exact text через тот же markdown parser/tokenizer, что использует frontend;
- отдельно проверь, не доходит ли до bubble другая строка, чем та, которую ты тестировал в backend.

Если parser на exact live text уже видит `table` / `heading` / `hr`, то корень уже не в markdown source и не в parser-синтаксисе, а в runtime render-path, client state или не том bundle.

### 6a. Если пользователь просит не трогать глобальный renderer — делай thread-scoped fix

Когда пользователь явно говорит в духе «реши только этот кейс, без глобальных настроек», сначала ищи узкий переключатель по message/thread contract:
- `meta.thread_title`;
- `message_kind` / `assistant_result_kind`;
- наличие конкретного derived surface (`recurring_summary`, file-result и т.д.);
- специфический shape payload (например, wide-table only).

Для markdown/table incidents это означает:
- не переводить все таблицы продукта на новый layout, если дефект локален одному чату;
- по возможности включать special render только для affected thread/class of messages;
- в отчёте явно отделять «локальный UX-fix» от «глобальной смены рендера», чтобы не создать видимость широкого product decision.

### 6b. Разделяй missing markdown и data-shape defect старых сообщений

Если live API уже отдаёт чистый `display_text`, а сырой `content` в БД остаётся загрязнённым reasoning/planning-текстом:
- не объявляй это "пропажей сообщения" или "чисто frontend-багом";
- фиксируй, что user-facing truth сейчас живёт в serializer output (`display_text`), а historical `content` — это отдельный data-shape/legacy defect;
- не начинай с ручной правки БД, пока не проверил, не достаточно ли уже serializer-contract для живого UI.

Это особенно важно для старых `job_delivery` / digest messages: сообщение может существовать и уже быть чистым в API, даже если его raw `content` по-прежнему выглядит как chain-of-thought blob.

## 7. Проверяй live bundle, а не только source tree

После frontend-фикса обязательно подтверди:
- какой `/assets/index-*.js` реально отдаёт live host;
- что нужный fix попал в свежий bundle;
- что соответствующий frontend service реально перезапущен.

После backend-фикса подтверди:
- рестарт нужного service;
- повторный live `serialize_message(...)` check для affected message.

## 8. Для acceptance закрывай инцидент только после message-specific verify

Минимум один live verify должен быть message-specific:
- affected `message_id` после рестарта;
- финальные поля, от которых зависит UI;
- краткий вывод: какой exact render-source теперь остался единственным.

Пример правильного критерия завершения:
- recurring message больше не имеет `display_text`/`meta.display_text`, а чистый user-facing digest остаётся только в `recurring_summary.summary/status_detail`.

# Частые pitfall'ы

- Проверить только БД `content` и решить, что UI тоже обязательно сломан так же.
- Проверить только serializer и решить, что живой frontend уже точно в порядке.
- Для recurring-case подавлять plain text только когда есть attachments.
- Очищать top-level `display_text`, но оставлять stale `meta.display_text`.
- Лечить duplicate digest как "два сообщения в thread", не проверив dual-render одного message.
- Диагностировать missing markdown только по screenshot без parser-check exact live text.

# Что сохранить в references

Сессионные детали клади в `references/`:
- affected message ids и thread ids;
- exact payload deltas до/после фикса;
- короткие reproduction notes по recurring duplication, stale `meta.display_text`, missing markdown.
- пример split-root-cause для локального markdown-fix vs legacy digest/body defect см. в `references/kpi-vs-tg-split-root-cause.md`.
