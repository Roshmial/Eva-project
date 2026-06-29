---
name: collection-proposal-routing
description: Use when designing or debugging local-first routing for requests of the form 'collect data from source X and return file / proposal / estimate artifact' without false triggers.
version: 1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [routing, collection, proposal, artifact, local-first]
    related_skills: [artifact-delivery-contract-hardening, scheduled-job-delivery-diagnostics, turnkey-local-first-mvp-delivery]
---

# Collection proposal routing

## Overview

Этот skill фиксирует устойчивый паттерн для запросов класса:
- собрать данные из web / Telegram / files / API;
- обработать данные;
- вернуть artifact;
- при явном intent дополнительно собрать проект КП / оценку стоимости / ресурсный план.

Он нужен не как отдельный исполнитель вместо backend, а как слой правил поверх backend-routing: что должно считаться обычным data-collection, что должно считаться proposal-composition, и как это проверять без ложных срабатываний.

## When to use

Использовать, когда нужно:
- проектировать universal `source -> processing -> artifact` contour;
- исключать ситуации, где один запрос случайно идёт сразу в несколько веток;
- отлаживать false-positive на `КП`, `стоимость`, `ресурсы`;
- проверять, что generic web / attachments / API не висят в вакууме, а проходят до реального файла;
- доводить request-класс `подготовь КП / оцени стоимость / оцени ресурсы` до отдельного composition artifact.

Не использовать как замену runtime-логике. Если нужна реальная обработка запроса, она должна жить в backend executor-ах.

## Core routing model

### 1. Source-kind
Сначала определить source-kind:
- web / open internet
- telegram
- attachment / attachments
- api
- tenders
- mixed

### 2. Deliverable-kind
Потом определить deliverable-kind:
- dataset/file
- proposal_draft
- proposal_bundle
- cost_estimate
- resource_estimate
- estimate_bundle

### 3. Intent guard
Proposal/composition включать только по explicit intent.

Хорошие trigger-примеры:
- подготовь КП
- сформируй проект КП
- подготовь коммерческое предложение
- оцени стоимость
- оцени ресурсы

Плохие trigger-примеры:
- собери в csv по теме проект КП
- собери аналоги КП в таблицу
- выгрузи прошлые КП в файл

Само по себе упоминание `КП` в теме, имени файла или поле dataset не должно включать proposal-layer.

## Recommended execution order

1. source detection
2. contract extraction
3. route lock
4. source materialization
5. collection execution
6. optional composition execution
7. artifact generation
8. attachment serialization

## Route lock

Для одного user-request должна срабатывать одна основная ветка.

Рекомендуемый приоритет:
- collection_execution
- collection_contract / clarification
- message_export
- dashboard
- recurring_job
- generic_chat

Важная оговорка: этот порядок не должен применяться механически. Если в запросе уже есть явный recurring monitoring intent с cadence/schedule, `recurring_job` должен подниматься выше `collection_contract / clarification`, иначе runtime создаёт ложный product-bug: пользователь просил регулярную задачу, а backend отвечает как будто речь только о one-shot сборе.

## Contract fields

Минимальный collection-contract должен уметь хранить:
- `source_kind`
- `source_items` или task-specific source manifest
- `subject`
- `output_format`
- `fields`
- `since_date` при необходимости
- `composition_mode` для proposal-ветки
- `analysis_modes` (`classification`, `selection`, `comparison`, `analyze` и т.п.)
- `task_layers`:
  - `root_class` (`data_pipeline`)
  - `stages` (`acquisition`, `analysis`, `delivery`)
  - `deliverable_kind` (`dataset` / `document`)
  - `cadence` (`once` / `recurring`)
- `budget_hint`
- `timeline_hint`
- `team_constraints`
- `request_text`

Практическое правило по trigger-ам:
- wording вроде «настрой выгрузку», «организуй выгрузку», «подготовь выгрузку» нужно считать валидным collection-intent, если в том же сообщении уже есть dataset target, source class и явный формат результата;
- bare mentions `csv/xlsx/json/xml` внутри collection-запроса надо уметь трактовать как `output_format`, даже если пользователь не писал отдельную file-export фразу вроде «отдай файлом»;
- subject extraction для формулировок `по теме X в csv/json/xlsx/...` должна останавливаться до format marker, чтобы тема не превращалась в `X в csv`.

Идея простая: skill помогает думать и маршрутизировать, а backend должен исполнять уже собранный контракт, а не угадывать смысл заново на каждом шаге.

## Proposal composition rules

Если intent явный, composition-layer должен:
- использовать уже собранные documents / rows, а не запускать параллельный несогласованный контур;
- разделять confirmed facts, analogs, hypotheses;
- отдельно показывать workstreams, cost notes, resource plan, risks, open questions;
- учитывать hints из запроса:
  - budget_hint
  - timeline_hint
  - team_constraints

## Artifact rules

Обычный collection-request:
- dataset artifact: csv/json/xlsx/xml/md/txt по контракту.

Явный proposal/composition request:
- composition artifact, по умолчанию markdown (`md`), если пользователь явно не потребовал другой стабильный итоговый формат.
- если нужен и dataset, и proposal, допустимо вернуть оба attachment-а, но composition artifact должен быть основным итогом.

## Skills vs backend

Правильная схема здесь гибридная:
- backend = движок исполнения и маршрутизации;
- skill = декларативные правила, guard-ы, checklist, verification pattern.
- policy layer = data-driven routing rules, которые backend подгружает из отдельного policy-file, а не держит как россыпь phrase-level regex по функциям.

Не надо переносить фактический executor целиком в skill, иначе получится вторая, дублирующая логика.

## Policy integration

Для production-grade контура collection/proposal phrase-rules должны жить не только в тексте skill и не только в Python-коде.

Нормальный паттерн:
1. skill фиксирует поведение и guardrails;
2. policy-file хранит trigger/extraction rules;
3. backend исполняет уже выбранный путь.

Если надо поддержать новый phrasing без изменения execution semantics, сначала менять policy layer, а не плодить новый backend `elif`.

Смотри также skill `chat-request-routing-policy`.

## Common failure patterns

1. Request completed only as a contract
Пользователь просил собрать данные и отдать файл, а система остановилась на contract/plan.

2. False proposal trigger
Слово `КП` встретилось в теме, и обычный dataset-path ошибочно превратился в proposal-path.

3. Generic web blocked by missing URLs
Пользователь явно просит сбор из интернета, но система возвращает искусственный blocker `нужен список URL`, хотя search-stage уже допустим.

4. Sources found, documents unavailable
Search/discovery уже нашёл релевантные ссылки, но downloader/fetch-stage не смог вытащить тексты. В таком случае не надо возвращать голый `web_collection_documents_unavailable`, если runtime уже может отдать полезный partial artifact со списком найденных источников.

Практический fallback:
- serialise найденные URLs/titles в реальный artifact;
- честно отметить, что документы недоступны, но source list собран;
- если requested format = `xlsx`, а xlsx runtime недоступен, degrade to `csv`, а не падать вторичным runtime-error.

5. Collection competes with dashboard/job routing
Один и тот же запрос одновременно начинает трактоваться как сбор, дашборд и recurring job.

## Verification checklist

- [ ] ordinary collection request с упоминанием `КП` в теме остаётся dataset-path
- [ ] explicit `подготовь КП` создаёт composition artifact
- [ ] generic web request без URL идёт через search manifest
- [ ] attachments-path реально строит artifact из extracted text
- [ ] API-path реально строит artifact из explicit endpoint
- [ ] composition artifact содержит budget/timeline/team hints, если они были в запросе
- [ ] route priority подтверждён тестами
- [ ] prod restart выполнен через canonical runtime env
- [ ] health-check после рестарта стабилен, без зависания
- [ ] новый `chat_task` уходит из `pending` без ручного дожима, `started_at` заполняется, а immediate-dispatch не стартует worker без атомарного claim `pending -> running`
- [ ] dashboard execution имеет backend fallback payload и заканчивается `dashboard_result`, даже если модель вернула слабую или частичную структуру
- [ ] тяжёлый Telegram/channel export проверен отдельно: либо проходит в разумное время с консервативными лимитами, либо честно переведён в async contract вместо псевдо-синхронного chat-task
- [ ] если Telegram collector вызывает внешний однопоточный TG API, backend делает singleflight-сериализацию export-вызовов и не шлёт параллельные `/export` во время активной выгрузки

References:
- `references/runtime-remediation-chat-tasks-dashboard-telegram-2026-06-20.md`
- `references/telegram-singleflight-runtime-notes.md`
- `references/prod-bugfix-routing-notes-2026-06-24.md`

## Common pitfalls

1. Запускать proposal-layer по одному слову `КП`.
2. Давать generic `в файл` перебить explicit composition-format.
3. Оставлять collection на стадии contract parsing без downstream execution.
4. Дублировать executor-логику в skills вместо backend.
5. Проверять только unit-path и не делать post-restart health/soak на prod.
6. Считать health-check достаточным доказательством, что user-path работает. Для acceptance нужен новый `chat_task`, который реально вышел из `pending` и завершился без ручного дожима.
7. Стартовать immediate worker без атомарного claim `pending -> running` перед запуском thread/process.
8. Требовать от модели идеальную dashboard-структуру и не держать backend fallback payload.
9. Держать тяжёлый Telegram export в синхронном chat-task контуре без консервативных лимитов или явного async-контракта.
10. Стучаться в однопоточный TG API параллельными backend export-вызовами. Если внешний collector single-threaded, нужен backend singleflight/lock и observability по wait/timeout.

## References to load when needed

Если задача уходит в runtime-реализацию, дополнительно смотри:
- `artifact-delivery-contract-hardening`
- `scheduled-job-delivery-diagnostics`
- `turnkey-local-first-mvp-delivery`
- `telegram-it-consulting-monitor` для telegram-specific collection cases
