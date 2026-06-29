# Dashboard runtime acceptance and language guards

Использовать для live-проверок Hermes Web dashboard-path, когда пользователь жалуется, что дашборд «никакой», уходит в английский, рисует synthetic charts или теряет тему follow-up.

## Что проверять сначала

1. Не считать проблему frontend-only по умолчанию.
   - Снять последний `dashboard_result` из thread/message storage.
   - Проверить `message_kind`, `dashboard_builder`, `downstream`, `dashboard_policy`, `sources`, `sections`, `summary_cards`.
   - Разделить: renderer/UI-баг vs плохой backend payload.

2. Для коротких follow-up вроде «А где сам дашборд?» проверять routing.
   - Если в треде уже был `dashboard_result`, follow-up не должен уходить как новый пустой dashboard request.
   - Нужно подтягивать предыдущий содержательный user request из того же thread.

3. Для исторических/эволюционных запросов проверять форму ответа.
   - Нормальный shape: `timeline_list` / `matrix_list` / фактологический `text_list`.
   - Подозрительный shape: generic market overview, adoption-by-size charts, usage share pie charts, не связанные с историей темы.

## Жёсткие anti-bullshit guards для dashboard-path

Если запрос на русском, acceptance должен проваливаться при любом из признаков:
- `reply_text`, `title`, `subtitle`, `notes` или секции ушли в английский без явной просьбы пользователя.
- В chart-like секциях встречаются маркеры `illustrative`, `placeholder`, `indicative`, `estimate`, `not retrieved`.
- Есть `bar_list` / `pie_list` с synthetic числами или выдуманными долями «для красоты графика».
- Тема сместилась: пользователь просил историю/эволюцию, а backend вернул общий overview по BI или рынку.

## Полезный runtime-приём

Если нужно быстро проверить backend-guardrails без полного user rerun:
- поднять live backend в штатном env (`source scripts/runtime_env.sh`, не голый waitress);
- временно подменить `call_hermes_messages` bad payload'ом;
- прогнать `build_global_dashboard_reply(...)` на реальном русском historical request;
- проверить, что результат очищается до русского safe fallback без fake charts.

Это удобно для подтверждения post-validation логики, когда реальный LLM-ответ нестабилен.

## Коммуникационный pitfall

Не вываливать пользователю сырой JSON, полный API response или профиль пользователя из live runtime.
Даже если это «всего лишь подтверждение логина/меты», в пользовательский ответ должен идти короткий вывод по сути:
- что проверено;
- что сломано / исправлено;
- что делать дальше.

## Live-операционный pitfall

Backend на live-контуре Hermes Web нужно перезапускать штатным bootstrap-скриптом (`run_backend_service.sh` или эквивалентным service path), а не голым `waitress-serve`.
Иначе можно случайно поднять backend в неправильном runtime-mode и начать проверять не тот контур.
