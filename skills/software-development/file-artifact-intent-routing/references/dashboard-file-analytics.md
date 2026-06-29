# Dashboard file analytics routing notes

Когда пользователь прикладывает табличный файл и просит dashboard/analysis, полезно разделять два уровня:

1. Generic dataset overview
- row count
- column count
- numeric vs categorical columns
- top categorical values
- sample rows

2. Business-oriented dataset analytics
- CRM / funnel
- sales / revenue
- breakdown by manager / channel / stage
- period dynamics
- concise findings

## Practical routing heuristics

### Intent from request text
Признаки `crm_funnel`:
- crm
- лид / lead
- воронка / funnel
- pipeline
- конверсия / conversion

Признаки `sales_performance`:
- продажи / sales
- revenue / выручка
- сделки
- за месяц / по месяцам

### Useful inferred column roles
Даже без явной схемы часто можно искать роли по названиям колонок:
- amount: amount, sum, revenue, price, value, выручка, сумма, чек, budget
- stage: stage, status, этап, pipeline, воронка
- manager: manager, owner, sales, менеджер, ответственный
- channel: channel, source, utm, канал, источник, campaign
- date: date, created, closed, month, day, дата, период, месяц

## Preferred sections for numeric business files
Если роли определены, лучше строить не schema-only блоки, а предметные:
- metric profile: сумма / среднее / максимум
- funnel by stage
- amount by stage
- amount by manager
- channel mix
- period timeline
- short conclusions

## Local-first implementation note
Если в runtime нет `pandas/openpyxl`, это не повод отказываться от простого `.xlsx` dashboard path. Для первого листа и базовых табличных кейсов достаточно lightweight reader через ZIP/XML OOXML parsing. Добавлять тяжёлые зависимости стоит только если реально нужны формулы, сложные типы, мультилистовая логика или полноценная spreadsheet-совместимость.

## Verification
- Файл действительно читается как dataset, а не только как attachment metadata.
- Request text влияет на тип аналитики.
- Numeric CRM/sales files дают business-oriented sections, а не только `строк/колонок/типы`.
- При слабой схеме есть fallback в generic dataset overview, а не ложная предметная аналитика.
