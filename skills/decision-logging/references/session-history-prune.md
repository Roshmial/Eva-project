# Безопасная очистка session history после coverage-аудита

## Gate перед удалением

Разрешай удаление только при одновременном выполнении условий:

1. Полный cold archive исходной базы существует, checksum и проверка целостности успешны.
2. Сессии до абсолютного cutoff тематически проаудированы.
3. Кандидаты сверены с raw evidence; `session_id/message_id` существуют и согласованы.
4. Канонический decision log дополнен без превращения планов в достигнутые результаты.
5. Независимая falsification-выборка дала `PASS`; остаточных исключений нет.
6. Журнал, policy и verification report находятся в подтверждённом remote Git commit.

## Зафиксировать популяцию

До первой мутации сохрани абсолютный UTC cutoff и JSON manifest. Минимальные поля:

- `id`;
- `source`;
- `started_at`, `last_activity_at`, `ended_at`;
- `message_count`;
- `parent_session_id`;
- `pinned`, `archived`;
- путь и checksum cold archive.

Не своди итоговые числа из повторных запусков rolling `--older-than 90`: граница сдвигается во время работы.

## Порядок удаления

1. Запусти dry-run штатного prune и запиши число кандидатов и причины пропуска.
2. Запусти prune только после gate.
3. Пересчитай остаток по сохранённому cutoff, отдельно `open/ended`, source и parent/child dependencies.
4. Удали явный остаток через штатную batch-семантику хранилища, а не SQL.
5. Для Hermes batch-delete используй параметры:

```python
skipped = []
deleted = db.delete_sessions(
    session_ids,
    sessions_dir=sessions_dir,
    exclude_active_write_guards=True,
    skipped_ids=skipped,
    include_compression_chain=False,
)
```

`include_compression_chain=False` сохраняет новые continuation-сессии за cutoff: хранилище отвязывает surviving child от удалённого старого parent. Любой `skipped_id` требует отдельной проверки active turn/lock; не обходи guard прямым SQL.

Если CLI не имеет bulk-команды, не запускай сотни отдельных процессов без checkpoint. Используй поддерживаемый batch API/метод того же хранилища в одном процессе и сохрани результат выполнения.

## Проверка после удаления

Обязательно проверь:

- количество сессий до cutoff равно нулю либо каждый остаток объяснён;
- `PRAGMA integrity_check` возвращает `ok`;
- `PRAGMA foreign_key_check` не возвращает нарушений;
- текущие сессии, gateway и delivery работают;
- остановленные refresh/timer возвращены в нужное состояние;
- итоговые counts и результат записаны в decision log и Git backup.

## Логическое удаление и размер файла

После удаления SQLite-файл может не уменьшиться: страницы находятся во freelist, но данные уже отсутствуют из live tables. Не смешивай два статуса:

- `deletion complete` — строки отсутствуют и integrity checks пройдены;
- `physical reclaim pending` — нужен `VACUUM`/`optimize-storage`.

Физическую компактизацию выполняй только offline:

1. Останови gateway и все процессы, удерживающие `state.db`/WAL.
2. Поставь на паузу независимые refresh/backup writers.
3. Запусти штатный `optimize-storage` без `--force`.
4. Восстанови сервисы и таймеры.
5. Проверь gateway health, delivery, integrity и новый размер файла.

Не запускай rewrite SQLite под live writer: замена/перестройка файла при открытом WAL может оставить процессы на устаревшем inode и нарушить дальнейшие записи.