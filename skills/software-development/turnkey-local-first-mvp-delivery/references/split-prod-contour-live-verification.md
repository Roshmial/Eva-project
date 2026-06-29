# Split prod contour live verification

Use when the live product is physically split across hosts/ports (for example: frontend on one server, backend/API on another) but the user expects one production service.

## Durable lessons

1. Do not verify only the backend host if the real prod UI lives elsewhere.
   - First identify the real user-facing frontend origin.
   - Then identify the backend/API contour it talks to.
   - Acceptance is incomplete until both are checked in their actual live locations.

2. Keep contour roles explicit during troubleshooting.
   - Example pattern from this session:
     - frontend/UI on `95:8803`
     - backend/API on `178:8791`
   - Do not mix them in reasoning or report a backend-only check as full prod acceptance.

3. When the user provides live credentials for acceptance, verify identity before blaming application logic.
   - If login returns `401 invalid_credentials`, check whether the exact account exists in the live user store.
   - Look for obvious email mismatch/typo before concluding that the freshness/job logic is still broken.
   - Distinguish:
     - wrong account identifier,
     - changed password,
     - real auth/runtime regression.

4. For job-thread freshness changes, acceptance should follow this order:
   - verify backend health,
   - verify the code/runtime is the updated one,
   - log in with a real target user,
   - inspect that user's job threads,
   - then test the specific freshness behavior (delivery vs user interaction).

5. In split contours, report verification scope honestly.
   - Backend health/API pass is not the same as UI acceptance.
   - UI reachability without successful auth is not the same as per-user behavioral acceptance.
