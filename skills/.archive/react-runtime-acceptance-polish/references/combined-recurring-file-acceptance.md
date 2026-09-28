# Combined recurring/file acceptance pattern

Use this reference when a chat/job/recurring result arrives as a combined payload: short assistant summary plus one or more attached files.

## Risk pattern

A green backend contract and a green frontend build can still leave the live UI wrong:
- service-grid metadata is shown instead of a product card;
- the same file is rendered twice (special result block + plain attachment list);
- bubble text is intentionally suppressed, but the renderer still shows a placeholder like `…`;
- the live port still serves an older JS asset, so the code fix is not actually in the runtime.

## Minimal acceptance recipe

1. Confirm the live contour and the exact frontend/backend ports.
2. Confirm the affected payload shape through the live API, not just DB inspection.
3. Rebuild the frontend and verify which asset hash the live HTML now serves.
4. Check for renderer markers in the served JS bundle, not only in source files.
5. If browser automation is partially blocked, use a temporary seeded acceptance thread/message that reproduces the exact payload shape.
6. After verification, delete the temporary thread/message so the runtime stays clean.
7. Record in decision-log whether the verification was full browser-pass or constrained fallback acceptance.

## What good UI looks like

For recurring/job delivery with attachments, default rendering should be one compact result card:
- short summary;
- status;
- optional delivery note;
- one file list with primary action;
- details/preview only behind an explicit expand action.

Default UI should NOT show:
- duplicated plain attachment list under the same result;
- empty bubble placeholder when display text is intentionally suppressed;
- technical contract grid (`reason`, `result kind`, `delivery`) as the main user-facing layout.
