# CopilotKit integration in a damaged cloned preview lane

Use when an isolated sibling copy of the web app was created for CopilotKit work and the copy turns out to be mechanically damaged before functional debugging even starts.

## Typical symptoms

- copied source files contain line-number prefixes like `1|...` or `17|17|...`;
- large files are truncated mid-component or mid-handler;
- React build fails with misleading parser errors far from the real issue;
- CSS build warns about unbalanced `{` because the file tail was cut;
- backend smoke fails because the copied backend file is incomplete, not because the CopilotKit patch itself is wrong.

## Reliable recovery sequence

1. Audit the copied lane before debugging CopilotKit logic.
- Check the exact files you touched first: `services/backend/app.py`, `services/backend/test_smoke.py`, `services/frontend-react/src/App.jsx`, `services/frontend-react/src/styles.css` or equivalents.
- If you see prefixed line numbers, strip them first.
- If a file is truncated, do not hand-reconstruct large missing tails from memory.

2. Restore from the nearest canonical sibling copy.
- Use the healthy neighboring repo copy as the source of truth.
- Replace the damaged full file first.
- Then re-apply only the intentional CopilotKit/dashboard changes as small targeted patches.

3. Re-verify project entrypoints before blaming the code.
- In split React layouts, `src/` may live under `services/frontend-react/` while `package.json` and `vite.config.*` live at repo root.
- Run the actual repo build script from the directory that owns `package.json`.
- For Python smoke, honor repo-specific import assumptions such as `PYTHONPATH=services/backend` when required by the project.

4. Rebuild in the right order.
- backend smoke first, so route/serializer regressions are caught before UI noise;
- frontend production build second;
- live browser/runtime flow only after both are green.

## Practical lesson

In cloned preview lanes, apparent CopilotKit/runtime defects may actually be file-copy corruption. Treat structural file integrity as a prerequisite check, not as a side note.
