# Chat routing and timeout pitfalls in Hermes Web MVP

Используй эту заметку при live-отладке Hermes Web чатов, где пользователь жалуется на странные обещания действия, ложные ошибки про файл или непонятные Telegram/dashboard сбои.

## 1. Сначала отдели generic chat path от special routes

Проверь у проблемного `chat_task`:
- `request_policy_json`
- `last_error`
- финальный assistant message

Практическая интерпретация:
- если `request_policy_json` почти пустой (`explicit_source_ids=[]`, `connector_targets={}` и т.п.), это сильный сигнал, что turn прошёл через обычный generic chat path;
- если `last_error = timed out` при пустом `request_policy_json`, не прыгай сразу к версии про поломанный connector или недостающий action-route;
- сначала проверь, не был ли это короткий follow-up после длинного assistant-ответа, который ушёл в слишком тяжёлый full-history LLM path.

## 2. Короткие follow-up подтверждения требуют отдельной проверки

Опасный шаблон:
- assistant дал длинный план/объяснение;
- пользователь отвечает коротко: `Да, сделай`, `давай`, `запускай`;
- turn уходит в generic path и ловит timeout.

Рабочая диагностическая гипотеза:
- проблема не обязательно в отсутствии отдельного action-route;
- сначала проверь, нужен ли focused follow-up context вместо полного history path.

## 3. Не путай generic timeout с file-generation failure

Публичная ошибка вида `Не удалось сформировать файл...` допустима только если действительно шёл file/export/generated-file path.

Если файл реально не генерировался, то generic `timed out` должен оставаться generic timeout-ошибкой. Иначе:
- дебаг уходит в неправильную ветку;
- создаётся ложное впечатление, что сломан export/file flow;
- теряется время на проверку не того контура.

## 4. Не маршрутизируй обычный текст в analytics/dashboard только по словам

Слова `Telegram`, `интернет`, `аналитика` сами по себе не означают dashboard/analytics intent.

Для special analytics route нужен явный intent на:
- дашборд;
- сводку/витрину;
- structured analytics output.

Иначе обычные admin-сообщения могут ошибочно выглядеть как проблемы `telegram_analytics_source_missing`, хотя сам Telegram API живой.

## 5. Практический порядок live-диагностики

1. Подними `messages` и `chat_tasks` по конкретному thread.
2. Проверь `request_policy_json` проблемного task.
3. Проверь `last_error` без интерпретации по UI-тексту.
4. Отдели generic path от export/dashboard/recurring-job path.
5. Только после этого решай, нужен ли новый structured route или достаточно поправить routing/context/error normalization.

## Когда это особенно полезно

- admin chat на Hermes Web;
- короткие подтверждения после длинных assistant-ответов;
- жалобы вида `сказал, что делает, но ничего не произошло`;
- ложные file-errors после обычных chat-turn;
- ложные Telegram/dashboard-ветки при обычном текстовом запросе.