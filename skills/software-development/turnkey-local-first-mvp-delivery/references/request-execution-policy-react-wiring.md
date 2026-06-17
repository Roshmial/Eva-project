# Request execution policy wiring in React local-first MVP

Use when the backend already exposes runtime `data_policy`, admin endpoints for policy management, and message-level `request_execution_policy`.

## Durable pattern

1. Treat backend `data_policy` as the single source of truth.
   - Bootstrap should hydrate frontend runtime defaults.
   - Admin editors should load from backend payload, not frontend constants.

2. Keep two separate frontend drafts.
   - `requestPolicyDraft`: chat composer state for per-request override.
   - `dataPolicyDraft`: admin editing state for source registry + processing policy.

3. Re-sync drafts from backend truth.
   - After bootstrap load: initialize `requestPolicyDraft` from `bootstrap.data_policy.processing_policy` and `dataPolicyDraft` from `bootstrap.data_policy`.
   - After admin save: update `bootstrap.data_policy`, `admin.dataPolicy`, and both drafts so composer defaults reflect the saved policy.

4. Send policy through both message paths.
   - JSON send: include `request_execution_policy` as an object.
   - Multipart send: include `request_execution_policy` as serialized JSON string in `FormData`.
   - Do not update only one path; attachment flows often bypass JSON helpers.

5. Verify history-level visibility.
   - If backend returns `message.meta.request_execution_policy` or `message.meta.dashboard_artifact`, render them directly in the message history.
   - This keeps governance visible in the same conversation where the dashboard was requested.

## Acceptance checklist

- Admin section can load current source registry / processing policy.
- Admin save updates backend and returns normalized payload.
- Chat composer default mode reflects backend policy.
- Chat send without files includes `request_execution_policy`.
- Chat send with files also includes `request_execution_policy`.
- Message history shows effective policy and dashboard artifact when returned.
- Final closure still requires real build/smoke, not just patch completion.
