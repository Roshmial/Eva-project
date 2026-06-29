---
name: internal-ai-product-core-definition
description: Формирует Product Core Definition и roadmap для внутреннего AI-продукта, особенно когда в компании уже есть общий LLM-чат и нужна отстройка через recurring workflows, files, artifacts и handoff.
user_locked: true
priority: 85
tags:
  - product-strategy
  - hermes
  - internal-platform
  - roadmap
  - consulting
version: 1
---

# Skill: internal-ai-product-core-definition

## Назначение

Используй этот навык, когда нужно определить, переписать или ужесточить продуктовую рамку внутреннего AI-продукта:
- Product Core Definition;
- product narrative;
- differentiators;
- product priorities;
- supported / guarded / non-core scenarios;
- roadmap верхнего уровня.

Особенно важен этот навык, если в компании уже существует общий LLM-чат и новый продукт нельзя позиционировать как ещё один «универсальный AI-чат».

## Когда активировать

Активируй, если пользователь просит:
- сформировать product concept / product core / roadmap;
- понять, как отстроиться от уже внедрённого LLM-чата;
- превратить набор AI-capabilities в внутренний продукт;
- определить, что уже можно внедрять, а что пока рано;
- увязать recurring automation, assistant layer, files и integrations в одну продуктовую рамку.

## Главный принцип

Не начинать с UX-полировки и не конкурировать с корпоративным LLM-чатом на его поле.

Сначала определить:
1. где продукт даёт отдельную ценность;
2. какие сущности у него first-class;
3. какие сценарии являются ядром;
4. как он деградирует на нестандартных запросах;
5. как он встраивается в рабочий и интеграционный контур компании.

## Базовый способ мышления

Рассматривай внутренний AI-продукт как сочетание 4 слоёв:
1. recurring / monitoring / execution layer;
2. assistant layer;
3. file / artifact layer;
4. admin / policy / operational layer.

Dashboards рассматривать как производный слой, если только пользователь явно не ставит visual analytics в центр.

Workflow layer обычно не должен быть первым приоритетом: его строят поверх уже стабилизированного core.

## Обязательная структура Product Core Definition

Документ должен как минимум содержать:
- зачем нужен продукт;
- отстройку от существующего LLM-чата;
- продуктовую цель;
- приоритеты по слоям;
- целевые пользовательские группы;
- core entities;
- supported scenarios;
- guarded scenarios;
- non-core scenarios;
- критерии зрелости;
- главные риски;
- дальнейшие шаги / roadmap.

## Как формировать приоритеты

Проверь, не требует ли ситуация сместить фокус с «чата» на более сильные differentiators:
- recurring jobs;
- cron;
- monitoring;
- file processing / generation;
- artifacts;
- handoff;
- operational governance.

Если пользователь уже сообщил явную продуктовую очередность, зафиксируй её как главную ось документа, а не как второстепенную заметку.

## Как оформлять сущности

Принудительно разводи роли сущностей:
- chat — обсуждение, постановка задачи, уточнения;
- file — входной или сгенерированный материал;
- artifact — самостоятельный результат работы;
- job — повторяемый процесс;
- run — конкретное исполнение job;
- handoff — передача в дальнейший рабочий контур;
- policy/admin — правила, наблюдаемость, управление.

Если эти сущности не разведены, продукт будет ощущаться как каша, даже если функции уже реализованы.

## Как оценивать roadmap

Разделяй roadmap на 3 состояния:
- уже можно использовать;
- готово к пилоту / полу-ручному внедрению;
- пока рано считать зрелым.

Не смешивай наличие capability с наличием продуктового path.
Пример:
- «можно руками собрать КП в чате» — это capability;
- «есть устойчивый контур формирования КП как продуктовый сценарий» — это уже product path.

## Работа с нестандартными сценариями

Для не прибитых к полу сценариев не обещай полную универсальность.
Нужно явно проектировать managed degradation:
- constrained execution;
- guided clarification;
- fallback;
- handoff в другой контур.

## Что считать сильным сигналом зрелости

Положительные сигналы:
- recurring jobs реально живут в проде;
- есть monitoring / audit / review workflows;
- есть file reuse и generated artifacts;
- есть admin / policy / events / health;
- есть split между supported и non-core.

Отрицательные сигналы:
- продукт описывается только через чат;
- сущности смешаны;
- roadmap уходит в dashboards раньше recurring core;
- нестандартные сценарии скрыто трактуются как «ну оно как-то само должно справиться».

## Выходные артефакты

Обычно нужно подготовить один или несколько артефактов:
- `PRODUCT_CORE_DEFINITION_V1.md`;
- product memo / concept note;
- product contract / acceptance matrix;
- prioritized roadmap;
- список: уже готово / готово к пилоту / пока в разработку.

## Для Миши

Если работа идёт по Hermes как внутреннему продукту, по умолчанию:
- не пытайся позиционировать его как просто «лучший AI-чат»;
- first focus — recurring / monitoring / operational usefulness;
- assistant layer вторичен, но важен;
- files — отдельный продуктовый контур, а не просто attachments;
- dashboards — позже, если не доказана более сильная прикладная польза.

Смотри также:
- `references/hermes-product-priority-stack.md`
- возможны пересечения с навыком `consulting:multi-user-agent-platform-design`; куратору стоит при случае проверить overlap.
