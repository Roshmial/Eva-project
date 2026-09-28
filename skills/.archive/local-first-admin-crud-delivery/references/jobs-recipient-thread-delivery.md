# Jobs recipient delivery: separate job-thread invariant

Класс задачи: Hermes Web MVP / local-first jobs UI и backend delivery.

Что подтвердилось на живом runtime:
- Для `fixed_user` доставка идёт не в обычный пользовательский чат, а в отдельный thread с `thread_kind='job'` и привязкой `job_id`.
- Для `fixed_thread` выбранный chat-thread используется только как источник владельца (`user_id`). Сообщение должно появиться в отдельном `job`-thread владельца выбранного чата, а не в самом исходном чате.

Практический способ проверки:
1. Создать тестовую job с одним recipient типа `fixed_user` или `fixed_thread`.
2. Выполнить `run`.
3. Проверить `job.runs[0].delivered_to_json`.
4. Подтвердить в БД/данных threads, что доставка ушла в thread с `thread_kind='job'` и нужным `job_id`.
5. Для `fixed_thread` отдельно проверить, что в исходном выбранном chat-thread новых job-сообщений нет.

Frontend-вывод:
- В job-recipient modal должны существовать оба выбора: пользователи и чаты.
- Подпись в UI должна явно объяснять, что выбор чата не означает доставку в этот чат; он создаёт отдельный job-чат владельца этого чата.

Product-вывод:
- В list-view jobs не раздувать строку деталями вроде расписания, visibility и recipient summary, если пользователь просит «нормальный вид». Для читаемости оставлять только визуальное название, техническое имя и статус; recipient semantics раскрывать в detail/modal.
