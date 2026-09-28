# Assistant markdown + reasoning digest regression (2026-06-25)

## Симптомы

- В чате `KPI` таблицы перестали рендериться как таблицы.
- В recurring / Telegram digest chat текст начал схлопываться в единый массив.
- В digest снова пролезал префикс вида `Примечание: включён глубокий reasoning-режим ...`.

## Что оказалось важным

1. Ошибка была не только в parser'е таблиц.
   - Слишком агрессивное отключение markdown-path для assistant messages ломает не только таблицы, но и переносы/абзацы в rich-text ответах.
   - Для Hermes Web assistant replies лучше считать markdown-capable по умолчанию, чем пытаться слишком рано выгнать их в plain text path.

2. При переходе на `marked`/token-based parsing нельзя бездумно брать paragraph content из `token.text`.
   - `token.text` может сглаживать исходные переносы строк.
   - Для digest/summary это приводит к потере визуальных абзацев и ощущению "всё пошло единым массивом".
   - Нужна отдельная проверка, не безопаснее ли рендерить paragraph/list из `token.raw` или эквивалентно близкого к исходнику поля.

3. Reasoning-note надо чистить в двух слоях.
   - Только frontend sanitation недостаточен.
   - Только backend `display_text` sanitation тоже недостаточен.
   - Нужны оба слоя: backend `display_text`/summary cleanup и frontend recurring fallback cleanup.

## Практический чек-лист

- После markdown-фикса проверить не только таблицы, но и обычные абзацы в recurring/digest сообщениях.
- Если жалоба звучит как "таблицы не рендерятся" и одновременно "всё схлопнулось", проверять нужно обе вещи:
  - markdown classification path
  - preservation of line breaks in token rendering
- При reasoning leakage смотреть:
  - `build_message_display_text(...)` / backend sanitation
  - frontend functions вроде `stripFrontendReasoningPrelude(...)`, `buildRecurringBodyText(...)`, `extractDigestBody(...)`

## Вывод

Для Hermes Web markdown regressions нельзя лечить только через table detector. Нужно отдельно держать в голове три независимых слоя:
- assistant markdown routing;
- token/block rendering with preserved line breaks;
- backend+frontend cleanup of reasoning/service prelude.
