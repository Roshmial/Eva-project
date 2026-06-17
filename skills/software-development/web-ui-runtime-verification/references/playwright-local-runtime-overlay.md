# Playwright local runtime overlay + same-origin triage

Когда применять:
- `ui:smoke` или Playwright падает ещё до реальной UI-приёмки;
- в ошибках фигурируют missing shared libraries (`.so`), `chrome-headless-shell`, browser startup failure;
- после снятия библиотечного блокера браузер уже стартует, но в консоли всплывают CORS/runtime discovery ошибки.

## 1. Сначала разделить два класса проблем

Не смешивать:
- системный browser-runtime блокер;
- прикладной runtime/UI дефект.

Признак первого класса:
- Playwright/Chromium не стартует;
- `ldd` показывает `not found`;
- smoke не доходит до живой страницы.

Признак второго класса:
- браузер уже запускается и открывает страницу;
- дальше появляются console/network ошибки (`CORS`, `501`, `runtime info fetch failed`, неправильный `copilotkit/info`).

## 2. User-space overlay без root

Если `sudo apt install` недоступен:
1. скачать нужные `.deb`;
2. распаковать их в локальный каталог, например `.playwright-libs/rootfs`;
3. подложить `LD_LIBRARY_PATH` только на время smoke/Playwright-процесса;
4. отдельно проверить бинарь `chrome-headless-shell --version`;
5. отдельно проверить `ldd ... | grep 'not found'`.

Смысл:
- сначала доказать, что missing libs закрыты;
- не делать выводов про приложение, пока не подтверждён сам старт браузера.

## 3. После старта браузера не продолжать «лечить ОС» по инерции

Если браузер уже жив:
- переключиться на console/network/runtime path;
- смотреть `copilotkit/info`, `CORS`, proxy target, `VITE_*`, run-script defaults;
- разделить `browser startup fixed` и `UI flow still failing`.

Это ключевой анти-паттерн: после снятия `.so`-блокера ещё 2–3 итерации тратить на поиск «ещё одной библиотеки», хотя реальная проблема уже в frontend/backend wiring.

## 4. Same-origin для React/Vite preview

Для product-like local-first UI-приёмки предпочитать:
- runtime path вида `/api/copilotkit`;
- существующий Vite proxy;
- тот же backend-origin, что и у основного приложения.

Проверять не только исходники, но и фактические entrypoint defaults:
- `main.jsx` может выглядеть корректно;
- но `run_frontend_*.sh` или env может всё равно подсовывать `http://127.0.0.1:8794/copilotkit`;
- из-за этого в live runtime остаётся cross-origin/CORS, хотя код уже «на вид правильный».

## 5. Как интерпретировать `501` на `/api/copilotkit/info`

Если после перевода на same-origin:
- CORS исчез;
- но `GET /api/copilotkit/info` даёт `501`;

то это уже не Playwright и не system runtime.

Это backend preview/runtime gap:
- либо route оставлен заглушкой;
- либо metadata/info endpoint не реализован;
- либо live backend не перезапущен после патча.

В отчёте это нужно описывать отдельно:
- browser-runtime block removed;
- runtime metadata endpoint still incomplete.

## 6. Что считать хорошим промежуточным отчётом

Разделять минимум на 3 слоя:
- build green;
- browser/runtime visible;
- end-to-end smoke accepted.

Если закрыт только первый или второй слой, не выдавать это за полную продуктовую приёмку.