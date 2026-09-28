# Local screen-open triage when wrapper and auth both confuse the result

Use this when the user asks for a simple confirmation like "open profile" but local UI runtime has two overlapping failure modes.

## Pattern

1. Check whether the documented localhost target is still the live one.
   - Prior notes may mention one port while the currently running frontend is on another.
   - Treat docs as hints; confirm the live listener first.

2. Distinguish wrapper failure from app failure.
   - `agent-browser open` can report success while later `snapshot -c` returns `(empty page)` and `eval window.location.href` returns `about:blank`.
   - That is evidence of wrapper/session drift, not proof that the app itself is blank.

3. Prove the app through an independent browser path.
   - Playwright can show whether the real page renders.
   - For this session, the independent path showed the login screen rendered correctly even though the wrapper path lost page state.

4. For "is screen X open?" requests, report the exact state reached.
   - valid confirmations are different:
     - target screen is open;
     - only login screen is open;
     - login failed / auth blocked further progress;
     - app unreachable.
   - Do not compress these into a generic "opened" claim.

5. If login returns 401, keep auth failure separate from browser-runtime failure.
   - The frontend may be healthy while the backend auth path is not.
   - In that case, do not claim the requested screen is open even if the shell page loads.
