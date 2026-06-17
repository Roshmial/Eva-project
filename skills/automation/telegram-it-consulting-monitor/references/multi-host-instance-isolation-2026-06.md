# Multi-host isolation for Telegram IT-consulting monitor

Контекст: один и тот же контур daily monitor был включён на двух серверах (`95` и `178`) при общей Telethon-session. Пользователь уточнил жёсткое правило: единственная точка пересечения между хостами — `session`; все артефакты выгрузки и digest должны быть раздельными.

## Что обязательно разводить по instance-id

Минимальный набор:

- `tg-since-id-it_consulting.json`
- `raw_logs/...`
- `raw_logs/reports/collect_*.json`
- `raw_logs/latest_collection_report.json`
- `archive/telegram_messages.jsonl`
- `latest_non_empty_for_summary.json`
- `latest_summary_input_path.txt`
- digest payload JSON
- processed CSV
- любые pointer-файлы latest-run

Практический шаблон:

- `TG-API/runtime/178/...`
- `TG-API/runtime/95/...`
- `~/.hermes/cache/documents/tg-it-consulting/178/...`
- `~/.hermes/cache/documents/tg-it-consulting/95/...`

## Рекомендуемый механизм

1. Вынести path-слой в отдельный модуль, который читает `TG_MONITOR_INSTANCE_ID`.
2. Если переменная не задана, допустим fallback на hostname, но для production-wrapper лучше задавать её явно.
3. Hermes cron wrapper на каждом сервере должен делать `os.environ.setdefault("TG_MONITOR_INSTANCE_ID", "178")` или соответствующее значение хоста.
4. Все runtime-пути строить через этот path-слой, а не хардкодить `TG-API/raw_logs`, `TG-API/archive`, общий `since.json` или общую cache-папку.

## Что проверять после изменения

1. Старые shared-path больше не обновляются.
2. Новый collector report появляется под `runtime/<instance-id>/raw_logs/reports/collect_*.json`.
3. Pointer latest report ведёт в тот же instance-specific контур.
4. Новый digest payload и CSV появляются в instance-specific cache-папке.
5. Новый cron output не содержит служебных блоков вместо клиентского результата.

## Cron-output hygiene

Если пользователь просит убрать технические записи cron, проверять именно фактические файлы:

- `~/.hermes/cron/output/<collector_job_id>/*.md`
- `~/.hermes/cron/output/<digest_job_id>/*.md`

Ожидаемый результат:

- collector/no-agent: только полезный stdout скрипта;
- digest/agent: только финальный текст для клиента;
- без `# Cron Job`, `## Prompt`, `## Response`, `Script Output` и похожей служебной разметки.

## Что не считать успехом

- В Telegram пришёл красивый digest, но `since.json` и `raw_logs` всё ещё общие.
- Новые output-файлы на одном хосте перетирают payload/CSV второго.
- Убрали техтекст только из сообщения пользователю, но оставили его в cron-output-файлах.
