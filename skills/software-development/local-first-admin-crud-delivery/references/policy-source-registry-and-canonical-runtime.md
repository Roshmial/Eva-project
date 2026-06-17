# Policy/source registry и канонический runtime

Когда в проекте одновременно существуют несколько похожих деревьев (`.../hermes-web-mvp-react` и `.../hermes-web-mvp-react-8793`) и несколько наборов портов, live-pass сначала должен подтвердить канонический contour, а уже потом править UI/backend.

Практический урок:
- сначала проверить матрицу `repo -> frontend port -> backend port -> launch script`;
- не считать dev-порты или старое дерево runtime по умолчанию;
- если policy/admin кажется «почти работает», но health падает, проверять не только routes, но и analytics SQL против реальной схемы live БД.

Для policy/data-sources:
- не держать hardcoded seed-список и отдельно живой DB-реестр как независимые истины;
- системный baseline источников лучше хранить одной backend-функцией/registry;
- operational-слой для admin/UI держать в `reference_items` (или эквиваленте) и синхронизировать из registry;
- request-level override должен иметь отдельное имя (`explicit_source_ids`/аналог), а старое `allowed_source_ids` оставлять только как compatibility alias, чтобы не путать policy governance и явный выбор источника в конкретном запросе.
