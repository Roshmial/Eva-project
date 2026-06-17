# June 2026: jobs screen, mobile nav, chat refresh, file preview

Use this note as a concrete acceptance reference for Hermes Web UI regressions where build passes but runtime behavior is broken.

## Confirmed runtime failure pattern

Parent screen bindings in `App.jsx` can drift after cleanup/refactors:

- `handleUpdateJobDisplayName`
- `handleOpenCreateJob`
- `handleOpenEditJob`
- `handleOpenRecipientsModal`
- `handleOpenAccessModal`

These names looked plausible but were not real functions. The correct runtime bindings in this session were:

- `handleUpdateDisplayName`
- `openCreateJob`
- `openEditJob`
- `openRecipientsPicker`
- `openAccessPicker`

Symptom in browser runtime:

- screen opens or navigation starts
- then React throws `ReferenceError`
- app body/root may go blank after clicking `Задачи`

## Contour lesson

For local dev acceptance in this session:

- frontend dev surface: `127.0.0.1:4173`
- user-facing frontend surface: `95.182.85.233:8803`
- working backend for acceptance/dev proxy: `178.104.207.89:8791`

Do not assume `95.182.85.233:8791` is the backend just because it is numerically adjacent to the frontend host. In this session it returned `Connection refused` and was the wrong target for dev proxying.

## Mobile/UI regression pattern

Two different causes combined into the visible `Задачи` failure:

1. onboarding overlay intercepted clicks
2. mobile CSS hid `.nav-btn-jobs`

The durable fix pattern was:

- make advisory onboarding non-blocking for pointer events
- close onboarding when navigating between major sections
- explicitly keep the jobs button visible on mobile
- verify narrow viewport behavior with a real browser run

## Chat refresh pattern

The useful polling shape added here:

- immediate refresh on entering chat
- `2500 ms` interval when there is a pending assistant placeholder
- `8000 ms` interval in steady state

This is a good acceptance baseline when the complaint is "messages appear only after manual refresh".

## File preview acceptance pattern

A code-only check is not enough. The acceptance path that proved useful was:

1. create a temporary acceptance user
2. create a thread
3. upload a real PNG
4. open profile → files
5. click `Открыть`
6. verify:
   - preview action exists
   - preview modal opens
   - image element renders
   - preview link points to `/api/files/<id>/download?...`

Observed successful result in this session:

- `openCount=1`
- `modal=1`
- `img=1`

## Practical browser acceptance sequence

A reliable order for this class of bug:

1. login as a disposable acceptance user
2. open profile/files and verify preview
3. open jobs and verify screen content
4. return to chat and verify composer/send path still renders
5. run the same jobs navigation on mobile viewport

## Verification outputs worth preserving

- `npm run react:build` passed after the handler fixes
- live browser run showed `Задачи Hermes` with task list/details instead of runtime crash
- live mobile run showed jobs nav visible and active
- Hermes Agent browser tests still passed separately: `39 passed`
