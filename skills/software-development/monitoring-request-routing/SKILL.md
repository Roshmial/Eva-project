---
name: monitoring-request-routing
description: Use when a loosely phrased user request should become a recurring monitoring workflow, not just an answer in chat.
version: 1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [monitoring, routing, recurring-jobs, cron, chat]
    related_skills: [scheduled-job-delivery-diagnostics, telegram-it-consulting-monitor, collection-proposal-routing]
---

# Monitoring request routing

## Overview

Этот skill нужен для класса запросов, где пользователь формулирует задачу неровно или разговорно, но по смыслу просит не разовый ответ, а регулярный мониторинг:
- еженедельный сбор новостей;
- ежедневный дайджест;
- отслеживание каналов, СМИ, блогов, тендеров, поставщиков, тем, конкурентов;
- периодический отчёт в заданном формате.

Главная цель: не терять такие запросы в generic chat-логике и не ограничиваться «ответила в чате», когда по смыслу нужен job / cron / monitor workflow.

## When to use

Использовать, когда запрос похож на:
- собирай каждую неделю / ежедневно / раз в месяц
- мониторь / отслеживай / присылай дайджест
- пусть приходит сводка
- поставь сбор информации
- смотри за каналами / СМИ / сайтами / блогами / тендерами
- хочу регулярную подборку

Особенно важно применять этот skill, если постановка дана неаккуратно и без формального шаблона.

## Core rule

Не считать мониторинг обычным chat-answer.

Для monitoring-класса phrase-rules и schedule-matching лучше держать в отдельном policy layer, а не в произвольных regex внутри backend-функций. Skill фиксирует смысл и guardrails, policy layer — конкретные trigger-маркеры.

Если пользователь просит периодическое наблюдение, нужно отдельно разделять:
1. intent на регулярность;
2. source scope;
3. deliverable format;
4. delivery target;
5. runtime vehicle:
   - Hermes cron/job;
   - существующий pipeline;
   - n8n execution contour, если пользователь уже перевёл workflow туда.

## Classification model

### Разовый запрос
Примеры:
- собери сейчас
- дай обзор на сегодня
- выгрузи в csv

Это one-shot collection / analysis task.

### Регулярный мониторинг
Примеры:
- каждую неделю собирай новости
- ежедневно присылай digest
- мониторь эти каналы
- поставь еженедельный сбор СМИ

Это recurring monitoring task.

## Mandatory extraction fields

Перед созданием recurring workflow нужно собрать или уточнить:
- cadence:
  - daily
  - weekly
  - monthly
  - custom schedule
- sources:
  - Telegram channels
  - СМИ / websites
  - blogs / RSS
  - tender platforms
  - mixed
- scope:
  - topic / company / market / region / keyword set
- output:
  - short digest
  - csv
  - markdown report
  - dashboard artifact
- delivery:
  - в этот чат
  - в job thread
  - в другой контур, если пользователь так попросил

## Routing rules

1. Если intent на регулярность явный — не закапывать запрос в обычный assistant answer.
2. Если cadence есть, но sources не заданы, вернуть clarification именно про scope/sources, а не уходить в generic discussion.
3. Если sources заданы и текущий stack уже умеет source-type, нужно идти в job/cron creation path.
4. Если в текущем user-message уже есть явная тема (`по теме LegalAI`, `по компании X`, `по тендерам Y`), subject нужно брать прямо из текущего запроса, а не из fallback-фразы вроде `отслеживай тему из текущего чата`.
5. Если пользователь даёт monitoring setup в два шага — сначала `давай поставим это как регулярный мониторинг`, потом отдельным коротким сообщением только cadence/time (`еженедельно по пятницам в 08:30`) — такой schedule-only follow-up нужно трактовать как продолжение monitoring intent из недавнего контекста, а не как generic chat.
6. Если источник требует отдельного collector pipeline, recurring job должен создавать/переиспользовать именно этот pipeline, а не вручную пересобираться в тексте ответа.
7. После перевода production workflow в n8n Hermes-версия должна оставаться только в dev/test и без активных рабочих расписаний.

## Anti-loss guard

Запросы типа:
- «поставь еженедельный сбор информации из СМИ»
- «мониторь эти каналы и присылай сводку»
- «сделай ежедневный мониторинг»

не должны завершаться только строкой `chat_tasks.status=completed`, если recurring job реально не создан.

Нужно отдельно подтверждать:
- request processed;
- job created;
- first run scheduled;
- delivery target resolved.

### Duplicate protection across chats

Если один и тот же пользователь повторяет по сути один и тот же recurring monitoring request в другом чате или новом thread, runtime не должен молча плодить второй активный job-клон.

Минимальный guard:
- сравнить `user_id`;
- сравнить normalized monitoring subject;
- сравнить cadence / schedule_kind / days_of_week / time_of_day / timezone;
- искать среди уже `active` / `paused` jobs того же monitoring type.

Если совпадение найдено:
- вернуть пользователю честный ответ, что задача уже существует;
- показать название и расписание существующего job;
- не создавать новый дубликат;
- предложить изменить расписание или scope, если нужен другой workflow.

## Minimal implementation contract

Для recurring monitoring backend/job layer должен уметь хранить:
- request class = monitoring
- schedule / cadence
- source manifest
- processing policy
- output contract
- delivery contract
- owner / recipients
- active runtime contour

## Verification checklist

- [ ] loosely phrased monitoring request определяется как recurring intent
- [ ] missing scope возвращает clarification именно про sources/schedule
- [ ] создан job / cron, а не только chat response
- [ ] есть подтверждённый schedule и delivery target
- [ ] job thread / runs / recipients проверяются отдельно от chat-task completion
- [ ] пользовательское сообщение не обещает готовую рассылку, если создан только job

## Common pitfalls

1. Считать, что completed chat-task = digest уже доставлен.
2. Терять monitoring intent из-за разговорной формулировки.
3. Смешивать one-shot collection и recurring monitoring в один маршрут.
4. Создавать повторный workflow рядом с уже существующим production pipeline.
5. Оставлять активными и Hermes, и n8n production schedules одновременно.

## Recommended companion skills

- `scheduled-job-delivery-diagnostics`
- `telegram-it-consulting-monitor`
- `collection-proposal-routing`
