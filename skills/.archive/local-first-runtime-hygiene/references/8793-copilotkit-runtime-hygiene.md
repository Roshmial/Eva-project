# Hermes Web 8793 runtime hygiene notes

Use this note when the active contour is the React/CopilotKit local-first stack around ports `8793/8791/8794`.

## Canonical contour
- frontend: `127.0.0.1:8793`
- backend: `127.0.0.1:8791`
- CopilotKit/runtime sidecar: `127.0.0.1:8794`

## Durable lessons

### 1. Check for sibling-repo contamination first
A separate backend from a sibling tree was still listening on `8788`. That created a false path where the frontend or diagnostic scripts could talk to the wrong backend and make fresh fixes look absent.

Operational rule:
- before acceptance, list listeners on `8788/8791/8793/8794` and map them to repo/cwd;
- stop legacy listeners before product diagnosis.

### 2. Proxy defaults matter even if launch scripts override them
`vite.config.js` still pointed at `8788` while the canonical backend for this contour was `8791`.

Operational rule:
- fix stale default proxy targets in-repo;
- do not rely only on launch-script env overrides to reach the correct backend.

### 3. File/open-link contract had a real backend gap
The frontend expected `/api/files/<id>/download`, but the backend route was missing. This was a real product bug, not a smoke-script issue.

Fix shape:
- add backend route `/api/files/<id>/download`;
- return `download_url` in file payloads;
- verify list endpoint plus live authorized download.

### 4. Message-attachment open-link had a data-model mismatch
The attachment download route initially handled only `local_path`, while saved attachments could carry `relative_path`.

Fix shape:
- support `relative_path` fallback in the attachment route;
- verify returned `download_url` from assistant/message attachments with a real authenticated GET.

### 5. Admin health can break on schema assumptions
`/api/admin/health` used `COUNT(DISTINCT user_id)` directly from `messages`, but `messages` only carried `thread_id`. This caused a real `500` on live admin screens.

Fix shape:
- join `messages` to `threads` and count distinct `threads.user_id`.

### 6. Admin aggregates can lie without `COUNT(DISTINCT ...)`
`active_sessions` was inflated by multi-join aggregation across users/threads/jobs/sessions.

Fix shape:
- count distinct session tokens that are not revoked, not raw joined rows.

### 7. Browser-runtime path should be treated as canonical infra, not a one-off fix
A stable local browser-runtime wrapper already existed in `scripts/browser_runtime_env.sh`. The right long-lived paths were under the user home/runtime areas, not ad hoc unpacking inside the workspace.

Operational rule:
- use the wrapper as the canonical entrypoint for browser acceptance;
- do not repeatedly re-debug missing browser libs if the wrapper path exists.

### 8. Smoke drift vs product drift must be separated explicitly
Several UI smoke failures were caused by changed labels, placeholders, and tab structure rather than broken runtime behavior.

Operational rule:
- patch smoke selectors after confirming the underlying feature works;
- reserve product-bug diagnosis for confirmed contract/runtime failures.
