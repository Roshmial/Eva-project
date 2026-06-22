---
name: dashboard-request-routing
description: Route, constrain, and verify dashboard requests in Hermes Web so explicit dashboard intents produce visual-first structured results without false triggers.
---

# When to use

Используй этот skill, когда пользователь просит:
- собрать дашборд;
- показать аналитику в dashboard-виде;
- отдать visual-first board по данным, рынку, каналам, периодам, срезам;
- перестроить ответ из plain text в структурированный dashboard.

Особенно нужен, если важно не путать:
- обычный research / сбор данных;
- generic chat;
- file export;
- recurring monitoring;
- dashboard delivery.

# Core routing rule

Dashboard path должен включаться только по явному dashboard intent или по продуктово допустимой форме, где пользователь действительно просит визуальную/структурированную board-подачу.

Само по себе наличие слов:
- "аналитика"
- "интернет"
- "Telegram"
- "разбор"

не должно автоматически переключать запрос в `dashboard_result`.

# Intent split

Разделяй 4 сценария:

1. `dashboard_request`
- пользователь явно просит dashboard / board / визуальную аналитику / панель / сводку в dashboard-формате.
- итог: structured dashboard payload.

2. `collection_then_dashboard`
- сначала нужно собрать/нормализовать данные,
- потом уже построить dashboard.
- итог: либо двухстадийный flow, либо честная clarification.

3. `research_only`
- пользователь просит исследование или подбор информации,
- но не просит visual dashboard explicitly.
- итог: не надо насильно включать dashboard route.

4. `monitoring_or_job`
- пользователь просит регулярное отслеживание/еженедельную сводку.
- итог: это не dashboard по умолчанию, а monitoring / job path.

# Source policy

По умолчанию для dashboard действует local-first логика:
- сначала attachment / local dataset / internal connector;
- потом, если policy разрешает и данных локально недостаточно, внешний web research.

Не обещай dashboard из локальных данных, если локального источника нет.
Не обещай внешний dashboard, если внешний источник policy не разрешает.

# Clarification contract

Если для dashboard недостаточно входных условий, нужно добрать минимум:
1. источник или набор данных;
2. период;
3. какие метрики и срезы нужны.

Если пользователь не знает источник, допустимо два честных пути:
- уточнить локальный источник;
- переключиться на внешний обзор по открытым источникам, если это разрешено policy.

# Delivery contract

Если запрос реально идёт в dashboard-result:
- ответ должен быть structured payload, а не длинный prose text;
- ключевые блоки должны быть видимыми сразу;
- без accordion / скрытых секций;
- при наличии количественной структуры нужен хотя бы один выраженный visual block.

Стабильный envelope:
- `kind`
- `title`
- `subtitle`
- `summary_cards`
- `sections`
- `sources`
- `notes`

# Section selection

Используй grammar-подход, а не один фиксированный шаблон.

Типовые блоки:
- `summary_cards`
- `pie_list`
- `bar_list`
- `bubble_list`
- `timeline_list`
- `matrix_list`
- `text_list`
- `post_list`

Приоритет:
- если есть доли/структура — `pie_list` / `donut-style` выше текста;
- если есть ranking/comparison — `bar_list`;
- если есть динамика — `timeline_list`;
- если есть факторный вклад — отдельный visual factor block.

# Anti-patterns

Не делать:
- false dashboard trigger по словам вроде `Telegram`, `аналитика`, `интернет`;
- text-heavy pseudo-dashboard без визуальной структуры;
- обещание dashboard, когда реально был только plain research answer;
- смешение dashboard intent и recurring monitoring intent.

# Verification checklist

Считать задачу закрытой только если подтверждено:
1. explicit dashboard intent действительно приводит к dashboard path;
2. generic research text без явного dashboard intent туда не уходит;
3. collection-route при необходимости имеет приоритет над dashboard-route;
4. output визуально структурирован, а не сваливается в prose;
5. dashboard policy по источникам соблюдена.

# Related skills

Этот skill — основной routing/delivery слой для dashboard scenario.

Используй вместе с:
- `adaptive-dashboard-grammar` — для section grammar и stable envelope;
- `dashboard-visual-selection` — для выбора и приоритизации visual blocks;
- `chat-runtime-reply-routing` — для общего route-split;
- `monitoring-request-routing` — чтобы не путать dashboard и recurring monitoring.

# Product truth

Dashboard — это не просто "ответ с таблицей" и не просто "аналитический текст".
Это отдельный контракт результата: visual-first structured board с явным routing, source policy и predictable payload shape.
