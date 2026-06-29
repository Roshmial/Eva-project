---
name: file-artifact-intent-routing
description: Use when a user asks for a file, document, export, or downloadable result and the system must route that request to a real artifact, not a verbal promise.
version: 1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [file, artifact, export, routing, delivery]
    related_skills: [artifact-delivery-contract-hardening, collection-proposal-routing]
---

# File artifact intent routing

## Overview

Этот skill нужен для повторяющегося класса сбоев, где пользователь просит файл или документ, а агент отвечает как будто файл уже есть, хотя runtime ничего реально не собрал и не приложил.

Skill отделяет:
- file intent;
- export mechanism;
- artifact evidence;
- пользовательскую формулировку ответа.

## When to use

Использовать, когда пользователь пишет:
- дай файл
- пришли документ
- выгрузи в файл
- собери csv/xlsx/docx/pdf
- отправь результат документом
- сделай приложение / attachment / export

А также когда пользователь жалуется:
- ты сказала, что файл готов, а его нет
- attachment не пришёл
- ссылка не работает

## Core rule

Нельзя утверждать, что файл готов, без artifact evidence в том же результате.

Generic file/export markers тоже лучше держать в policy layer, а не размазывать по backend как случайные phrase-specific исключения. Skill описывает expected behavior, а backend должен только честно сделать export и приложить artifact.

Разрешено говорить:
- «собрала файл», только если есть attachment / путь / download_url.

Нельзя говорить:
- «документ готов»
- «файл приложила»
- «ссылка ниже»

если runtime реально не приложил deliverable.

## Intent classes

### Explicit format request
- в csv
- в xlsx
- в docx
- в pdf

### Generic file request
- дай файл
- пришли документ
- выгрузи результат
- сделай приложением

Оба класса должны идти в deterministic export path.

## Routing model

1. Detect file intent.
2. Resolve what content should be exported:
   - latest answer
   - collected rows
   - proposal artifact
   - summary/report
3. Run deterministic export.
4. Attach artifact metadata.
5. Only then allow wording that the file is ready.

## Output contract

Минимальный положительный результат должен содержать хотя бы одно:
- attachment metadata;
- local path to generated file;
- download_url.

Если этого нет, результат считается не файлом, а только текстовым ответом.

## Collection-specific rule

Для запросов формата:
- собери данные и отдай в csv/json/xlsx

контракт двухступенчатый:
1. если вход неполный — honest clarification;
2. если вход полный и source-type уже поддержан — real execution result с attachment.

Не принимать дизайн, где полный request остаётся на уровне plan/contract.

## Analytical file requests

Отдельно обрабатывай класс запросов, где пользователь уже приложил файл и просит не export, а аналитический dashboard по данным:
- проанализируй лиды CRM
- построй дашборд продаж за месяц
- разложи выручку по менеджерам / каналам / этапам

Для таких запросов файл — это не только deliverable, а ещё и источник данных. Поэтому routing должен идти не в generic file-preview path, а в request-aware dataset analytics path.

Базовая последовательность:
1. Detect attached dataset as source-of-truth.
2. Use the user request text to infer analysis intent, а не только format файла.
3. Distinguish хотя бы:
   - generic dataset overview;
   - CRM / funnel analysis;
   - sales / revenue performance.
4. Prefer business sections over schema-only sections:
   - funnel by stage;
   - amount / revenue profile;
   - period dynamics;
   - breakdown by manager / channel / segment;
   - short conclusions.
5. Fallback to generic dataset overview only when business roles cannot be inferred.

Local-first правило: не тащить тяжёлые внешние зависимости только ради простого tabular dashboard, если существующий runtime может прочитать CSV/JSON и базовый XLSX встроенными средствами.

См. также `references/dashboard-file-analytics.md`.

## Verification checklist

- [ ] generic `дай файл` routes to export path
- [ ] explicit `в csv/pdf/docx` routes to deterministic export path
- [ ] response with file claim always has attachment/path/url
- [ ] collection request with complete inputs returns real artifact
- [ ] live runtime proof confirms download handle works
- [ ] for structured exports, verification checks payload content, not only HTTP `200` / file presence / byte size
- [ ] if the request means "export the previous answer", followup phrases like `да, лучше сразу в файл` still resolve to deterministic `message_export`, not to generation of a brand-new file

## Structured export verification

Для `CSV/XLSX/DOCX/PPTX` недостаточно доказательства уровня "endpoint вернул 200" или "файл скачался".

Минимум проверки зависит от формата:
- `CSV/XLSX`: открыть содержимое и убедиться, что в нём есть ожидаемые колонки и строки, а не пустой/служебный лист;
- `DOCX/HTML/Markdown`: проверить, что внутри нормализованное user-facing content, а не сырой planning/service blob;
- `PPTX`: проверить не только число слайдов, но и содержимое slide XML / extracted text, чтобы табличные или структурные данные реально попали в презентацию.

Если live contour split (`public frontend -> remote backend`), финальным доказательством считать именно public export path плюс содержательную проверку артефакта.

См. также `references/structured-export-live-verification.md`.

## Common pitfalls

1. Считать красивую текстовую формулировку доказательством, что файл есть.
2. Поддержать только explicit format names и забыть про generic `дай файл`.
3. Смешивать file intent с обычным explanatory answer.
4. Проверять только текст сообщения, а не attachments metadata.
5. Вводить второй export-pipeline вместо reuse существующего message-attachment path.
6. Для приложенного табличного файла строить только schema preview (`строк/колонок/типы`), игнорируя пользовательский аналитический intent.
7. Для числовых CRM/sales файлов сразу тянуть новые внешние библиотеки или отдельный сервис, хотя текущий local-first backend может покрыть базовую аналитику встроенным dataset path.

## Recommended companion skills

- `artifact-delivery-contract-hardening`
- `collection-proposal-routing`
