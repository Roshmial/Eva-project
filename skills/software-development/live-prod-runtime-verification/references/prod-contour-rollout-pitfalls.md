# Prod contour rollout pitfalls

Use this note together with `live-prod-runtime-verification` when the working tree says "fixed" but the named live contour still misbehaves.

## 1. Bind-host regression after backend restart

Symptom:
- frontend proxy starts returning `frontend_proxy_upstream_unavailable` after a backend restart,
- but local health on the backend host still looks fine.

What to verify:
- check the actual listen address with `ss -ltnp` or equivalent,
- compare `127.0.0.1:port` vs `0.0.0.0:port`,
- compare that with how the frontend reaches the backend (external IP, localhost, unix socket, etc.).

Durable fix:
- persist the correct bind host in runtime env before restart,
- then re-check both direct backend HTTP and frontend-proxied HTTP.

Why it matters:
- otherwise you can restart into a state where the service is healthy locally but unreachable from the frontend contour.

## 2. Local user-systemd prod frontend

Some "remote" prod surfaces are actually served by the local host running Hermes.

Additional pitfall:
- a manual backend process can keep owning the port while `systemctl --user` tries to restart the official unit
- the contour may look partially healthy by direct HTTP, while the unit sits in restart loops with `Address already in use`

Verification rule:
- after rollout, check both `systemctl --user is-active ...` and actual port ownership with `ss -ltnp`
- if the unit flaps but the port still answers, suspect a rogue/manual process rather than a successful managed restart
- finish by ensuring the canonical user-systemd unit owns the port again, not just "something" listening on it

Pattern:
- public frontend on a named host/port,
- underlying service is a local `systemctl --user` unit serving a production bundle.

Implication:
- after frontend code fixes, rebuild the bundle and restart the real local user-systemd service,
- do not assume that backend rollout alone updates what the public frontend is serving.

## 3. Chained admin-screen failures

Admin screens often fail in layers.

Pattern:
- first missing handler blocks screen open,
- after fixing it, a second missing handler appears only after the screen renders or a deeper tab/action is clicked.

Verification rule:
- after the first fix, reopen the admin screen on the live surface,
- then exercise at least one deeper tab or action before calling it closed.

## 4. Marker-file runtime ingestion probe

For document extraction, do a live probe through the real API with small synthetic files that contain unmistakable markers.

Suggested markers:
- DOCX header: `HEADER-ALPHA`
- body paragraph: `BODY-BETA`
- table cell: `TABLE-GAMMA`
- PPTX slide text: `TITLE-DELTA`
- PPTX notes: `NOTE-EPSILON`

What to inspect in the API response:
- `text_extracted`
- `extraction_note`
- preview / excerpt fields

This distinguishes four different states:
- parser logic missing,
- truncation after extraction,
- dependency not installed in runtime,
- feature fully working in deployed service.
