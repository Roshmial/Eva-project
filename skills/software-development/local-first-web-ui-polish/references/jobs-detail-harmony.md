# Jobs detail harmony patterns

Session pattern for Hermes Web MVP `Задачи` detail after functional fixes.

## When to apply

Use after the screen already works, but the detail panel still feels too technical, noisy, or admin-only.

## Stable lessons

1. Review the screen from two audiences at once:
   - operator/admin;
   - ordinary user who only needs to understand what the task is doing.

2. First-screen metrics should be limited to decision-relevant signals:
   - `Название`;
   - tech name;
   - `Источник`;
   - `Текущий статус`;
   - `Последний статус`;
   - `Следующий запуск`;
   - `Последний запуск`;
   - `Приватность`;
   - `Отдельные чаты задач`;
   - primary actions.

3. Remove from the first screen unless they clearly change user action:
   - owner;
   - role;
   - `своя задача`;
   - duplicated access blocks;
   - thin meta-card rows;
   - technical description/prompt text.

4. If `description` actually contains a working prompt or system instruction, do not show it in the detail view.
   Preferred path for this class of screen: remove it from the main detail entirely.

5. Human-facing naming matters.
   Prefer:
   - `Название`
   - `Сохранить название`
   over developer-facing copy like `Визуальное имя в этом браузере` or `Сохранить ярлык`.

6. After content cleanup, do a harmony pass:
   - uniform card radii, borders, and padding;
   - consistent section-title sizing;
   - consistent value-text sizing inside info cards and list rows;
   - avoid mixed status patterns (chip in one place, plain text in another, duplicate chip elsewhere);
   - remove duplicate status chips if `Текущий статус` is already shown as a primary metric.

7. A good target layout for jobs/detail:
   - identity block: name, tech name, source;
   - one compact metric grid for runtime status/schedule;
   - one consistent row of access/privacy cards;
   - history and parameters below as secondary sections.

## Runtime acceptance

Confirm in live UI that:
- technical description is gone;
- labels are human-facing;
- metric cards use the same typography family;
- duplicate status chips are removed;
- no JS errors appear in console.
