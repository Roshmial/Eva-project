# Semantic metric mapping v2

Добавочный semantic-слой поверх `dynamic explainable metrics` и `semantic metric mapping v1`.

## Когда применять

Использовать, когда dataset dashboard уже распознан как business-function analytics и в данных видны не только отдельные KPI-колонки, но и multi-column business constructs:
- funnel step chains;
- inflow/outflow/backlog patterns;
- concentration / dependency / risk patterns.

Этот слой нужен, чтобы не останавливаться на отдельных колонках и derived rates, а поднимать более осмысленные business structures.

## 1. Funnel step chains

### Идея

Если набор содержит несколько колонок, представляющих этапы потока, строй не только summary card по одному этапу, а цельную funnel section.

Примеры:
- sales: `lead -> qualified/MQL/SQL -> won`;
- marketing: `lead/signup/visitor -> MQL -> SQL -> won/customer`;
- hr: `applicant/candidate -> interview/screen -> offer -> hire/joined`;
- product: `signup/trial/visitor -> activated -> retained/repeat`.

### Что строить

Минимальный набор:
- summary card `Сквозная конверсия воронки`;
- отдельная section с суммарными объёмами по этапам.

### Практическое правило

Если найдено меньше двух осмысленных этапов — funnel не строить.
Если найдено 2+ этапа — считать totals по каждому этапу и строить funnel даже если dataset не идеален.

### User-facing naming

Предпочтительные названия:
- `Сквозная воронка продаж`
- `Маркетинговая воронка`
- `Hiring funnel`
- `Продуктовая воронка`

## 2. Inflow / outflow / backlog logic

### Идея

Для operations/support одного backlog недостаточно. Нужен смысловой слой: растёт ли система быстрее, чем успевает переваривать входящий поток.

Типовые пары:
- `created/opened/incoming` vs `completed/resolved/closed/done`;
- плюс `backlog`, если он доступен.

### Что строить

Полезные cards:
- `Inflow vs Outflow` — дельта между входящим и обработанным потоком;
- `Flow clearance rate` — какая доля входящего потока была обработана;
- `Pressure on backlog` — backlog как индикатор накопленной перегрузки, особенно если inflow > outflow.

### Интерпретация

- Если `inflow > outflow`, система накапливает хвост.
- Если clearance rate стабильно ниже 100%, backlog с высокой вероятностью будет расти.
- Если backlog уже высокий и inflow > outflow, это сильный сигнал operational pressure.

## 3. Concentration / dependency / risk patterns

### Идея

Если объём заметно сосредоточен в одной категории, это уже не просто breakdown, а управленческий риск / dependency.

Типовые оси:
- procurement: `vendor/supplier`;
- product: `feature/module`;
- marketing: `channel/source/campaign`;
- operations/support: `team/queue`;
- sales: `manager/owner`.

### Что строить

Минимальный набор:
- summary card, показывающая долю крупнейшей категории;
- top-share section по крупнейшим категориям.

### User-facing naming

Примеры:
- `Vendor concentration risk`
- `Концентрация по каналу`
- `Концентрация по feature`
- `Концентрация нагрузки`
- `Top vendors by spend share`

### Интерпретация

Высокая доля top-1 категории означает риск зависимости:
- от одного поставщика;
- от одного канала привлечения;
- от одного продуктового модуля;
- от одной команды/очереди.

## 4. Как встраивать v2 поверх v1

Правильный порядок:
1. business-function detection;
2. dynamic explainable metrics;
3. semantic v1 (`plan/fact`, ratios, ageing, cohorts);
4. semantic v2 (`funnel`, `flow pressure`, `concentration`).

Не подменять v1 новым слоем. V2 — это надстройка, а не замена.

## 5. Регрессионная проверка

Если вносится semantic v2:
- добавлять payload-level тесты минимум на 3 класса паттернов:
  - funnel;
  - inflow/outflow;
  - concentration.
- если `pytest` показывает `N passed`, но затем валится хвостовым teardown-abort, полезно отдельно прогнать тот же набор через прямой Python/unittest runner с принудительным выходом после результата, чтобы отделить correctness логики от бага окружения/teardown.

## 6. Pitfalls

- Не считать funnel из случайных числовых колонок без step semantics.
- Не называть любой category split словом `risk`: риск есть только там, где высокая концентрация реально означает dependency.
- Не терять explainability: даже semantic v2 cards должны объяснять, как читать метрику, а не просто показывать число.
- Не смешивать inflow/outflow semantics с generic backlog totals: backlog сам по себе не объясняет динамику системы.
