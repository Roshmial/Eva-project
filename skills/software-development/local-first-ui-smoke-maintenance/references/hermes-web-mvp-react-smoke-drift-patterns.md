# Hermes Web MVP React smoke drift patterns

Condensed notes from a real local-first acceptance pass.

## Durable lessons

### 1. Do not confuse UI drift with product failure
Observed drift examples:
- nav selector `Чаты` became ambiguous because both `Чаты` and `Все чаты` existed;
- composer placeholder changed from `Напишите сообщение для Hermes…` to `Напишите сообщение для текущего чата…`;
- profile file assertions had to open the `Файлы` tab instead of checking the profile summary screen;
- job status action label changed from `Поставить на паузу` to `Приостановить задачу`;
- create-user flow lived behind `Новый пользователь` modal flow, not inline fields.

Rule: after the first selector mismatch, stop blind retries and map the current UI contract from code/runtime.

### 2. Keep browser runtime work durable
If Chromium already launches through a repo helper like `scripts/browser_runtime_env.sh`, reuse that helper and stable user-space runtime roots instead of unpacking the same shared libraries into a new workspace directory every session.

### 3. Acceptance for file/open-link flows must verify the real route contract
In this case the frontend expected `/api/files/<id>/download`. The backend needed to expose that route and return `download_url` from file serialization. Acceptance should verify:
1. `/api/files` returns a real file with `download_url`;
2. the download route returns `200` and real file content;
3. frontend helpers do not double-prefix `/api` when backend already returns `/api/...`.

### 4. Separate smoke repair from product repair
- Smoke repair: update selectors, tabs, modal-entry points, and labels to match the current product.
- Product repair: add missing backend route, fix broken download flow, or correct runtime wiring.

Do not report smoke drift as app regression, and do not close product acceptance until the canonical or replacement smoke is green end-to-end.
