# Admin state hydration and registry notes

Use this note alongside the `local-first-admin-state-hydration` skill.

## Durable lesson from the session

A local-first React admin screen can restore into `screen='admin'` from persisted UI state and still show empty policy/source data if the boot path restores the screen shell but does not trigger the admin section loader.

The durable fix pattern is:
- keep `loadCoreState()` responsible for restoring screen and base session state;
- add a guard effect that triggers `loadAdmin(false)` when:
  - user is authenticated;
  - role is `admin`;
  - current screen is `admin`;
  - admin data is not loaded yet.

## Why this matters

Without this, verification gets misleading signals:
- backend policy endpoints can return correct payloads;
- the admin card can still render;
- but `dataSources` remains the default empty array until another interaction causes load.

This is a state-hydration bug, not an API bug.

## Registry framing lesson

When the user says there are multiple APIs and more data than one digest, do not model the registry around the current visible dataset.

Correct framing:
- top level registry = source or connector classes;
- lower levels = concrete datasets, feeds, reports, or artifacts.

Examples of correct top-level entries from the session:
- `user_attachment_dataset`
- `local_dataset_registry`
- `telegram_api_connector`
- `google_api_connector`
- `public_procurement_connector`
- `web_research`

## Verification pattern that worked

The most reliable acceptance path was:
1. verify `/admin/dashboard-policy` returns policy plus `data_sources`;
2. verify the live page renders the same source keys;
3. change mode and allowed sources;
4. save;
5. re-read through API;
6. reload page;
7. confirm UI still reflects saved state;
8. restore original policy.

## Browser-runtime lesson

When dev-server hydration timing is noisy, prefer polling for meaningful DOM state such as:
- `[data-source-key]` count becoming non-zero;
- the policy select being present and populated.

This is more robust than a single `waitForFunction()` tied to an early app-layout or route-shell condition.
