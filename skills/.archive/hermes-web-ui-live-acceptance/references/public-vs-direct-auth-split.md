# Public frontend auth split vs direct backend auth

Use this note when Hermes Web acceptance appears blocked on login or session restore even though backend API checks are green.

## Symptom pattern

- Direct backend login works, for example `http://127.0.0.1:8791/api/auth/login` returns `200` for a known user/password.
- The same credentials fail through the public frontend proxy, for example `http://95.182.85.233:8803/api/auth/login` returns `401 invalid_credentials`.
- Direct authorized export/download works, but browser acceptance on the public surface cannot enter the same user account.
- Manual token injection into browser storage may still show `Сессия истекла`, which points to contour/session divergence rather than to a broken export endpoint.

## Fast classification rule

Do not collapse this into a single "DOCX export is broken" statement.
Split the finding into two claims:

1. Artifact/export contract claim
   - Can the backend produce and return the file for an authenticated user?
   - Verify `GET /api/messages/<id>/export?format=docx` or the equivalent endpoint directly.
   - Check `200`, correct MIME type, file size, and that the downloaded file is a real Office container.

2. Public UI acceptance claim
   - Can the same user authenticate through the exact public frontend `/api` path?
   - If not, the blocker is auth/runtime contour mismatch and the UI export path is not yet admissible as passed.

## Minimum proof set

- Direct backend login result with the target credentials.
- Public frontend proxy login result with the same credentials.
- Backend export/download result for the same user/message.
- Explicit statement whether the public browser session is blocked by auth mismatch or whether the export action itself failed after login.

## Reporting template

- Backend export contract: confirmed / not confirmed.
- Public frontend auth on the same contour: confirmed / blocked.
- Therefore: public UI export acceptance is blocked by auth/runtime mismatch OR failed on the export path itself.

## Why this matters

Without this split, it is easy to waste time patching export UI code while the real issue is that the public frontend is not talking to the same auth/user contour as the backend you validated directly.
