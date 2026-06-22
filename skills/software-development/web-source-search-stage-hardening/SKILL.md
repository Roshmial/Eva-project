---
name: web-source-search-stage-hardening
description: Stabilize generic web collection when requests arrive without explicit URLs and the runtime must first discover sources via external search.
---

# When to use

Используй этот skill, когда пользователь просит:
- "собери информацию из источников в интернете ..."
- "найди по открытым источникам и выгрузи в csv/xlsx/json"
- "подбери источники по теме и сформируй файл"

и при этом в запросе нет явного списка URL.

Особенно актуально, если на runtime всплывают такие симптомы:
- `web_collection_sources_not_found`
- bot challenge от DuckDuckGo
- один плохой сайт (`403`, `404`, антибот, пустая страница) валит весь сбор
- generic web path работает технически, но source-list получается мусорным или слишком шумным

# Core rule

Generic web collection без URL — это двухступенчатый pipeline:
1. search stage: найти кандидатов-источники;
2. fetch/normalize stage: скачать, извлечь текст, превратить в rows/artifact.

Не смешивай эти два класса сбоев.

# Verification order

1. Проверь, что routing дошёл именно до `collection_execution_result` или хотя бы до web-collection executor.
2. Если source list пустой — проблема в search stage.
3. Если source list есть, но fetch падает — проблема в source fetch / anti-bot / site-specific accessibility.
4. Если fetch проходит, но rows пустые или мусорные — проблема в extraction / structuring / query relevance.

# Hardening rules

## 1. Предпочитать локальный Hermes search contour, а не один HTML-search provider

Если в контуре уже есть локальный Hermes CLI с toolset `web`, используй его как preferred search provider для generic web discovery.

Практический порядок:
- provider A: local Hermes CLI (`hermes chat ... -t web -Q`);
- provider B: HTML search fallback (DuckDuckGo/Bing или другой запасной parser).

Если primary provider отдаёт challenge/anti-bot или вообще не доступен по PATH/runtime env, нужен fallback search provider.

Минимально приемлемая схема:
- provider A -> если unavailable / bot challenge / empty results -> provider B.

## 2. Один плохой источник не должен валить весь сбор

Если из N найденных URL:
- часть скачалась успешно,
- часть вернула `403/404/timeout/blocked`,

то executor должен:
- продолжить по успешным источникам,
- сохранить `web_sources_skipped` с ошибками,
- честно отразить количество пропущенных источников в reply/meta.

Падать целиком допустимо только если не удалось обработать ни одного источника.

## 3. Source manifest обязателен

На generic web path сохраняй task-specific source manifest с:
- query,
- найденными URL,
- итоговыми URL после redirect,
- skipped/error sources,
- временем запуска.

Без source manifest невозможно разбирать качество поиска и повторяемость результата.

## 4. Relevance важнее формального успеха

Если pipeline технически завершился, но source list нерелевантен теме, это всё ещё product-quality issue.

Признаки низкой релевантности:
- unrelated domains,
- redirect-spam,
- сервисные/legal pages вместо предметных источников,
- повторяющиеся домены без содержательной ценности.

# Practical prod pattern

Реальный типовой сбой:
- DuckDuckGo HTML search начал отдавать human/bot challenge;
- routing был исправен, но search stage возвращал 0 candidates;
- после fallback search provider generic web path начал работать;
- затем вскрылся второй слой: `403 Forbidden` на части найденных сайтов;
- устойчивость достигалась только после partial-source tolerance.

# Acceptance standard

Не закрывай задачу, пока не подтверждено всё сразу:
1. generic web request без URL реально проходит route selection;
2. search stage не ломается от одного provider challenge;
3. хотя бы один частично успешный mixed-source кейс переживает `403`/blocked source;
4. пользователь получает реальный artifact attachment;
5. в meta есть `task_source_list`, а при частичном отказе — `web_sources_skipped`.

# When NOT to use

Не используй этот skill для:
- explicit URL collection, где источники уже заданы;
- Telegram channel collection;
- API source collection;
- attachment/file bundle collection.

Там другие failure domains.

# Recommended user-facing framing

Хорошо:
- "Сбор выполнился, но часть найденных сайтов оказалась недоступна; результат собран по доступным источникам, пропуски отмечены отдельно."
- "Проблема была не в маршрутизации, а в внешнем search stage / anti-bot ограничениях."

Плохо:
- "Ничего не получилось" — если часть источников была пригодна.
- "Всё готово" — если artifact есть, но source relevance явно мусорная и это не проговорено.
