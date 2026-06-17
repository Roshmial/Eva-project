# Dashboard result UX for Hermes Web chat-first

Use this when accepting or polishing `dashboard_result` responses inside Hermes Web.

Key lesson from live review:
- KPI cards alone are not enough; the result reads as a stub rather than a dashboard.
- In chat, pseudo-accordion / collapsed sections are bad UX if they are not fully interactive and obviously clickable.
- If a section is important, its content must be visible immediately without extra clicks.

Practical rules:
1. Push the backend prompt to request typed visual sections, not just free-text blocks.
2. Prefer at least two visible visual sections when there are quantitative slices: `bar_list`, `pie_list`, `bubble_list`.
3. Always support a plain visible text renderer for narrative sections (`text_list`) so the UI never degrades to title-only cards.
4. Reject chat renderers that visually imply hidden interactivity unless that interaction is implemented and acceptance-tested.
5. During acceptance, do not stop at `200 OK`; verify the actual message composition and whether the dashboard reads as a finished artifact.

Acceptance checklist:
- more than KPI cards when numbers exist;
- at least one ranking/comparison visual;
- narrative sections render as visible text, not empty headers;
- no fake clickable sections;
- dashboard feels complete inside chat.
