# Source registry + processing policy + chat override

Use this pattern for local-first web/admin products when the user asks for:
- trusted vs external source boundaries;
- registry of available data sources;
- admin-managed default processing mode;
- per-chat or per-request override of how aggressively external sources may be used.

## Preferred architecture

Extend the existing operational contour:
- backend `app_settings` (or equivalent settings table) stores:
  - `source_registry`
  - `processing_policy`
- bootstrap endpoint returns the same normalized payload for the frontend;
- admin screen edits those settings through normal backend endpoints;
- chat composer sends only a minimal request-level override field;
- backend resolves `effective_processing_mode` and injects the resulting source-policy context into the model call.

Avoid:
- separate policy microservice;
- duplicate frontend-only source dictionaries;
- shadow settings storage disconnected from bootstrap/admin/runtime.

## Recommended data split

### source_registry
Purpose: inventory and trust metadata.

Typical item fields:
- `source_key`
- `name`
- `source_type`
- `origin` (`internal` / `external`)
- `registration_status` (`registered`, `known_external`, `unregistered`)
- `trust_level` (`trusted`, `review_required`, `experimental`)
- `enabled`
- `connector_kind`
- `access_mode`
- `usage_scope`
- `notes`
- `sort_order`

### processing_policy
Purpose: runtime behavior.

Typical fields:
- `default_mode`
- `allow_override`
- `allowed_modes`
- `mode_labels`
- `mode_descriptions`
- `default_external_action`
- `source_selection_order`

Keep registry and policy separate. Registry answers "what exists and how trusted is it". Policy answers "how the system may use it right now".

## Recommended backend flow

1. Seed defaults in the existing settings table.
2. Normalize settings on read/write.
3. Add admin endpoints to read/update both registry and policy.
4. Return normalized policy in bootstrap so chat/admin share one source of truth.
5. Extend the existing message POST flow with `processing_mode_override`.
6. On backend:
   - validate override against `allowed_modes`;
   - deny non-default override if `allow_override=false`;
   - compute `effective_processing_mode`;
   - build a compact system-context block describing active source rules.
7. Store lightweight assistant meta such as:
   - `processing_mode`
   - `processing_mode_override_requested`
   - `source_policy_applied`

## UI pattern

### Admin
Keep two separate sections or cards:
- source registry editor;
- processing policy editor.

Do not bury request-level override rules inside a generic settings dump.

### Chat
Keep it minimal:
- selector for active processing mode;
- short Russian explanation of the selected mode.

Do not expose the full registry editor in chat.

## Acceptance checklist

- bootstrap contains normalized `data_policy` payload;
- admin can read and update registry/policy;
- chat sends override through the existing send path;
- backend rejects forbidden override with explicit error;
- assistant message meta records the effective mode;
- runtime check covers both bootstrap/admin endpoints and real message send.

## Common pitfalls

- mixing source registry and processing policy into one amorphous JSON blob with no clear ownership;
- putting allowed modes only in frontend constants;
- adding a new message endpoint instead of extending the current send flow;
- allowing UI override without backend validation;
- describing external fallback as if it were already verified internal data.
