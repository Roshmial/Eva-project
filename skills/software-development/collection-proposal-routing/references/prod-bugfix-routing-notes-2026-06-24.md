# Prod bugfix routing notes — 2026-06-24

Короткая выжимка по трём реальным failure classes, полезная для будущих routing/debugging-сессий.

## 1. Recurring monitoring false-success / wrong route

Симптом:
- пользователь явно просит регулярную задачу с cadence/schedule;
- runtime уходит в `data_collection_clarification` вместо `job_created`.

Урок:
- explicit schedule-intent должен иметь приоритет над collection-clarification, даже если в тексте есть source/data wording.

## 2. False `message_export` on engineering request

Симптом:
- длинный запрос про скрипт/Excel/код ошибочно уходит в export previous answer.

Урок:
- слова `excel/xlsx/file/document` сами по себе не доказывают export-intent;
- нужны suppressors для code fences, library markers (`python`, `pandas`) и verbs типа `переделать/доработать/переписать/исправить`.

## 3. Web discovery succeeded, document fetch failed

Симптом:
- source discovery нашёл URL;
- fetch-stage не вытащил ни одного документа;
- старое поведение: жёсткий `web_collection_documents_unavailable`.

Урок:
- если source list уже найден, лучше вернуть partial artifact со списком ссылок, чем пустой hard error.
- при недоступном xlsx runtime лучше честно деградировать в `csv`.

## What was verified

Targeted regressions passed:
- recurring schedule intent wins over collection clarification;
- long xlsx/code request no longer becomes previous-answer export;
- web documents unavailable returns partial artifact instead of hard failure.
