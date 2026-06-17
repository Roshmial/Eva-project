# Hermes Web acceptance pitfalls: runtime green vs brittle UI smoke

Use this when a local-first Hermes Web contour looks alive at runtime, but end-to-end acceptance still fails.

Key lessons

1. Separate contour health from acceptance-script brittleness.
- Treat frontend/backend/runtime alignment as a different checkpoint from full UI smoke.
- If quick runtime probes are green (`frontend`, `service-info`, auth/bootstrap/profile), do not describe the whole contour as broken just because a Playwright flow still fails.
- Report clearly: runtime aligned; remaining failures are in acceptance automation or narrow UI behavior.

2. Do not assume demo credentials.
- Existing DuckDB state may no longer match `admin@demo.local / demo123`.
- For acceptance, prefer a dedicated admin smoke account and verify login against the live backend before long browser runs.
- If a dedicated acceptance user exists, use it instead of resetting the primary admin account.

3. First-login onboarding can block all nav clicks.
- A welcome/onboarding modal may appear after login and leave `.modal-backdrop-react` intercepting pointer events.
- Dismiss it explicitly before navigation.
- Prefer a DOM-level fallback (`button.click()` inside `page.evaluate`) when normal locator clicks keep getting intercepted.
- Avoid unnecessary clicks on already-active tabs such as `Обзор`; if the target section root is already visible, proceed directly.

4. Prefer stable UI readiness checks.
- For admin overview, wait for the actual section root (for example `#adminDashboardSourceModeReact`) instead of relying only on nearby tab/button clicks.
- For task details, verify that the detail pane belongs to the newly created job before issuing pause/resume actions.

5. Use polling for stateful job actions.
- Pause/resume may not be reflected immediately after a click.
- Poll the backend job state for several seconds instead of asserting after a fixed short sleep.
- If a separate diagnostic flow proves pause/resume works while the main smoke still fails, treat that as a brittle browser path, not a backend failure.

6. Be careful with redaction during execution.
- Never substitute a masked placeholder like `***` into the real command being run.
- Redact only in user-facing summaries, not in the actual env/CLI invocation.

Suggested verification order
- Step 1: runtime/process/HTTP health
- Step 2: auth with the exact acceptance credentials
- Step 3: browser smoke with modal dismissal
- Step 4: narrow admin/task acceptance flows
- Step 5: docs/package refresh only after the acceptance layer is green
