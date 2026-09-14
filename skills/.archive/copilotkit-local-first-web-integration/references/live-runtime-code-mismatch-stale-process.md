# Live runtime code mismatch: stale-process diagnosis

Use this when backend source code already contains the expected CopilotKit/chat-dashboard branch, but the live API still answers as if the old path were active.

## Symptom pattern

Typical signals:
- direct code inspection shows a local helper or route branch exists;
- isolated import/in-process call of that helper returns the expected structured payload;
- live API on the real product port still returns an older text-only or downstream fallback response;
- frontend render contract is ready, but nothing appears because the live message lacks structured `meta`.

Example class of mismatch:
- source returns `downstream = telegram-digest-dashboard` and `meta.dashboard.kind = telegram_digest_analytics`;
- live API still returns `downstream = hermes-api-server` plus plain text/file links.

## Fast diagnosis order

1. Confirm the exact live port the UI uses.
2. Find the PID listening on that port.
3. Compare PID start time with the edited file mtime.
4. Inspect the PID `cwd` and relevant env (`HERMES_WEB_*`, backend port, runtime base URL, DB path if applicable).
5. Check whether another sibling repo/process on a nearby port is creating confusion.
6. Reproduce both layers separately:
   - direct import/in-process helper call from the current source tree;
   - real authenticated API call through the live backend route.
7. If import-path and live API disagree, prefer the stale-process hypothesis before patching business logic again.
8. Restart through the project's canonical launcher script, not an ad hoc command, then rerun the same API probe.

## Why this matters

This failure mode can look like:
- `build` green;
- backend smoke green;
- source code obviously correct;
- frontend seemingly wrong because the dashboard never renders.

But the real issue is often simpler: the port is still served by a process that predates the code change.

## Reporting pattern

State the result in layers:
- code path exists in source;
- helper works when imported directly;
- live runtime was stale / was not stale;
- post-restart live API now does or does not emit the expected structured payload.

Do not claim end-to-end success until the live API response itself contains the structured field the frontend depends on.
