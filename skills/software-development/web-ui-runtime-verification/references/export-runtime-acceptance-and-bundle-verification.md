# Export runtime acceptance and bundle verification

Когда задача — добавить export/download-функцию в local-first web UI (`txt/docx/xlsx/pdf` и похожие форматы), а полноценный headless browser pass частично блокируется средой, не останавливай приёмку на фразе `UI не удалось открыть`.

Используй layered acceptance:

1. Backend contract first.
- Подтверди live round-trip на реальном backend, а не только локальным smoke.
- Создай временного acceptance-пользователя и тестовый thread/message с assistant-content, который реально должен экспортироваться.
- Проверь каждый поддерживаемый формат отдельным HTTP-запросом:
  - статус `200`;
  - `Content-Type`;
  - `Content-Disposition`;
  - сигнатуру файла (`%PDF`, `PK`, читаемый UTF-8 text preview для `txt`).
- Отдельно проверь unsupported-format path (`rtf` или аналог) и зафиксируй честный `400`/expected error code.

2. Frontend bundle proof.
- Если полноценный UI-click-through не подтверждён, отдельно проверь, что live frontend origin уже обслуживает свежий production bundle.
- Возьми `index.html`, найди фактический `/assets/index-*.js`, скачай его и проверь присутствие ключевых маркеров:
  - route/path export endpoint (`/messages/.../export?format=` или эквивалент);
  - user-facing error strings для unsupported format / unavailable dependency;
  - download filename marker или export helper wiring.
- Это не заменяет UI-приёмку, но честно доказывает, что deploy фронта произошёл именно в live contour.

3. UI verdict split.
- Разделяй два вывода:
  - functional acceptance: backend export и frontend bundle wiring реально live;
  - visual/UI acceptance: пользовательский click-flow в браузере подтверждён или ограничен средой.
- Если browser wrapper/CDP или Playwright падает после логина, не объявляй feature неподтверждённой целиком. Формулируй: `функциональный контур принят, headless UI-подтверждение ограничено browser runtime`.

4. Cleanup is part of acceptance.
- Временный acceptance-аккаунт, thread и messages нужно удалить в конце проверки.
- Не оставляй live БД загрязнённой тестовыми экспортными сообщениями.

Практический минимальный verdict для export-фичи:
- backend endpoint live и возвращает корректные файлы по всем поддержанным форматам;
- unsupported format даёт честную продуктовую ошибку;
- live frontend реально обслуживает bundle с export-wiring;
- если headless UI не добит, это зафиксировано как отдельное ограничение среды, а не смешано с verdict по feature.