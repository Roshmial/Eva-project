# Weekly QA reclassification artifacts — 2026-06

## Когда понадобилось

Пользователь попросил, чтобы weekly статистическая выгрузка по Telegram-дайджесту не только показывала число сообщений с типом `требует уточнения`, но и сразу формировала отдельную задачу на их переклассификацию.

## Устойчивый паттерн

Для weekly QA лучше делать два слоя результата:

1. Краткий QA summary:
- число запусков;
- число `no_new_messages`;
- число summary-файлов;
- среднее число непустых сообщений;
- `requires_review_total`;
- распределение типов.

2. Отдельные reclassification artifacts:
- `...requires_review_reclassification_<timestamp>.json`
- `...requires_review_reclassification_<timestamp>.csv`

Минимальные поля в reclassification-артефакте:
- `instance_id`
- `summary_input_path`
- `канал`
- `дата-время`
- `ссылка`
- `краткое содержание`
- `саммари`
- `альтернативный тип`
- `confidence`
- `исходный текст`

## Важный pitfall

Не строить reclassification-список из compact rows, которые возвращает `build_digest_payload()` для сохранения payload JSON.

Причина:
- compact payload rows могут не содержать `_raw_text`;
- в результате `исходный текст` в CSV/JSON окажется пустым;
- артефакт станет плохой основой для ручной или последующей агентной переклассификации.

Правильный путь:
- для reclassification-list отдельно повторно проходить исходный `summary_input` через `derive_rows(...)`;
- только так сохраняются `_raw_text`, `confidence`, `alternative_type` и другие поля полного classification-layer.

## Path hygiene

Reclassification artifacts должны писаться не в общий корень cache/documents, а в instance-specific путь:
- `~/.hermes/cache/documents/tg-it-consulting/<instance_id>/...`

Это важно, чтобы не смешивать weekly QA разных инстансов/хостов.

## Что полезно показать в самом weekly output

Если residue есть:
- отдельной строкой показать путь к CSV и JSON на переклассификацию.

Если residue нет:
- честно писать, что переклассификация не требуется.

## Практическая проверка после правки

После изменения weekly QA:
1. `python3 -m py_compile weekly_monitor_qa.py`
2. `python3 weekly_monitor_qa.py`
3. проверить, что weekly JSON содержит ссылки на reclassification CSV/JSON;
4. открыть CSV и убедиться, что поле `исходный текст` реально заполнено, а не пустое.
