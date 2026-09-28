# Structured message flow: clarification/approval через общий message path

Кейс: Hermes Web MVP React 8793, июнь 2026.

## Что оказалось важным

### 1. Не делать отдельный reply-endpoint по умолчанию
Для `clarification_request` полезнее было не добавлять новый backend route, а расширить существующий message contract.

Рабочая схема:
- backend reply содержит `message_kind`;
- для clarification добавляются `clarification_options` и лучше сразу `clarification_actions`;
- action хранит хотя бы `label`, `prompt`, `value`;
- frontend по кнопке отправляет `prompt` в обычный chat send flow.

Плюсы:
- reuse optimistic UI;
- reuse thread history model;
- без второго write-path для reply handling.

### 2. Статические labels недостаточны
Если backend отдаёт только список опций, фронт знает, что показать, но не знает, что именно безопасно отправлять назад.

Лучше сразу отдавать action objects:
- `kind: reply`
- `label`
- `prompt`
- `value`

### 3. Acceptance нужно строить как минимум в два шага
Недостаточно проверить, что в UI появился красивый artifact.

Нужен smoke на цепочку:
1. user message -> assistant `clarification_request`
2. follow-up по одному из action prompt -> assistant `dashboard_result` (или другой целевой message kind)

### 4. Для dashboard-result не угадывать shape payload
В этом кейсе smoke сначала проверял `dashboard.cards` и падал, хотя feature работала.
Правильный контракт оказался:
- `dashboard.summary_cards`
- `dashboard.sections`

Вывод: перед smoke-чеком лучше один раз посмотреть реальный ответ и опираться на его текущую форму, а не на догадку по имени поля.

### 5. Если browser-smoke сломан средой, разделяй functional и visual acceptance
В этом кейсе:
- backend smoke прошёл;
- `react:build` прошёл;
- live порты/endpoint'ы отвечали;
- Playwright smoke упёрся в native dependency (`libnspr4.so`).

Правильная формулировка результата:
- structured flow функционально подтверждён;
- визуальная headless-приёмка ограничена browser runtime среды.
