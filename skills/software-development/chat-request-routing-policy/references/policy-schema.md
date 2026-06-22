# Chat routing policy schema

## Goal

Этот reference фиксирует практический формат policy-layer для routing запросов в backend.

## Recommended file

В runtime-проекте policy-file должен лежать рядом с backend, например:
`services/backend/policies/chat_routing_policy.json`

## Expected top-level sections

- `message_export`
- `collection`
- `monitoring`

## Section responsibilities

### `message_export`
Хранит:
- format keywords
- generic file markers
- non-content markers
- discussion markers
- request stopwords
- regex request patterns

### `collection`
Хранит:
- structured formats
- proposal trigger patterns
- collection action/data-target patterns
- source keyword rules
- subject extraction patterns
- field extraction patterns
- budget/timeline/team extraction patterns

### `monitoring`
Хранит:
- recurring action patterns
- schedule patterns
- follow-up patterns
- default schedule
- weekday rules
- time parsing pattern

## Boundary rule

Если изменение касается phrasing, trigger-слов, regex-маркеров или extraction-правил — это кандидат в policy-file.

Если изменение касается fetch, parsing runtime, artifact generation, DB writes, job creation, attachments или delivery — это backend runtime.

## Verification

После изменения policy-file должны проходить регрессии минимум по:
- file/export intent
- recurring monitoring intent
- collection route priority
- proposal false-trigger guard
- artifact generation for supported source kinds
