# Runtime source verification before UI polish

Use this when code changes in `services/frontend/*` do not appear in the live browser even after reload.

## Durable lesson
Before spending another polish pass on layout, verify that the running app is actually serving the frontend files you are editing.

## Fast verification pattern
1. In the live browser, check for a newly added DOM marker, input id, or CSS class that should definitely exist after your edit.
2. Compare that against the local edited file.
3. If the browser still shows the old DOM while console is clean, assume a source mismatch before assuming the patch failed.

## Good probe examples
- `document.getElementById('jobSearchInput')`
- `document.querySelector('.chat-welcome-shell.compact')`
- loaded script URLs with cache-busting query params

## Interpretation rule
If:
- JS console has no errors,
- reload succeeds,
- but expected DOM markers are missing,

then the likely issue is one of:
- backend serves a different `index.html` / `app.js` than the edited files,
- build output is coming from another directory,
- a stale runtime instance is serving an older asset set.

## What to do next
Stop cosmetic polishing and first trace the actual served frontend source. Otherwise you risk improving the wrong files and creating only the illusion of progress.
