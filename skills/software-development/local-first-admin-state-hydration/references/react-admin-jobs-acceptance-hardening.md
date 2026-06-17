# React admin/jobs acceptance hardening

Use this note when a local-first React runtime already persists `screen`, `adminSection`, or active IDs and the acceptance path keeps mixing real product bugs with restore-path noise.

## Durable patterns from the session

1. Treat restore-path and click-navigation as separate acceptance entry points.
   - `screen='admin'` plus `adminSection='users' | 'operations' | 'references'` in persisted UI state is a valid product path.
   - If headless tab clicks are flaky but reloading into the subsection renders correct data, keep the smoke focused on the restored subsection behavior instead of overfitting to the click itself.

2. Make login tolerant of an existing session.
   - Smoke scripts should not assume the login form is always present.
   - First detect whether the page is already authenticated and only perform credential entry when needed.

3. Update selectors when admin user creation moves into a modal.
   - A previously valid inline `Email/Password/Name` form may become a `Новый пользователь` button plus modal.
   - Acceptance should click the opener, then target modal-scoped labels and the create/save button.

4. For pause/resume, refresh detail from the mutation result.
   - Backend status can change correctly while the detail panel still shows the old action button.
   - After `updateJob(status=paused|active)`, refresh `activeJob` directly from the returned payload or an immediate targeted job re-read before asserting the next button state.

5. Distinguish product defects from smoke fragility.
   - Backend `dashboard-policy` or job status API succeeding while UI still looks stale usually points to hydration or detail-state wiring, not the mutation itself.
   - Repeated `401` or missing login form during smoke can be acceptance setup drift rather than product regression.

## Good verification sequence

1. Verify API truth for policy or job status.
2. Verify restored UI state on the same runtime.
3. Verify modal/detail flows with current UI contracts.
4. Only then tighten selectors for click-path smoke.

## Do not over-learn

Do not record transient masked-env mistakes or one-off credential mixups as durable rules. Keep the reusable lesson: acceptance scripts must tolerate restored sessions and should verify actual UI contracts before assuming old selectors still apply.
