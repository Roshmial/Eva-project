# DuckDB session conflicts and registry reactivation

Use this note when a local-first threaded backend shows intermittent auth failures or when the live source registry is narrower than the code inventory.

## Symptom 1: intermittent 500 on login/bootstrap

Observed failure shape:
- `POST /api/auth/login` returns 500 under live threaded load.
- Traceback points into session revoke/cleanup code.
- DuckDB raises `TransactionContext Error: Conflict on tuple deletion!`.

Practical diagnosis:
- Unit tests can stay green because they do not create enough concurrent session mutations.
- The hot spots are usually:
  - cleanup before login,
  - revoke old sessions for the same user,
  - issue new session,
  - touch/revoke inside auth middleware.

Durable fix pattern:
- Add one process-level lock around all writes to the `sessions` table in the threaded backend process.
- Keep normal reads outside the lock where possible, but serialize cleanup/revoke/issue/touch/logout writes.
- Verify with a concurrent login burst, not just one happy-path login.

## Symptom 2: code inventory is broad, live registry is narrow

Observed failure shape:
- Code defines canonical source classes such as:
  - `user_attachment_dataset`
  - `local_dataset_registry`
  - `internal_connector`
  - `external_connector`
  - `web_research`
- Live API returns only a subset, often because legacy rows still exist and canonical rows were deactivated earlier.

Typical legacy drift:
- old concrete entries like `telegram_digest`, `telegram_api_connector`, `google_api_connector`, `public_procurement_connector`
- new canonical connector groups exist in DB but remain inactive

Durable fix pattern:
- Sync must do more than update payload/label/sort order.
- If a canonical row is present in the computed inventory but DB has it as inactive or soft-deleted, sync must reactivate it:
  - `is_active = 1`
  - `deleted_at = NULL`
- Then verify via live endpoints such as:
  - `/api/bootstrap`
  - `/api/admin/dashboard-policy`

## Architectural rule

For dashboard/source policy, keep the registry at the connector-class level. Do not model one current dataset (for example a Telegram digest) as the main source-of-truth entry when the real platform has a wider API and connector surface.

Legacy aliases are compatibility inputs, not the canonical visible registry.
