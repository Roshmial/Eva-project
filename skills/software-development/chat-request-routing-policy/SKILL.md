---
name: chat-request-routing-policy
description: Use when recurring chat request classes should move from phrase-level backend hardcode into a declarative routing policy layer plus focused skills.
version: 1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [routing, policy, backend, skills, local-first]
    related_skills: [collection-proposal-routing, monitoring-request-routing, file-artifact-intent-routing]
---

# Chat request routing policy

## Overview

Этот skill нужен, когда в backend начинают расползаться phrase-level `if/else`, regex-ветки и локальные словари для повторяющихся классов запросов:
- сбор данных;
- мониторинг;
- file/export intent;
- proposal / estimate intent.

Цель — не переносить runtime в skill, а развести слои правильно:
- skill = policy, guardrails, verification, contract expectations;
- backend = execution, storage, delivery, attachment handling;
- policy file = декларативные trigger-rules, которые можно менять без переписывания half-backend.

## When to use

Использовать, когда появляются признаки:
- backend ловит intent по всё новым жёстко зашитым фразам;
- похожие правила дублируются в нескольких функциях;
- false triggers начинают ломать соседние сценарии;
- повторяющиеся классы запросов уже известны и их лучше описать как policy-data;
- user-facing поведение должно быть согласованным между collection / monitoring / file / proposal paths.

## Target architecture

### Layer 1. Skill layer
Здесь живут:
- правила классификации;
- anti-false-trigger guards;
- distinction one-shot vs recurring;
- distinction dataset vs proposal;
- verification checklist.

### Layer 2. Declarative policy layer
Здесь живут:
- trigger patterns;
- marker lists;
- source keyword rules;
- schedule keyword rules;
- subject/field extraction patterns.

Это должен быть data-file, а не размазанный код.

### Layer 3. Backend runtime layer
Здесь живут только:
- route lock;
- execution path;
- fetch / parse / transform;
- artifact generation;
- attachment serialization;
- job creation;
- delivery.

## Practical rule

Если изменение касается словарей фраз, keyword-rules, extraction patterns или guard-маркеров — сначала смотри, можно ли менять policy-file, а не Python-ветку.

Если изменение касается:
- реального вызова API;
- обработки файлов;
- генерации artifact;
- сериализации attachment;
- создания recurring job;

это уже backend/runtime.

## Good outcomes

Хороший результат выглядит так:
- новый phrasing пользователя поддерживается изменением policy-data;
- skill описывает, как этот класс запросов должен вести себя;
- backend-код не получает ещё один хаотичный `elif` под частный текстовый кейс.

## Bad outcomes

Плохой результат:
- правила живут только в чат-обсуждении;
- или только в skill;
- или только в backend-regex, который уже никто не помнит где именно лежит.

## Verification checklist

- [ ] intent-rules вынесены в декларативный policy layer
- [ ] skill описывает guardrails и expected behavior
- [ ] backend не дублирует policy по нескольким местам
- [ ] existing regressions на file / monitoring / collection / proposal проходят
- [ ] route priority остаётся взаимоисключающим

## Common pitfalls

1. Называть policy-layer skill-ом и всё равно оставлять те же regex внутри Python.
2. Пытаться засунуть execution в skill.
3. Переводить в policy то, что на самом деле является runtime side-effect.
4. Делать новый policy-файл, но не привязывать к нему тесты.
5. Убирать хардкод только в одном сценарии, оставляя соседние классы запросов в старом виде.
