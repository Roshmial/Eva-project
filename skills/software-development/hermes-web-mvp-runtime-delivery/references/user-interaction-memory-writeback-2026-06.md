# User interaction memory writeback for Hermes Web MVP

Когда полезно:
- пользователь говорит, что агент использует только ранее записанный профиль, но не фиксирует новые результаты взаимодействия;
- в базе уже есть `pinned_json` / `assistant_profile_json`, но нет признаков auto-writeback;
- нужно внедрить memory accumulation без отдельной внешней инфраструктуры.

## Проверенный паттерн

Разделяй два слоя:
1. `profile_memory` — ручной профиль пользователя (`pinned_json`, `assistant_profile_json`);
2. `interaction_memory` — автоматически накопленные устойчивые факты из диалогов.

Для второго слоя нужны:
- отдельное поле пользователя, например `interaction_memory_json`;
- отдельный курсор `memory_last_processed_message_id`;
- периодический worker pass внутри уже существующего backend runtime.

## Почему не писать в pinned_json

Смешивание auto-memory и ручного профиля даёт три проблемы:
- админский/ручной профиль перестаёт быть управляемым;
- нельзя понять, что пользователь задал явно, а что накопилось автоматически;
- сложнее безопасно обновлять и чистить память.

## Минимальная схема реализации

1. Добавить user-scoped поля в `users`.
2. В `user_to_dict()` и personalization serialization вернуть `interaction_memory` отдельно.
3. В `build_personalization_block()` включать `interaction_memory=...` отдельной частью, не смешивая с `profile_memory=...`.
4. Периодический worker должен:
   - выбирать пользователей с новыми `user/assistant` сообщениями после курсора;
   - извлекать memory-кандидаты эвристикой, а при наличии model path можно дополнять LLM JSON extraction;
   - обновлять `interaction_memory_json`;
   - продвигать `memory_last_processed_message_id`.
5. Проверять не только запись памяти, но и продвижение курсора.

## Практические проверки

Локально:
- `python3 -m py_compile services/backend/app.py services/backend/test_smoke.py`
- `python3 -m unittest services/backend/test_smoke.py -k memory`
- `python3 -m unittest services/backend/test_smoke.py -k personalization`

Live:
- выкатить backend-код;
- перезапустить runtime;
- создать временного пользователя и короткий диалог с явным предпочтением;
- прогнать periodic writeback;
- проверить, что:
  - `interaction_memory_json` обновился;
  - `memory_last_processed_message_id` дошёл до последнего сообщения;
  - temporary test data можно убрать без следов.

## Важный нюанс тестов

Если в test DB уже есть demo-сообщения, worker может подобрать не того пользователя первым. Для точечных тестов изолируй сценарий:
- либо выставляй другим пользователям курсор на текущий `MAX(messages.id)`;
- либо делай выборку/worker достаточно адресной.

Это не баг самой memory-механики, а ловушка тестовой выборки.

## Подтверждённый live-результат

На live backend `178.104.207.89` periodic writeback успешно записал в `interaction_memory_json` предпочтение вида:
- `По умолчанию отвечай кратко и не используй английские слова без необходимости`

и продвинул `memory_last_processed_message_id` до последнего сообщения тестового диалога.
