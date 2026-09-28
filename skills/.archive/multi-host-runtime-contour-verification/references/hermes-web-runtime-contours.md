# Hermes Web split runtime contours

Use this as a reference example for future multi-host verification work.

## Canonical contour example

### Dev
- `95.182.85.233:8791` — backend
- `95.182.85.233:8793` — frontend
- `95.182.85.233:8794` — auxiliary runtime
- All dev surfaces are on the same host.

### Prod
- `178.104.207.89:8791` — backend
- `178.104.207.89:8794` — auxiliary runtime
- `95.182.85.233:8803` — frontend
- Prod backend and prod frontend are split across hosts.

## Durable lessons

1. Always classify the target surface before acting.
   - A prod frontend fix belongs on the host that serves the prod frontend port, not necessarily the prod backend host.

2. If the current machine already owns the requested frontend port, start with local inspection.
   - Check local `systemctl --user` units.
   - Check local listeners with `ss -ltnp`.
   - Check local runtime files and the served source/build artifacts.
   - Do not begin with SSH discovery for the same machine.

3. Verify split runtimes in layers.
   - Frontend unit/runtime on the frontend host.
   - Backend unit/runtime on the backend host.
   - Proxy target between them.
   - End-to-end request flow.

4. Keep user-facing model controls semantic.
   - Show stable work modes like "Текущая работа" and "Глубокое исследование".
   - Hide internal fallback chains in backend routing/metadata.

5. Prefer free-first fallback chains for agent routing when acceptable.
   - Standard-work chain can start from free general-purpose models and only fall back to paid models later.
   - Reasoning chain can start from free reasoning-capable models and fall back to paid reasoning only on quota/provider failure.
