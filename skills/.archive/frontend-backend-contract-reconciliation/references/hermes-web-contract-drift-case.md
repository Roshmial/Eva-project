# Hermes Web contract-drift case

Problem class:

Frontend and backend both existed, but the React layer had drifted away from the current backend API and payload shapes.

Observed symptoms:

- admin screen crash: `O.getAdminDataSources is not a function`
- user-reported disappearance of chat parameters that previously exposed:
  - model choice: `reasoning` / `обычная модель`
  - source policy: internal only / local-first / external
- user perceived the whole frontend as having changed unexpectedly

What was found:

1. Frontend caller drift
   - `App.jsx` still called `api.getAdminDataSources()`.
   - `api.js` no longer exported that helper.

2. Backend contract had moved
   - current admin endpoint: `GET /api/admin/dashboard-policy`
   - current admin patch endpoint: `PATCH /api/admin/dashboard-policy`
   - response shape: `dashboard_policy + data_sources`
   - bootstrap also exposed `llm_routing`

3. UI shape drift
   - frontend screen still wanted a synthesized structure like:
     - `data_policy.source_registry`
     - `data_policy.processing_policy`
   - backend no longer sent that shape directly for the relevant flows

Repair approach that worked:

1. Replace dead helper usage with the current admin policy endpoint.
2. Add a frontend normalization function that maps:
   - `dashboard_policy + data_sources`
   into
   - `data_policy.source_registry + processing_policy`
3. Restore the missing chat controls from backend capabilities already present in bootstrap:
   - `llm_routing.selector` -> model selector UI
   - `dashboard_policy.source_mode` -> source policy selector UI
4. Ensure outgoing request payload again includes:
   - `model_preference`
   - `source_mode`
   - `explicit_source_ids`
5. Rebuild and inspect the artifact.

Verification pattern that proved useful:

- build frontend bundle
- grep/check built JS for:
  - restored labels like `обычная модель`, `reasoning`, `Политика источников`
  - current endpoint marker like `/admin/dashboard-policy`
  - absence of removed helper string like `getAdminDataSources`
- run targeted backend tests for adjacent capabilities, especially routing/bootstrap exposure

Why this matters:

This was not a random visual regression. It was a backend-contract migration that the frontend had only partially absorbed. The right fix was contract reconciliation, not cosmetic tweaking.
