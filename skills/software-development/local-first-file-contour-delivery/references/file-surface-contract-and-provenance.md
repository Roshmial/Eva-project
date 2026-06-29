# File surface contract and provenance reference

Короткая опора для задач, где file contour уже частично есть, но его нужно собрать в единый продуктовый слой.

## Практический contract

Рекомендуемая форма на file payload:

```json
{
  "original_name": "brief.docx",
  "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "size_bytes": 2048,
  "file_kind": "reused_file",
  "file_origin": "profile_reuse",
  "file_surface": {
    "file_kind": "reused_file",
    "file_origin": "profile_reuse",
    "extraction_status": "recognized",
    "preview_status": "available",
    "used_in_response": true,
    "source_file_id": 77,
    "generated_from_request": false,
    "next_actions": ["open_file", "reuse_file"]
  }
}
```

## Рабочие distinctions

### input upload
- `file_kind: input_file`
- `file_origin: user_upload`

### profile reuse
- `file_kind: reused_file`
- `file_origin: profile_reuse`

### generated deliverable
- `file_kind: generated_result`
- `file_origin: generated_file_response` или `generated_result`

### export previous answer
- `file_kind: exported_answer`
- `file_origin: message_export` или `exported_answer`

## Provenance на assistant message

Если ответ использовал файлы, на assistant meta полезно хранить:
- `used_files` — нормализованные file payloads;
- `used_file_ids` — короткий индекс для фильтрации и проверок.

Стартовый компромисс допустим:
- если точного file-level tracing пока нет, использовать attachments текущего user message как conservative provenance;
- но сохранять это именно в `used_files`, а не смешивать с `attachments` пользователя.

## UI expectations

Минимум, что пользователь должен видеть:
- что это за файл по роли: входной / повторно использованный / сгенерированный / экспортированный;
- откуда он взят;
- распознан ли текст;
- использовался ли он в текущем ответе.

Хороший паттерн:
- file result card показывает result files;
- отдельный блок `Использовано в ответе` показывает provenance.

## Regression checks

Минимальный полезный набор:
- serialize-message contract test для file response;
- `process_chat_task` test на `used_files` / `used_file_ids`;
- regression tests на export follow-up scenarios;
- backend compile check;
- frontend production build.

## Session-specific note

В одной из реализаций хорошим P0 оказался такой порядок:
1. unified backend `file_surface`;
2. `used_files` provenance в `process_chat_task(...)`;
3. frontend contract-driven rendering;
4. targeted backend tests;
5. `vite build` / production build.
