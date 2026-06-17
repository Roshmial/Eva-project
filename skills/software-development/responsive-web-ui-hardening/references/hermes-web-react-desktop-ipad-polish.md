# Hermes Web React desktop/iPad polish notes

When doing a final UI pass for this class of local-first React admin/chat surfaces, check these specific pitfalls:

- Do not leave raw MIME strings in end-user file lists when they add no decision value. Long values like `application/vnd.openxmlformats-officedocument.wordprocessingml.document` read as noise.
- In `Files` popovers and profile file lists, prefer only user-meaningful metadata: file name, size, date, processing status, and explicit open/select actions.
- Remove duplicate helper copy when the section structure already explains itself. Typical examples:
  - duplicate subheadings repeating the tab name;
  - helper text like "you can use previously uploaded files" when the selector already makes that obvious.
- Treat visual consistency of navigation as a shared control system problem, not as isolated button tweaks. `nav`, `ghost`, and logout/admin utility buttons should share the same base shape, hover behavior, and active-state language.
- For iPad Pro 11" / tablet-desktop overlap, add an intermediate breakpoint above the phone layer. A phone-only breakpoint often leaves two-column admin/profile layouts feeling cramped on tablets.
- If an admin chart "looks like it does not render", verify whether the JSX exists but the chart classes have no CSS. A missing layout/height/grid definition can make a real chart appear invisible.
- For light-weight custom charts built from `div` bars:
  - give the chart container explicit min-height;
  - define column/grid structure for bars;
  - align bars to bottom;
  - add a visible legend;
  - verify tablet breakpoints so the chart does not collapse awkwardly.

Verification pattern:

- Rebuild production assets.
- Restart the local frontend service.
- Confirm the served HTML references the new JS/CSS bundle names.
- If browser verification is blocked by auth, state that clearly: runtime delivery is verified, but authenticated visual acceptance still needs a user-level check.
