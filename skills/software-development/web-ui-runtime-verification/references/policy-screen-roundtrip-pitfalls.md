# Policy screen round-trip pitfalls

Класс проблемы: admin/policy экран визуально выглядит рабочим, но toggle/default selectors не отражают реальный persisted state.

## Симптомы

- визуально кажется, что «всё включено» сразу после открытия экрана;
- toggle кликается, но после reload состояние откатывается;
- selector политики по умолчанию меняется локально, но не переживает save/reload;
- child-коннекторы отображают группу, которая не совпадает с реально сохранённым mapping.

## Проверять по цепочке

1. GET / bootstrap payload
- какие поля реально присылает backend;
- где authoritative allow-list, а где только convenience fields.

2. normalizeDataPolicyShape / аналог
- нет ли оптимистического fallback вроде `enabled=true`;
- не подставляется ли default source, которого уже нет среди enabled options.

3. cloneDraft / hydration
- копируются ли `default_*`, nested maps, notes, connector assignments, child connector lists.

4. JSX controls
- checkbox, select, label и summary должны использовать один и тот же canonical key space.

5. PATCH payload
- backend может ожидать и aggregate map, и отдельный override map для реконструкции группировки;
- сверяй реальный payload с backend route, а не только с frontend draft.

## Конкретный урок из этой сессии

- нельзя считать `enabled=true`, если backend не прислал флаг: в allow-list UI это создаёт ложную картину «всё включено»;
- для child-коннекторов нельзя смешивать `source_key` и canonical group keys `internal_connector/external_connector`;
- если backend использует `connector_group_overrides` для устойчивого round-trip, его нужно отправлять вместе с `connector_targets`, а не вместо него.
