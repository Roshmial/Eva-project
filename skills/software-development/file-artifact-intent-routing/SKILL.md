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

## Verification checklist

- [ ] generic `дай файл` routes to export path
- [ ] explicit `в csv/pdf/docx` routes to deterministic export path
- [ ] response with file claim always has attachment/path/url
- [ ] collection request with complete inputs returns real artifact
- [ ] live runtime proof confirms download handle works

## Common pitfalls

1. Считать красивую текстовую формулировку доказательством, что файл есть.
2. Поддержать только explicit format names и забыть про generic `дай файл`.
3. Смешивать file intent с обычным explanatory answer.
4. Проверять только текст сообщения, а не attachments metadata.
5. Вводить второй export-pipeline вместо reuse существующего message-attachment path.

## Recommended companion skills

- `artifact-delivery-contract-hardening`
- `collection-proposal-routing`
