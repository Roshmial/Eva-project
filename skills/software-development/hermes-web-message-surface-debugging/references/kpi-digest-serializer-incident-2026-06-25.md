# KPI / ТГ Дайджест serializer incident reference

Date: 2026-06-25

## Symptom pattern

Two user-visible threads looked like a generation problem but were actually a serializer-contract defect:
- `ТГ Дайджест`: historical assistant messages contained planning/instruction text instead of the cleaned digest body.
- `KPI`: raw reasoning-preface remained in stored content and leaked on some surfaces.

## Live facts that mattered

- Historical digest messages in live Postgres on `178` had bad planning text in stored fields.
- Helper/export normalization tests were already green.
- The decisive failing test was:
  - `HermesWebBackendSmokeTest.test_serialize_message_exposes_safe_display_text_without_internal_reasoning`
- Failure mode:
  - expected normalized digest body in `payload["display_text"]`
  - actual value was empty string.

## Root cause

In `serialize_message(...)`, assistant messages with `recurring_summary` had their `display_text` explicitly cleared.
That meant:
- helper functions could normalize correctly;
- export/viewer could be partially fixed;
- but the main chat API still had no safe top-level `display_text` to return.

## Fix pattern

Replace "clear display_text when recurring_summary exists" with:
- choose best recurring body from `summary`, then `status_detail`, then fallback body;
- run it through `build_message_display_text(...)`;
- preserve it as top-level and meta `display_text`.

## Tests used

Green after fix:
- `test_extract_hermes_output_for_delivery_strips_internal_reasoning_prelude`
- `test_message_export_recurring_uses_normalized_digest_body`
- `test_build_message_display_text_strips_russian_internal_reasoning_prelude`
- `test_serialize_message_exposes_safe_display_text_without_internal_reasoning`

## Deployment note

On the live `178` contour, direct in-process restart was blocked by gateway constraints.
Working fallback:
- sync updated `app.py` to host;
- confirm `systemd` unit uses `Restart=always`;
- terminate main PID;
- let `systemd` auto-restart the backend;
- verify service is back up and rerun the targeted unittest remotely.
