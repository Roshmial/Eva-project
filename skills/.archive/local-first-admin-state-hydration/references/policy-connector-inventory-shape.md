# Policy connector inventory shape

Use this pattern when an admin policy screen needs a stable top-level list of source classes but still must expose concrete connector routes.

## Stable top level

Prefer a short product-facing list:
- `user_attachment_dataset`
- `local_dataset_registry`
- `internal_connector`
- `external_connector`
- `web_research`

Rationale:
- user uploads are a distinct workflow from datasets and connectors;
- local datasets/reports/vitrines stay grouped in one local registry instead of becoming separate policy rows;
- concrete integrations like Google/Telegram/procurement do not belong on the same policy level as product-facing source classes;
- web research remains distinct from generic external connectors because it is a separate search/research mode.

## Child connector rule

Only `internal_connector` and `external_connector` should have child connectors.

Do not add child connector lists for:
- `user_attachment_dataset`
- `local_dataset_registry`
- `web_research`

That adds structure without decision value and blurs the difference between local data inventory and integration routes.

## Minimal child fields

Keep child connector fields practical and discoverable from Hermes/runtime/environment:
- `connector_key`
- `alias`
- `route`
- `purpose`
- `target` or destination
- `enabled`
- `status`: `available` or `unavailable`

Nice-to-have fields are optional; do not block implementation on them.

## Admin UX rule

The admin needs two separate controls:
1. include/exclude the top-level source class;
2. include/exclude concrete child connectors inside `internal_connector` / `external_connector`.

The admin also needs visibility into where requests go:
- alias
- route
- destination/target
- status available/unavailable

Unavailable connectors should remain visible but non-selectable. This avoids wasting time on dead routes while still showing the real inventory.

## Deduplication rule

If multiple technical routes belong to the same family (for example multiple Google-related routes), keep the duplication at the child-connector layer if needed, not at the top-level policy class layer.

The top level should stay stable even when the lower-level inventory changes.
