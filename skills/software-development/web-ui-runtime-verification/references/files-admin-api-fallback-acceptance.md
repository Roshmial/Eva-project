# Files/Admin API fallback acceptance

Когда headless/browser verification блокируется средой, а пользователь спрашивает про фактическую работоспособность файлов или админских данных, полезен backend-first приёмочный путь.

## Когда применять

- browser/CDP недоступен или нестабилен;
- headless Chromium падает на нативном runtime;
- нужно честно ответить на вопросы класса:
  - `файлы открываются?`
  - `в чатах реально есть вложения?`
  - `в админских графиках есть данные?`
  - `название хранится в backend или это local-only?`

## Минимальный порядок проверки

1. Найти frontend contract.
- Какой route вызывает кнопка `Открыть`.
- Какие поля UI ждёт в payload (`attachments`, `download_url`, `display_name`, `last_run_at` и т.п.).

2. Найти backend serializer и download/write-path.
- Что именно сериализуется наружу.
- Не теряется ли нужное поле по дороге.
- На какой field реально опирается handler (`local_path`, `relative_path`, `stored_name`).

3. Подтвердить live round-trip.
- Взять реальный объект из `/api/files`, `/api/threads/:id`, `/api/admin/jobs` или другого живого endpoint.
- Проверить, что downstream route отвечает по этому же объекту.
- Для download-path подтвердить не только `200`, но и `Content-Disposition`/фактическое имя файла.

4. Только потом делать вывод для пользователя.
- `backend-backed/shared`
- `local-only`
- `route есть, но payload неполный`
- `данные для графика есть, но визуальная проверка заблокирована средой`

## Типовые разрывы

- frontend уже умеет строить fallback URL, но backend route ещё не существует;
- serializer хранит вложения внутри `meta`, а UI ждёт top-level `attachments`;
- attachment download route ищет только `local_path`, хотя в живом payload лежит `relative_path`;
- admin chart строится не из timeseries endpoint, а локально из списка сущностей (`threads.updated_at`, `jobs.last_run_at`), поэтому нужно проверять именно эти поля, а не только отдельный analytics route;
- ответ на вопрос `сохраняется ли название` нельзя выводить из UI-кода: нужен реальный round-trip через API.

## Как формулировать вывод

Разделяй:
- что подтверждено по живому API и serializer/write-path;
- что подтверждено именно визуально в браузере;
- что заблокировано средой проверки, а не приложением.
