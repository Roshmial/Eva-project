# Admin chat routing and non-executable promises (2026-06)

## Когда это всплывает

Используй при жалобах вида:
- `не могу забрать каналы`, хотя TG API вроде включен;
- `я приступаю`, `сейчас проверю`, `создам файл`, но дальше ничего реально не происходит;
- обычный текстовый запрос внезапно уходит в dashboard/analytics/connector flow.

## Подтверждённый live-паттерн

На prod `178.104.207.89:8791` было два разных дефекта, которые внешне выглядели как «ошибка генерации»:

1. Обычный текст с упоминаниями `Telegram`, `интернет`, `аналитика` ошибочно воспринимался как special analytics/dashboard intent.
2. Assistant публиковал operational promises (`Что я сделаю сейчас`, `Приступаю к проверке инфраструктуры`), хотя backend не запускал реальный action/file/dashboard path.

## Как различать быстро

### 1) Сначала отдели реальную недоступность API от ложного routing

Минимум проверь:
- `TELEGRAM_API_BASE_URL` в effective env runtime;
- `discover_connector_targets()` — есть ли `telegram_api` и `available=true`;
- слушает ли сервис нужный порт (`ss -ltnp | grep 8001` или аналогичный для текущего коннектора).

Если API/коннектор физически доступен, а запрос всё равно падает с `source_missing`/`analytics_source_missing`, подозревай не инфраструктуру, а ошибочную классификацию текста.

### 2) Потом подними сами `messages` и `chat_tasks`

Ищи:
- `assistant_message.content` с текстами обещаний (`приступаю`, `что я сделаю сейчас`);
- `assistant_message.meta_json.downstream`;
- `assistant_message.meta_json.message_kind`;
- следующий `chat_task.status` / `last_error`.

Ключевая интерпретация:
- если `downstream=hermes-api-server`, нет `message_kind=file_response/dashboard_result/...`, нет action-метаданных и нет отдельного job/action-run — это был обычный LLM reply, а не старт операции;
- если следующий ход пользователя (`Да, сделай`) потом уходит в `timed out`, проблема уже не в «первом обещании», а в отсутствии реального action-path для этого класса запросов.

## Минимальный фикс для этого класса проблем

### A. Routing

Обычные текстовые запросы не должны уходить в analytics/dashboard route только из-за слов:
- `Telegram`
- `интернет`
- `аналитика`

Нужен явный intent на:
- `дашборд`
- `dashboard`
- `сводка`
- `витрина`

### B. Финальный текст generic chat-ответа

Если backend не выполняет настоящий action-path, в postprocess нельзя оставлять:
- `Что я сделаю сейчас`
- `Проверю`
- `Создам`
- `Запущу`
- `Приступаю`

Практический guard:
- для generic chat-ответов вырезать такие operational promises;
- для реальных route (`file_response`, `dashboard_result`, `clarification_request`, `approval_request`, `generated_from_request`, `downstream=dashboard:*`) не трогать.

## Что проверять после фикса

1. Прямой вызов функции классификации:
- обычный текст про письмо с упоминаниями `Telegram/интернет/аналитика` -> `False` для dashboard intent.

2. Прямой вызов postprocess:
- ответ с `Что я сделаю сейчас` / `Приступаю` + generic `downstream=hermes-api-server` должен схлопнуться до нейтрального описательного текста без обещаний действия.

3. Live runtime:
- `api/health` зелёный;
- service после restart `active`;
- при необходимости — один model-backed probe, а не только health.

## Важная оговорка

Не делай вывод `TG API выключен` только потому, что assistant написал `не могу забрать каналы`.
Сначала проверь routing-classification и connector availability отдельно. В подтверждённом кейсе проблема была в логике маршрутизации и публикации текста, а не в недоступности самого Telegram API.
