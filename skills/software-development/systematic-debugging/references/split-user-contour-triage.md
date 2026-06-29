# Split user / contour triage

Use when a chat/UI incident arrives after a previous fix and the new complaint may belong to a different user path, host, or delivery contour.

## Fast checklist

1. Freeze the exact tuple before debugging:
   - user/account/email
   - thread or job id
   - UI host:port the user is actually viewing
   - backend host/port that serves API for that UI
   - symptom layer: storage, API, render, scroll/position, or wrong contour

2. Do not assume the current complaint belongs to the same user or thread as the previous incident.
   - Verify thread ownership in DB.
   - Verify whether recurring/job delivery is routed to `fixed_user`, `fixed_thread`, `owner`, or `origin`.
   - For recurring content, check whether the fresh delivery landed in a different thread than the one you are inspecting.

3. Compare three representations for the same message:
   - raw stored `content`
   - persisted `meta.display_text`
   - API serializer output consumed by UI

4. For "latest messages are missing" complaints, test both hypotheses:
   - messages absent from DB/API
   - messages present, but the chat view opens at the wrong scroll position or renders the older segment first

5. Before claiming a frontend fix is live, confirm you patched the host the user actually opens.
   - A backend fix on one host does not prove the UI host was updated.
   - In split runtimes, the visible UI may be a different box than the backend you just repaired.

## Typical false branches

- Fixing a real backend incident for User A, then assuming User B's complaint is the same bug.
- Seeing updated thread preview/timestamp and assuming the message body was delivered into the same thread.
- Proving data is in DB and concluding the incident is closed without checking UI initial position.
- Building or restarting the frontend on one host while the user is looking at a different live UI host.

## Practical probes

- Query thread ownership and latest message ids by thread.
- Query recurring/job delivery state alongside actual `messages` rows.
- Fetch the exact `/api/threads/<id>` payload for the affected user session.
- Inspect whether `display_text` is already good even when raw `content` contains reasoning noise.
- If UI symptom persists, inspect scroll-to-bottom / initial-position logic in the chat component before touching backend again.
