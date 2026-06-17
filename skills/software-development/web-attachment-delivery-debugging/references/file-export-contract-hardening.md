# File export contract hardening for Hermes Web

Когда использовать:
- пользователь говорит не «файл скачивается с ошибкой», а «агент вместо файла пишет объяснения»;
- в истории есть claims про невозможность `.docx`, Markdown workaround, security/install ограничения;
- generic request вида «Отправь мне файл» ведёт себя нестабильно.

Что проверять дополнительно к обычной attachment-chain:

1. Маршрутизация запроса
- Определи, был ли запрос распознан как export-request.
- Generic формулировки тоже важны: `отправь мне файл`, `пришли документ`, `дай файл`.
- Если такой запрос ушёл в обычный LLM-path, возможны `timed out` и ложные apology-ответы.

2. Источник экспорта
- Смотри `message_kind=file_response`.
- Проверяй `exported_message_id`.
- Сверяй `preview_excerpt` и реальный исходный assistant-message: backend может экспортировать не тот ответ.

3. Настоящий ли это `.docx`
Минимальная live-проверка:
- HTTP `200` на attachment endpoint.
- `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Ненулевой размер.
- Первые байты payload: `PK\x03\x04`.

4. Реальное backend-ограничение или выдумка модели
Если модель пишет про невозможность создать `.docx`:
- проверь наличие `python-docx` в backend `.venv`;
- проверь, что backend строит файл локально, а не через внешний tool/install path;
- не принимай claims про `security blocked install` как факт, пока не подтверждено runtime/logs.

5. Нормальный контракт для file-request
Правильных финала только два:
- `file_response` с attachment;
- короткая file-specific ошибка backend.

Неправильный финал:
- длинное apology-полотно;
- рассказы про Markdown workaround;
- общие слова про ограничения среды вместо фактического статуса export-path.

Практический урок из прод-проверки на 178:
- повышение timeout полезно, но не заменяет route-hardening;
- реальная проблема может быть не в доставке attachment, а в том, что generic file-request не попал в export-route;
- если в треде нет пригодного предыдущего assistant-answer, лучше вернуть короткую ошибку `Не удалось сформировать файл по предыдущему ответу...`, чем выпускать LLM в свободное объяснение инфраструктуры.
