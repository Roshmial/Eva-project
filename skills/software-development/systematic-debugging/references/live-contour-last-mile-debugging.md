# Live contour vs last-mile debugging

Use this when a prod/local-first web issue looks like a backend defect, but the user-visible symptom may sit in the final UI mile.

## Why this matters

A recurring failure mode in split or local-first runtimes:
- backend already computes the right derived field or structured payload;
- operator sees a public host/port and assumes a separate machine or inaccessible contour;
- investigation stalls on access assumptions;
- root cause is actually in the currently reachable frontend/runtime.

## Fast triage order

1. Confirm the contour before touching code
- Verify whether the named host/port is actually served from the current machine, a local systemd unit, reverse proxy, or a genuinely separate host.
- Do not conclude "need remote access" until you inspect the real serving path.

2. Split the incident into three layers
- Backend state: DB timestamps, derived fields like `freshness_at`, stored `message_kind`, `downstream`, `meta.dashboard`.
- Contract/parser: whether the model/backend emits valid structured payloads; watch for wrapped JSON, fenced blocks, prefix/suffix noise.
- Last-mile UI: whether the frontend actually reads the correct field and renders the structured payload.

3. Verify the served frontend, not only the source tree
- Check the live HTML and served bundle name/hash.
- Confirm the relevant token or field name exists in the served bundle, not only in local source.
- If restart/reload tooling is constrained, prove what the live server actually serves before claiming the fix is absent.

## Practical examples from live incidents

### A. Wrong "last activity" in job/digest chats
Symptom:
- UI shows a stale or identical timestamp for multiple job threads.

Debug path:
- Inspect API output for `freshness_at` versus raw `updated_at`.
- If API already computes `freshness_at` correctly, inspect the frontend timestamp selector.
- Typical fix: use `thread.freshness_at || thread.updated_at || thread.created_at` instead of `updated_at` alone.

### B. Dashboard request fails with JSON parse error
Symptom:
- Task fails with something like `dashboard_json_invalid`.

Debug path:
- Reproduce with the same route and inspect the exact model output shape.
- If the model returns explanatory text + fenced JSON + trailing text, a greedy `{...}` regex is too fragile.
- Prefer a decoder that finds the first valid JSON object inside a larger text response.

### C. Structured dashboard is present, but user sees wrong top-line text
Symptom:
- `meta.dashboard` is already normalized and in the right language, but `assistant_message.content` stays in English or stays generic.

Debug path:
- Inspect both the structured payload and the saved text preview/content.
- Add the same language/content guard to the top-level reply text path, not only to the structured dashboard normalizer.

## Pitfalls

- Do not stop at `api/health == ok`.
- Do not confuse a public host label with a separate deployment path.
- Do not patch DB/backend state until you verify what field the frontend actually consumes.
- Do not treat a parser failure and a content-quality/language failure as the same bug; they often sit in adjacent but different stages.

## Good verification evidence

- live bundle hash/name;
- direct proof that the served JS contains the new field path or renderer token;
- rerun of the original failed task/thread to `completed`;
- saved assistant message content + saved structured metadata after rerun.
