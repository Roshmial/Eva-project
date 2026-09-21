# CDP 404 and UI regression notes — 2026-06-15

What was learned from this incident:

## 1. Browser-tool failure mode split

Observed split:
- `browser_navigate`, `browser_snapshot`, `browser_console` could already succeed;
- `browser_vision` was the unstable part.

Implication:
- do not describe this as “browser is broken”;
- localize it to screenshot/vision path vs session acquisition.

Applied fix pattern:
- prefer screenshot capture through the already-live CDP supervisor/session;
- only fall back to a separate CLI screenshot path if supervisor capture is unavailable.

Important acceptance nuance:
- removing the 404-class failure does not guarantee a good screenshot;
- blank screenshots after the 404 fix are a separate rendering/runtime issue.

## 2. Frontend regression pattern

A passed build did not prove runtime correctness.
The screen still had parent→child prop drift after cleanup.

Concrete examples from this session:
- `ThreadsModal` call site still used mismatched props;
- `AdminUserModal` call site used old prop names;
- `InteractionSetupModal` call site used old callback naming;
- parent passed `onToggleUserSelection` while `AdminUsersSection` expected `onToggleUser`.

Lesson:
- after UI cleanup, compare component signatures and call sites directly before assuming state logic is broken.

## 3. UX acceptance pattern

The user complaint was not “the API is wrong”.
It was:
- too much text;
- wrong panel shape;
- cramped file preview;
- broken task-screen/form behavior.

Lesson:
- after contract/API fixes, do a second pass dedicated only to visible UX acceptance.

## 4. File preview pattern

A generic modal width is often too small for profile-file preview.
Better pattern:
- modal width near viewport width, not generic narrow modal;
- image max-height tied to viewport height;
- preview stage with larger min/max height and `object-fit: contain`.

## 5. User workflow preference captured as skill guidance

For this class of issue, do not default to SSH-based investigation when the user is clearly pointing at a frontend surface and asking to fix the visible UI.
Start from live runtime/UI evidence and local code/bundle evidence first.
