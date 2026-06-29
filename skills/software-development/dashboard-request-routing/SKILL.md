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

Критично: не хардкодь routing только под `web`.
Если dashboard строится поверх уже собранных материалов, опирайся на общий semantic path (`task_layers`, `analysis -> synthesis -> delivery`, provenance предыдущего ответа), а не на конкретный source-kind.

Для research-dashboard запросов уровня:
- `Проанализируй рынок ... и построй дашборд`
- `Собери дашборд по ...`

предпочтительный паттерн — отдельный policy guardrail, а не разрозненный Python-хардкод.
В policy-слое должны жить:
- implicit source для допустимых research-dashboard intent;
- allowlist intent-классов;
- short source-completion follow-up markers (`из интернета`, `по открытым источникам`, `с сайта`);
- флаг, нужны ли обязательные result fields для `dashboard`.

См. `references/research-dashboard-policy-guardrails.md`.

# Synthesis-first rule for analytical dashboards

Для исторических, эволюционных, исследовательских и narrative-heavy dashboard-запросов не пытайся строить итоговый dashboard напрямую из сырого collection output.

Правильный путь:
1. собрать или нормализовать материалы;
2. сделать содержательный synthesis;
3. только потом строить dashboard из synthesis.

Это особенно важно для сценариев вроде:
- история рынка / практик / технологий;
- эволюция инструментов;
- обзор по ранее собранной теме;
- dashboard, который должен рассказывать историю, а не просто перечислять источники.

Если route выдал только техническую сводку о сборе данных или fallback-секции, такой payload не должен считаться достаточным `dashboard_result`.

Критичный intent-split внутри synthesis:
- `history_evolution` может просить этапы, поворотные точки, смену практик и подходов;
- `market_overview` не должен автоматически уезжать в историю, методологию или `best practices`.

Для `market_overview` synthesis и fallback-dashboard должны быть ориентированы на:
- игроков и конкурентный контур;
- рыночные сигналы и сдвиги;
- продуктовые/ценовые акценты;
- ограничения и оговорки.

Если market/dashboard fallback показывает секции вроде `Смена практик и подходов`, это smell: скорее всего history-template протёк в market intent.

# Previous-answer transform path

Если пользователь просит короткий follow-up вида:
- `построй дашборд по этой теме`
- `на основе этого`
- `из этого`
- `по этому ответу`

и в треде уже есть содержательный assistant-ответ по теме, по умолчанию трактуй это как transform предыдущего ответа в dashboard, а не как новый внешний collection-run.

Практический смысл:
- previous substantive answer = source of truth;
- dashboard follow-up = операция преобразования формы ответа;
- новый внешний route нужен только если пользователь явно просит пересобрать материал или предыдущего содержательного ответа недостаточно.

# Route ordering pitfall

При добавлении previous-answer transform path не ломай соседние deterministic routes.

Безопасный приоритет:
1. transform dashboard follow-up по предыдущему содержательному ответу;
2. collection / contract route, если запрос реально про сбор данных;
3. export route, если это не collection и не transform;
4. generic dashboard route;
5. recurring / monitoring route.

Иначе легко сломать:
- file export (`csv`, `xlsx`, `pptx`, `docx`) из предыдущего ответа;
- collection-запросы, где формат файла указан прямо в пользовательском сообщении;
- short follow-up, который ошибочно уходит в generic dashboard или export path.

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
