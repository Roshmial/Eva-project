# Server cutover: TG proxy mode + chat layout cleanup

When moving Hermes Web to a new server but keeping Telegram login/session state on the old server:

- Do not copy Telegram session files by default.
- Keep old-server TG auth/session ownership intact.
- Add request/proxy mode in `TG-API` on the new server:
  - `create_link` may request a remote auth link from the old server.
  - `status`, `send_phone`, `verify_code`, `verify_password` should proxy to the old auth backend when remote mode is enabled.
  - `export` on the new server may proxy to the old TG API when a remote base URL is configured.
- Expose the mode explicitly in payloads, e.g. `proxy_mode=remote_auth`, so verification can distinguish local-session flow from remote-session flow.
- Verification criterion: if remote mode is intended but `create_link` still returns a local `auth_url` and no `proxy_mode`, configuration is incomplete even if the endpoint itself works.

Backend/data cleanup lessons from this pass:

- After migrating to PostgreSQL and cleaning product history, verify with runtime counters, not only SQL output.
- A practical acceptance check is `/api/health` showing:
  - `users_count=1` after admin-only cleanup
  - `threads_count=0`
  - `jobs_count=0`
- Re-run a concurrent probe against `/api/admin/chat-notice` after the cleanup to confirm the earlier race fix still holds under the target runtime.

Frontend chat-layout cleanup lessons from this pass:

- For the chat screen, do not keep both topbar and composer sticky when message scrolling already lives inside a nested panel; this easily produces the effect of banners getting visually pinned in the wrong place.
- Prefer this layout rule set:
  - message scrolling belongs to `.messages-panel`
  - parent grid/flex containers must have `min-height: 0`
  - topbar can be static when persistent visibility is already guaranteed by page layout
  - composer can remain accessible without sticky if the main column uses a stable vertical split
- If a source-selection summary creates user confusion, reduce product wording instead of adding more explanatory text. In this pass, the clearer framing was to rename the control from `Источники` to `Режим ответа` and suppress the summary banner when nothing is selected.

Verification checklist extracted from the session:

1. Build frontend locally and on the target server after CSS/layout edits.
2. `py_compile` the TG-API and backend-adjacent Python files after auth/proxy changes.
3. Restart the affected user services.
4. Check backend `health` and `service-info` over localhost on the target server.
5. Test admin login over localhost on the target server.
6. Run a small concurrent probe for `/api/admin/chat-notice`.
7. For TG proxy mode, verify not only HTTP 200 but also that the response shape proves remote mode is active.