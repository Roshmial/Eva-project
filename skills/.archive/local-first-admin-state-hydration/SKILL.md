---
name: local-first-admin-state-hydration
description: Diagnose and prevent local-first React admin screens that restore into a visible route before section data has hydrated; model source registries at the connector-class level instead of one dataset per current use case.
---

# When to use

Use this skill when working on a local-first React or similar web admin surface where:
- UI state is restored from local storage or another persisted client state source;
- a screen can open directly into `admin`, `settings`, `overview`, or another privileged section without going through the normal navigation click path;
- the screen renders a shell immediately, but section data is loaded by a separate async function;
- a registry is being introduced for data sources, integrations, APIs, or connectors;
- acceptance must prove real load/save/reload behavior, not just successful API responses.

Typical symptoms:
- the admin screen is visible but lists, cards, or toggles are empty until a second interaction happens;
- API routes return correct data in isolation, but the UI stays on default arrays or null state;
- a registry is drifting into a list of one-off datasets or current pipelines instead of stable connector classes.

# Core rule

A restored screen is not the same as a navigated screen.

If `loadCoreState()` or boot logic can restore `screen='admin'` directly, the code must also ensure the admin data loader runs from that restored state. Do not assume the normal `handleNavigate('admin')` path will fire.

# Recommended implementation pattern

1. Separate shell restore from section hydration.
   - It is fine for bootstrap to restore `screen`, active IDs, and section names.
   - It is not fine to stop there if the screen depends on additional async section data.

2. Add a guard effect for restored privileged screens.
   - In React, use an effect that watches the minimum state needed to know hydration should occur.
   - Typical guard:
     - authenticated user exists;
     - user role permits the screen;
     - current screen equals `admin` (or another privileged screen);
     - section data has not loaded yet.
   - Then call the section loader once.

3. Make the guard idempotent.
   - The effect should early-return once the admin data is already loaded.
   - Avoid duplicate fetch storms.

4. Keep navigation-triggered loads too.
   - Direct restore and normal click-navigation are two separate entry paths.
   - Support both.

5. Acceptance must test both entry paths.
   - open the screen through the normal click path;
   - restore directly into the screen via persisted UI state;
   - confirm both end with the same rendered admin data.

# Registry modeling rule for data sources and connectors

For `data_sources`-style registries, the top-level registry should represent stable source classes, not one current dataset, digest, or derived artifact.

Good top-level entries when the UI is product-facing policy rather than a raw integration catalog:
- `user_attachment_dataset`;
- `local_dataset_registry`;
- `internal_connector`;
- `external_connector`;
- `web_research`.

Avoid at the top level:
- one specific Telegram digest;
- one current CRM export;
- one temporary derived report;
- Google/Telegram/procurement as separate top-level policy entries when they are really concrete routes inside a broader connector class;
- pipeline-specific artifacts that belong inside a connector or local dataset layer.

The correct layering is:
- top level: stable policy classes;
- child level only for `internal_connector` and `external_connector`;
- next level fields should stay minimal and practical: alias, route, purpose, target/destination, enabled flag, and status `available` / `unavailable`.

Do not set an aspirational schema for child connectors if Hermes/runtime/environment can only provide a smaller real inventory. Prefer a thin honest inventory over a rich speculative one.

# Source-of-truth pattern

Prefer this order:
1. code-level canonical definitions for stable source classes;
2. a sync step that materializes them into the reference or admin registry table;
3. admin/API responses read from the synchronized registry;
4. policy uses those active registry items, not a hand-maintained UI list.

This gives you:
- one code-level place to evolve connector classes;
- DB-backed admin visibility;
- less drift between backend logic and UI;
- safer migration from legacy source keys.

# Legacy compatibility rule

When replacing old source keys with better connector-class keys:
- keep an alias map in normalization logic;
- apply it both when saving policy and when resolving runtime context;
- never silently drop legacy keys just because the registry name changed.

# Live verification workflow

1. Verify the API path first.
   - Confirm the policy endpoint returns both the policy payload and the synchronized registry entries.

2. Verify the UI render path second.
   - Confirm the screen shows the same number of source entries as the API.
   - Confirm restored-state boot into the admin screen hydrates the section automatically.

3. Verify round-trip state.
   - change policy mode;
   - change allowed sources;
   - save;
   - re-read through the API;
   - reload the page;
   - confirm the UI still reflects the saved state;
   - restore the original state if this is a verification run.

4. Separate verification failures by layer.
   - API correct + UI empty -> likely state wiring or hydration issue.
   - UI shows the card but not the data -> likely screen shell restored before section load.
   - direct route restore fails but click-navigation works -> missing hydration effect.

# Browser verification pitfall

When live UI hydration is asynchronous or dev-server timing is noisy, avoid brittle single-point waits.

Prefer:
- polling for a meaningful rendered condition such as `document.querySelectorAll('[data-source-key]').length > 0`;
- verifying final DOM state after a short stabilization delay;
- using Playwright or equivalent runtime fallback if higher-level browser wrappers are unstable.

Do not conclude that the backend is broken just because an early DOM wait timed out.

# Acceptance hardening for restored admin/jobs flows

When a local-first React runtime persists UI state, acceptance should explicitly support two valid entry paths:
- normal click-navigation;
- restore via persisted UI state (`screen`, `adminSection`, active IDs) followed by reload.

Use the restore-path intentionally when the goal is to verify that a section can re-open correctly on the same canonical runtime, especially when headless tab switching is flaky but the section itself renders correctly once restored.

Recommended rules:
- make smoke scripts tolerant of an already-authenticated session; do not assume the login form is always the first screen;
- for admin sections, set persisted `adminSection` and reload when you need a stable proof of section hydration across `overview -> users -> operations -> references`;
- if a create/edit flow moved from inline inputs to a modal, update the smoke to target the modal contract instead of preserving stale inline selectors;
- after job status mutations like pause/resume, update the active detail from the fresh mutation response or from an immediate targeted re-read of that job, rather than relying only on list refresh side effects.

# Jobs detail refresh rule

For local-first job screens with optimistic concurrency or versioned writes:
- treat `updateJob()` as the authoritative new detail payload when available;
- update `activeJob` from that fresh payload immediately;
- only then refresh the jobs list in the background;
- do not depend on `loadJobs()` alone to make the detail panel flip from `pause` to `resume` or vice versa.

This reduces stale-detail bugs where backend status is already `paused` or `active` but the detail panel still renders the old button set.

# Pitfalls

- Restoring `screen='admin'` without triggering `loadAdmin()` or equivalent.
- Treating a visible admin shell as proof that section data loaded.
- Modeling the registry around today's most visible dataset instead of stable connector classes.
- Maintaining a separate frontend list of sources instead of consuming the synchronized backend registry.
- Dropping legacy source keys during normalization or policy save.

# Done criteria

Consider the task done only when all are true:
- restored admin screen hydrates section data without extra user interaction;
- UI source list matches the API registry count and keys;
- policy save survives reload;
- legacy keys normalize into current registry keys without silent loss;
- registry entries describe connector/source classes, not one-off artifacts;
- jobs detail reflects pause/resume state on the same live screen, not only in backend API responses;
- acceptance can re-enter admin subsections and jobs detail on an already-restored session without assuming a fresh login.

# References

- See `references/admin-state-hydration-and-registry-notes.md` for a compact worked example of the restore-path hydration bug and the connector-class registry framing.
- See `references/policy-connector-inventory-shape.md` for the product-facing split between stable top-level policy classes and minimal child connector inventory under internal/external groups.
- See `references/react-admin-jobs-acceptance-hardening.md` for the acceptance patterns that stabilized restored admin subsections, modal user creation, and job detail pause/resume verification.
