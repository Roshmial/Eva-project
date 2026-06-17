# Admin tabs headless acceptance: async section overwrite

When to use:
- local-first React admin screens work in live runtime, but headless browser acceptance intermittently fails to switch tabs/sections;
- a click appears to hit the right `button`, yet the visible section or persisted UI state snaps back to an older value.

Observed durable pattern:
- the click handler may actually fire;
- the visible failure is caused by a later async refresh overwriting the selected section with a stale value;
- sections that trigger their own follow-up reload can appear healthy while simpler sections fail.

Concrete reproduction shape:
1. Enter admin screen.
2. Click a tab such as `users`.
3. Verify both:
   - UI text / active tab marker;
   - persisted state such as `localStorage.hermes_web_mvp_ui_state.adminSection`.
4. Add a temporary console marker in the section-change handler to distinguish:
   - click never fired;
   - click fired, but state was overwritten later.

What fixed it in this session:
- `handleAdminSectionChange(section)` kept the immediate local `setState`;
- for sections that previously only changed local state (`users`, `references`), the handler also triggered `loadAdmin(false, section)` so the eventual async state commit preserved the requested section;
- sections that need a forced refresh (`operations`) kept `loadAdmin(true, section)`.

Why this matters:
- do not stop at DOM-level theories like overlay, selector mismatch, or headless click flakiness if the handler is already firing;
- check for async/state overwrite before rewriting selectors or keeping permanent reload-based workarounds.

Acceptance maintenance lesson:
- once the product bug is fixed, remove or reduce `localStorage + reload` smoke workarounds and return the scenario to normal tab-click navigation;
- if full smoke still fails afterward, treat that as smoke-maintenance debt first, not immediate evidence that the product fix regressed.
