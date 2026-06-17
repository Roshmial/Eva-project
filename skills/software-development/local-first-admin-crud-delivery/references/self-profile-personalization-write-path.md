# Self-profile personalization write-path: symptom and fix

Когда пригодится:
- после перевода personalization на backend references;
- когда admin CRUD уже работает, а `PATCH /api/me` всё ещё падает;
- когда UI умеет сохранять nested `assistant_profile`, но self-profile path не подтверждён live-проверкой.

Симптом:
- валидный `PATCH /api/me` с payload вида
  - `assistant_profile.tone`
  - `assistant_profile.answer_depth`
  - `assistant_profile.interaction_mode`
  - `assistant_profile.about_user`
  возвращает `400` и `error = "nothing_to_update"`.

Типовая причина:
- handler считает обновлениями только плоские поля (`name`, `timezone`, `style` и т.д.);
- nested `assistant_profile` собирается отдельно, но сам по себе не делает запрос «update-worthy»;
- в результате self-profile path расходится с admin CRUD/import, хотя contract уже общий.

Правильный фикс:
1. Разрешить `PATCH /api/me`, если в payload есть nested `assistant_profile`, даже когда обычные поля не меняются.
2. Читать текущий `assistant_profile` пользователя из БД и делать merge с частичным payload.
3. Только после merge валидировать значения по активным backend references.
4. При успешной записи увеличивать `users.version`.
5. Писать audit-запись в `user_change_log` с отдельным типом, например `self_update`.

Минимальная проверка после фикса:
1. `GET /api/bootstrap` содержит datasets:
   - `assistant_tones`
   - `assistant_answer_depths`
   - `assistant_interaction_modes`
2. Валидный `PATCH /api/me` возвращает `200`.
3. Ответ содержит обновлённый `assistant_profile`.
4. `style_summary` возвращает русские labels из справочников.
5. `version` увеличивается.
6. Невалидный `tone` возвращает `assistant_profile_invalid_tone`.

Практический вывод:
- Если в admin/reference-задаче «почти всё работает», но self-profile path ещё не подтверждён, задача не закрыта. Для этого класса работ `PATCH /api/me` — обязательный write-path, а не второстепенный хвост.
