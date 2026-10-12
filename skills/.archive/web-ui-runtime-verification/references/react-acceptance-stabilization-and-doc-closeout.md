# React acceptance stabilization and doc close-out

When a long React/Playwright smoke is flaky but targeted live probes show the product flow is healthy, separate three layers explicitly:

1. Product defect
- backend route реально падает;
- write/read round-trip не проходит;
- list/detail расходятся по состоянию.

2. Smoke drift
- assertions завязаны на старые тексты, общий `innerText`, legacy selectors или `getByText(...)` без уникального маркера;
- automation пытается восстанавливать экран через `localStorage + reload`, хотя живой UI уже умеет обычную навигацию по tab-кнопкам.

3. Hardening tail
- основной flow уже зелёный;
- остаётся только профилактика: request token / stale-response guard, синхронизация smoke-селекторов с текущим UI, cleanup legacy runtime surfaces.

Practical stabilization pattern:
- сначала докажи backend-контракт прямым API и/или targeted probe;
- для React admin/jobs предпочитай реальные клики по текущим tab controls (`data-*`, active class) вместо restore-path через `localStorage`;
- жди structural invariant экрана, а не общий текст всей страницы;
- для modal-flow жди сам modal-container, а не косвенный текст где-то в `main`;
- после зелёного full smoke сразу обнови project backlog/docs: переведи тему из "незакрытый дефект" в "hardening tail", если это подтверждено реальными прогонами.

Recommended documentation close-out after successful stabilization:
- backlog: убрать формулировки вида "full acceptance ещё нужно довести";
- runbook/deploy guide: зафиксировать канонический smoke command и актуальные troubleshooting notes;
- decision log: записать, что defect закрыт и остались только hardening-хвосты.
