# Hermes API-only remote cutover notes

Use this when the target VPS should run Hermes as an internal agent runtime for a web product, not as a Telegram-facing bot host.

## Target shape

- Hermes API Server is enabled and reachable on loopback.
- Gateway may still exist as local runtime/service scaffolding, but messaging platforms are intentionally left unconfigured.
- Web/backend injects user-scoped personalization into downstream Hermes calls.
- Hermes global memory and Hermes global user-profile memory are disabled if they would create a second shared memory plane.

## Practical checks

1. `hermes status --all`
   - Telegram and other messaging platforms should show `not configured` on the new host when they are intentionally excluded.
2. Verify loopback ports for the deployed contour.
   - Example contour from this session: Hermes API `8642`, backend `8791`, frontend `8793`, runtime `8794`.
3. Confirm app mode and health from the backend.
   - `service-info`
   - `health`
4. Confirm backend concurrency knobs are explicit in env/service startup.
   - backend threads
   - chat/background processor concurrency
5. Confirm the assistant identity split is correct.
   - server persona in `SOUL.md`
   - per-user memory/personalization in app-owned profile fields
   - no shared Hermes memory layer active underneath

## Why this matters

Without this split, migrations tend to copy old Telegram/gateway behavior and old global memory assumptions into a multi-user web product. That creates hidden coupling and cross-user context risk.
