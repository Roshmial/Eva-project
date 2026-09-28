# Data collection contract routing in live chat runtimes

Use when the reported failure is not just "file export broken", but the broader pattern:
- user asks `собери данные ... в csv/xlsx/json/xml`
- chat says something reassuring
- no real dataset appears
- or a fake file is created from ordinary assistant text

## Why this matters

A collection request is not the same class of task as:
- exporting a previous assistant reply
- generating a narrative memo/document
- answering a generic research question in chat

If the backend does not formalize the request before generation, it will often route into the wrong branch and produce a believable but false success.

## Minimum contract before execution

The backend should extract and validate:
- `source_kind` / `source_label`
- `subject`
- `output_format`
- `fields` for structured outputs (`csv`, `xlsx`, `json`, `xml`)

## Correct routing behavior

### Incomplete request
Example:
- `Собери данные по LegalAI в csv`

Expected behavior:
- return `clarification_request`
- explicitly ask for missing source and required fields
- do **not** go to generic LLM chat
- do **not** produce `file_response`

### Complete request
Example:
- `Собери данные из СМИ по теме LegalAI в csv с полями дата, источник, ссылка, summary`

Expected behavior:
- return a route-specific structured response such as `collection_contract`
- store execution steps / contract metadata for the downstream runtime
- only after that hand off to the actual collector/worker

## Verification checklist

1. Inspect the user message text and final assistant `message_kind`.
2. Confirm the collection route is evaluated before generic export/file routing.
3. For structured outputs, verify the backend refuses to treat plain assistant text as a dataset.
4. Verify the prod runtime through the live service interpreter/venv, not ambient `python3`.
5. Run two narrow tests:
   - incomplete request -> `clarification_request`
   - complete request -> `collection_contract`

## Common misclassification

Do not label this only as a file-generation bug.
If `собери ... в csv` goes to generic text and then gets exported, the real defect is routing and contract formation before execution.
