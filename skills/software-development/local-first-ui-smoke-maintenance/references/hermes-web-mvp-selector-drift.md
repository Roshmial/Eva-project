# Hermes Web MVP: smoke drift after profile/admin UI restructuring

Session pattern worth reusing:

## Symptom

Canonical UI smoke failed even though the app was largely healthy:
- profile assertion failed: uploaded file not visible in profile files;
- admin assertion failed: admin users block empty / timeout.

## Root cause

These were not product regressions.
The smoke script still assumed an older UI structure:
- profile files were no longer immediately visible on profile open; the script had to switch to `Профиль` -> `Мои файлы` first;
- admin users were no longer expected in the default overview flow; the script had to switch to `Управление` -> `Пользователи`;
- the real users container was `#adminUsersTable`, not the older `#adminUsers` assertion target.

## Durable lesson

When a local-first admin/chat UI becomes more sectioned:
- update the smoke to navigate sections explicitly before asserting content;
- distinguish stale selectors from real runtime defects;
- prefer stable user-flow selectors such as section buttons plus concrete target containers.

## Concrete repair pattern

1. Reproduce the smoke failure unchanged.
2. Verify the same path manually in the live browser.
3. If the content exists behind a tab/panel, update the script to open that tab/panel.
4. Re-run the full smoke until it passes end-to-end.
5. Keep assertions meaningful:
   - uploaded file visible in the correct profile files section;
   - admin users visible in the actual users table;
   - jobs list still visible on the jobs screen;
   - console/network errors empty.
