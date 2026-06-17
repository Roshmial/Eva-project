# DOM sync, null-guards и live browser smoke для больших `index.html + app.js`

Когда полезно:
- после крупного UI-pass на ванильном frontend;
- когда `index.html` уже перестроен, а `app.js` частично живёт в старой модели;
- когда экран визуально почти открылся, но поверх него появляется runtime-banner вроде `Cannot set properties of null`.

## Устойчивый паттерн

1. Сначала перечитать точные DOM-точки:
- новые `id`;
- `data-*`-атрибуты для tabs/sections/buttons;
- placeholder-контейнеры, которые реально остались в HTML.

2. Затем синхронизировать `app.js` по слоям:
- `state`;
- `els` map;
- `render*` функции;
- `set*Section`/`switchScreen`;
- event listeners.

3. Для вторичных блоков, которые могли исчезнуть из новой IA, добавлять null-guards:
- `if (els.adminThreads) ...`
- `if (els.someOptionalPanel) ...`

Это особенно важно для admin/history/reference секций: одна старая ссылка не должна валить уже рабочий экран.

## Типовой симптом

Экран реально открывается, данные частично отрисованы, но в banner висит ошибка `Cannot set properties of null (setting 'innerHTML')`.

Обычно это значит:
- не сломан весь runtime;
- сломана одна старая ветка рендера, которая обращается к уже удалённому DOM-узлу.

Правильная реакция:
- найти конкретный `els.*`, который теперь optional/removed;
- обернуть в null-guard или убрать старый вызов;
- повторно открыть именно этот экран;
- затем отдельно проверить `browser console` и banner.

## Порядок проверки

Технический минимум:
- `node --check app.js`
- backend syntax/smoke, если frontend завязан на backend contracts
- live HTTP backend/frontend

Живой минимум:
- login;
- вход в изменённые экраны;
- `browser snapshot` по фактическому экрану;
- `browser console` после повторного входа в экран, а не только после initial load.

## Урок по интерпретации

Если browser snapshot уже показывает рабочий экран и основные данные, не объявляй весь pass сломанным только из-за banner-ошибки. Сначала отдели:
- частичный secondary render defect;
- полный runtime failure;
- устаревший UI-state от предыдущего render-cycle.

## Пример из Hermes Web MVP

Полезная последовательность была такой:
- профиль, jobs и admin уже были перестроены под новую IA;
- live snapshot показал, что admin screen открывается и данные приходят;
- banner показал `Cannot set properties of null (setting 'innerHTML')`;
- причина оказалась не в основной IA, а в старом безусловном `els.adminThreads.innerHTML`, хотя самого блока в новой админке уже не было;
- null-guard устранил дефект без новой инфраструктуры и без отката UI-pass.
