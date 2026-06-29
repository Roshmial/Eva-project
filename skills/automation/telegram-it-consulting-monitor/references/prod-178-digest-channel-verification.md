# Prod runtime/178 digest-channel verification

Когда использовать:
- пользователь говорит, что daily digest ограничен, показывает не все каналы или «раньше было больше источников»;
- нужно восстановить боевой список каналов и доказать, что он реально участвует в сборке.

## Канонический контур

- runtime: `178`
- profile pointer: `profile_178`
- config pointer: `daily_178`
- wrapper scripts:
  - `/home/hermes/.hermes/scripts/tg_it_collect_daily.py`
  - `/home/hermes/.hermes/scripts/tg_it_build_digest_context.py`

## Канонический набор каналов

1. `b1_news`
2. `Axenix_Ru`
3. `beringpro`
4. `Softline`
5. `k2_tech`
6. `Lanit_life`
7. `InnotechCompany`
8. `YakovPartners`
9. `delret`
10. `tedo_business`
11. `kept_business`
12. `Reksoft_group`
13. `norbit_ru`
14. `tadviser`

## Где должен быть закреплён список

Список должен быть синхронно закреплён в обоих файлах:
- `TG-API/channels_daily_178.yml`
- `TG-API/channels_178.yml`

Если правка сделана только в одном из них, prod-контур считается не доведённым.

## Минимальная последовательность live-проверки

1. Проверить указатели:
   - `.tg-monitor-config-name` → `daily_178`
   - `.tg-monitor-profile-name` → `profile_178`
2. Проверить оба YAML-файла на полный набор из 14 каналов.
3. Выполнить live collector:
   - `python3 /home/hermes/.hermes/scripts/tg_it_collect_daily.py`
4. Выполнить live digest-context build:
   - `python3 /home/hermes/.hermes/scripts/tg_it_build_digest_context.py`
5. Открыть `runtime/178/raw_logs/latest_collection_report.json` и найти строку `Запрос к API:`.
6. Подтвердить, что запрос реально идёт как:
   - `export?profile=profile_178&config=daily_178&since=...`
   - и содержит полный канонический набор каналов.

## Что считать достаточным доказательством

Недостаточно:
- «YAML выглядит правильно»;
- «раньше этот экспорт был полным»;
- «указатели вроде бы выставлены верно».

Достаточно:
- оба wrapper-скрипта завершились успешно;
- свежий `latest_collection_report.json` подтверждает live-запрос в `profile_178 + daily_178`;
- по `since`-карте видно, что полный боевой набор каналов действительно пошёл в сборщик.

## Соседний прод-урок из этой сессии

Если параллельно чинится Hermes Web backend и пользователь просит сделать всё под ключ, не завершай работу на конфиг-правке. Для реального закрытия задачи нужен живой прогон pipeline и проверка фактического output-контура, а не только кода или YAML.