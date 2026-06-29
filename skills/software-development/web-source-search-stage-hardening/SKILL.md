---
name: web-source-search-stage-hardening
description: Stabilize generic web collection when requests arrive without explicit URLs and the runtime must first discover sources via external search.
---

## Session-learned hardening patterns

- Treat web collection as a staged degrade path, not a binary success/fail pipeline. If search/discovery is flaky but some candidate URLs were already found, continue with partial source sets instead of failing early with a generic `documents_unavailable` / `web_search_stage_failed` outcome.
- Add an explicit second fetch attempt for 401/403-style responses using more browser-like headers before giving up on a source. Capture the lesson as a retry pattern, not as a permanent claim that a domain is blocked.
- Relevance filtering after fetch should have a soft-fallback mode. If topic matching is directionally correct but exact subject overlap is weak, keep a small set of best documents instead of collapsing the entire collection to zero documents.
- Keep multiple HTML search fallbacks in the discovery layer. Do not rely on only one or two providers when the class of failure is provider-specific throttling or markup drift.
- For user-facing behavior, prefer an honest partial-result response (`часть источников недоступна, результат собран по доступным`) over an early hard fail when at least part of the collection path succeeded.

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
- provider B: HTML search fallback (DuckDuckGo/Bing);
- provider C: ещё один независимый HTML fallback (например Startpage), если первые два дали challenge / empty results / provider-specific blockage.

Если primary provider отдаёт challenge/anti-bot или вообще не доступен по PATH/runtime env, нужен fallback search provider.

Минимально приемлемая схема:
- provider A -> если unavailable / bot challenge / empty results -> provider B -> provider C.

Важно: не считай `DDG empty` или `Bing blocked` доказательством, что у runtime в целом нет внешнего доступа. Это может быть только provider-level failure search stage.

## 2. Один плохой источник не должен валить весь сбор

Если из N найденных URL:
- часть скачалась успешно,
- часть вернула `401/403/404/timeout/blocked`,

то executor должен:
- продолжить по успешным источникам,
- сохранить `web_sources_skipped` с ошибками,
- честно отразить количество пропущенных источников в reply/meta.

Падать целиком допустимо только если не удалось обработать ни одного источника.

Практический hardening на fetch-stage:
- делай хотя бы одну повторную попытку для `401/403` с более browser-like заголовками (`Accept-Language`, более обычный `User-Agent`, `Cache-Control`/`Pragma`), прежде чем окончательно помечать источник как недоступный;
- сохраняй итог как partial success, если после повторных попыток хотя бы часть источников осталась читаемой.

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

Но обратная ошибка тоже опасна: не делай relevance-gate настолько жёстким, чтобы он выбрасывал все документы с мягким, но предметно полезным совпадением.

Практическое правило:
- сначала отбирай документы с явными subject hits и хорошим score;
- затем допускай soft-match слой: тематически близкие title/text с умеренным score и без признаков low-value pages;
- только после этого объявляй `documents_irrelevant`.

Если хотя бы несколько документов содержательно подходят теме, лучше вернуть partial / weaker synthesis, чем сваливаться в пустой отказ из-за переужесточённого relevance filter.

# Practical prod pattern

Реальный типовой сбой:
- DuckDuckGo HTML search начал отдавать human/bot challenge;
- routing был исправен, но search stage возвращал 0 candidates;
- после fallback search provider generic web path начал работать;
- затем вскрылся второй слой: `403 Forbidden` на части найденных сайтов;
- устойчивость достигалась только после partial-source tolerance.

Ещё один полезный паттерн из live-prod:
- внешний доступ с runtime может быть частично живым (`Google News 200`), даже если часть целевых сайтов отвечает `401/403/503`;
- generic chat path в этот момент легко ошибочно описать как `browse сломан` или `внешки нет`;
- правильная классификация — partial source reachability + anti-bot friction, а не total egress outage.

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
- "Внешний доступ есть не ко всем источникам одинаково: часть сайтов открылась, часть режет automation; итог собран по доступным материалам."

Плохо:
- "Ничего не получилось" — если часть источников была пригодна.
- "Всё готово" — если artifact есть, но source relevance явно мусорная и это не проговорено.
- "browse не работает / у сервера нет внешки" — если у тебя есть хотя бы один успешный outbound probe и проблема ограничена частью источников или search providers.

# References

See `references/partial-egress-and-search-fallbacks.md` for a concrete live pattern: `run now` debugging surfaced that outbound access was partial rather than absent, and web collection became more stable only after adding search-provider redundancy, browser-like 401/403 retries, and softer post-fetch relevance fallback.
