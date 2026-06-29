# Semantic Metric Mapping v3

Этот reference-файл описывает следующий слой над `semantic-metric-mapping-v1` и `v2` для dataset dashboards.

## Когда включать v3-слой

Включай этот слой, если данные уже распознаны как business-function dashboard и дополнительно выполняется хотя бы одно условие:
- есть `plan/fact`-поля, но отклонение важно не только по строкам, а и по группам (`department`, `category`, `team`, `vendor`, `period`);
- есть concentration/risk pattern, который нужно показать не только overall, но и по срезам;
- в одном наборе смешаны доли вида `0.42` и проценты вида `48`, и user-facing dashboard должен показывать их единообразно;
- structured payload пришёл не только из file export, но и из web/connector shape, и нужно честно отразить тип источника без возврата к source-centric identity.

## Правила v3

### 1. Grouping-aware plan/fact

Если найдены `plan` и `actual`, не ограничивайся только row-level matrix.

Добавляй второй слой:
- grouped `plan/fact` section;
- группируй по лучшей dimension из ряда:
  - `category`
  - `department`
  - `cost center`
  - `team`
  - `vendor`
  - `period`
- ранжируй группы по абсолютному отклонению `|actual - plan|`.

Цель этого слоя — показать, где отклонение накапливается системно, а не только в отдельных строках.

Хорошие user-facing названия:
- `Plan vs Actual по группам`
- `Отклонение от плана по группам`

### 2. Grouping-aware concentration

Если уже есть concentration logic (`top vendor`, `top channel`, `top team`, `top feature`), не останавливайся на overall-share card.

Добавляй grouped concentration section, когда есть вторая разумная dimension:
- `period -> channel concentration`
- `period -> team concentration`
- `category -> vendor concentration`
- `period -> feature concentration`

Смысл:
- overall concentration показывает общую зависимость;
- grouped concentration показывает, в каких срезах зависимость становится особенно опасной.

Хорошие user-facing названия:
- `Концентрация каналов по периодам`
- `Концентрация нагрузки по периодам`
- `Vendor concentration across slices`
- `Концентрация feature по периодам`

### 3. Нормализация смешанных долей и процентов

Не используй наивное правило `<= 1.0 -> *100` без проверки контекста набора.

Правильный подход:
- если почти весь набор в диапазоне `0..1`, трактуй как shares и переводи в проценты;
- если набор уже в диапазоне процентов (`5..100`), не пересчитывай;
- если в одном наборе есть и `0.42`, и `48`, нормализуй их к общей шкале процентов;
- округляй нормализованные значения, чтобы не тащить в payload хвосты floating point вроде `55.00000000000001`.

Это особенно важно для:
- `conversion`
- `retention`
- `coverage`
- `adoption`
- `uptime`
- `sla`

### 4. Source-shape bridging без source-centric identity

Если dataset path питается не только от файлов, но и от structured web/connector inputs, dashboard не должен снова становиться `dashboard по CSV` или `dashboard по web`.

Правильный паттерн:
- business function остаётся основным semantic identity;
- source shape показывается как context card / subtitle field;
- источник влияет на caveat и confidence, но не заменяет собой функциональный фокус.

Полезный минимальный словарь source shape:
- `file_export`
- `web_structured`
- `structured_source`

Хорошие user-facing элементы:
- card `Форма источника`
- subtitle вида `source shape: web_structured`

## Pitfalls

### Плохой паттерн: source снова становится главным именем dashboard

Неправильно:
- `CSV dashboard: Marketing`
- `Web dashboard: Procurement`

Правильно:
- `Дашборд бизнес-метрик: Маркетинг`
- `Дашборд бизнес-метрик: Закупки`
- плюс отдельный context/card про `source shape`.

### Плохой паттерн: overall concentration без slice-level follow-up

Если есть риск зависимости, overall-share card полезен, но часто недостаточен. Без grouped section пользователь не видит, где именно концентрация вспыхивает сильнее всего.

### Плохой паттерн: математически корректная, но UX-плохая нормализация

Даже если вычисление формально корректно, payload с неокруглёнными float-хвостами — плохой user-facing результат и плохая база для стабильных тестов.

## Минимальный verification checklist

- Для `plan/fact` есть и row-level, и grouped-level section, если grouping dimension доступна.
- Для concentration есть slice-level section, если доступна вторая dimension.
- Mixed share/percent values нормализуются в одну шкалу.
- В payload нет заметных floating-point хвостов.
- Source shape отражён как contextual layer, а не как новая dashboard identity.
