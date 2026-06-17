# Live dashboard meta verification

Use this when a chat-first CopilotKit/local dashboard integration looks correct in code, but the real UI still shows only plain assistant text.

## Symptom pattern

- frontend has a dashboard renderer bound to `message.meta.dashboard`;
- build passes;
- backend tests pass;
- starter action/button sends the expected prompt;
- but the assistant reply in the real app contains only narrative text or file paths.

## High-signal verification sequence

1. Verify the actual live frontend/backend ports already serving traffic.
- If launcher scripts fail with `Port ... is already in use`, distinguish `fresh instance started by me` from `existing live runtime already serving`.
- Continue verification against the existing live contour only if you state that clearly.

2. Probe the backend-owned CopilotKit/runtime discovery path separately.
- Example: `/api/copilotkit/info` answering `200` proves discovery metadata exists.
- It does **not** prove the chat-thread analytics route is the one returning the final assistant reply.

3. Send a real message through the same backend thread/message path the UI uses.
- Create or reuse a real thread.
- POST the actual analytics prompt to `/api/threads/<id>/messages` or the project-equivalent route.
- Do not infer success from helper functions in source code.

4. Inspect the persisted assistant message, not only the immediate UI text.
- Read the returned `assistant_message` or fetch the thread back.
- Check for `meta.dashboard` (or the project-equivalent structured artifact field).
- Also note whether the reply instead contains text pointing to generated HTML/JSON files.

5. Interpret the result conservatively.
- `meta.dashboard` present -> structured dashboard path is live.
- No `meta.dashboard`, only plain text/file links -> the live backend is still taking an older analytics/reply path, even if source code already contains a local dashboard helper.

## Reporting template

- frontend artifact renderer: present / absent
- live backend route tested: yes / no
- persisted assistant structured meta: present / absent
- actual live reply mode: structured dashboard / plain text analytics / other
- blocker: code/runtime mismatch, old path shadowing, or unverified browser pass

## Why this matters

Without this check, it is easy to over-report progress:
- build green;
- unit smoke green;
- CopilotKit discovery green;
- but no user-visible dashboard artifact is ever emitted by the live chat flow.
