# React controlled state + live runtime verification

Use when a live UI bug involves a mode selector, composer option, or request policy control that affects submit behavior.

## Durable recipe

1. Localize the control owner and the submit owner.
   - If the control is rendered in a child but submit happens in a parent, the state usually belongs in the parent or another common owner.
2. Convert the control to a controlled component.
   - `value={state}` + `onChange={setState}`.
3. Remove direct DOM reads from the submit path.
   - Build request policy from React state instead of `document.getElementById(...).value`.
4. If there is server/bootstrap policy, sync it into the owner state deliberately.
   - Typical triggers: active thread change, bootstrap policy refresh.
5. Rebuild with the project's canonical frontend build command.
6. Restart the exact live frontend service/unit.
7. Verify the target port serves the new code markers.
   - Search for parent-level `useState(...)`, child prop names, and submit-path usage of the same state variable.

## Example symptom progression

- original bug: selected mode resets after rerender;
- partial fix: child gets local `useState(...)`;
- regression: parent submit handler references the child-local variable and throws `... is not defined`;
- final fix: lift state to the parent, pass it into the child, and use the same state in request construction.

## What to prove before closing

- mode selection persists across rerender;
- submit path uses the selected mode;
- target runtime serves the updated code after rebuild/restart;
- no stale served source on the live port.
