# Runtime diagnostics and frontend relocation

Use this note when a small local-first web contour starts feeling "underpowered" and the team is considering moving only the frontend to a different server.

## What to verify before blaming hardware

Take a live snapshot of:
- CPU count and load average
- RAM, available memory, and whether swap exists
- disk free space and basic `vmstat` I/O wait
- live listeners and the owning processes/cwd
- per-endpoint latency for:
  - backend `health`
  - backend `service-info`
  - sidecar info
  - frontend shell

Reason: a single slow endpoint can come from endpoint design, not host-wide saturation.

## Strong diagnostic signal

If `service-info`, sidecar info, and the frontend shell are fast but `health` is hundreds of milliseconds slower, inspect the health endpoint first.

Typical smell:
- the endpoint performs multiple DB queries
- then shells out to a subprocess bridge to enumerate jobs/runtime state

In that case, parallel probes often scale badly even on an otherwise mostly-idle host.

## Interpreting the result

### Pattern A — real host saturation
Clues:
- CPU stays pegged
- RAM is close to exhaustion or swap is thrashing
- I/O wait is elevated across the sample
- many unrelated endpoints degrade together

Implication:
- moving frontend may help, but the host likely needs broader capacity or contour separation.

### Pattern B — expensive health path on an otherwise healthy host
Clues:
- CPU/RAM/I/O look mostly calm
- `service-info` and frontend shell are fast
- only `health` (or a similar diagnostics path) is slow
- latency rises sharply with 4/8 parallel workers

Implication:
- optimize/split the health path before treating this as a pure hardware problem.

## Safe rule for frontend relocation

When only the frontend moves to another host, keep the browser contract unchanged:
- frontend serves static assets
- browser still talks to `/api`
- backend still owns `/api/copilotkit`
- sidecar remains an internal backend detail

Preferred shape:
- frontend host: static build + reverse proxy `/api/*` to backend host
- backend host: backend app + sidecar + Hermes integrations

Avoid:
- exposing sidecar ports directly to the browser
- keeping Vite dev server as the permanent production surface
- combining frontend move with backend DB migration in the same step

## Acceptance checklist after the move

Re-run live checks for:
- login/logout/session restore
- bootstrap
- admin tabs and admin save paths
- jobs list/create/pause/resume
- file download/open flows with auth
- CopilotKit path through backend-owned `/api/copilotkit`
- CORS allow-origins for the new frontend origin

## Documentation discipline

If the runtime status changed materially, update all three:
- backlog
- runbook/deployment docs
- decision log

Especially do this when the old state said "acceptance still incomplete" and the new reality is "acceptance passed; only hardening tails remain".
