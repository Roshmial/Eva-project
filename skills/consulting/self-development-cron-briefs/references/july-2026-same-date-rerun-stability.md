# Same-date rerun stability for daily briefs

Use this note when Misha asks to "доделать daily под ключ" and the job is being tuned through multiple manual reruns on the same morning.

## What went wrong before

A formally improved brief could still fail on three practical signals:
- weather line drifted across reruns for the same date;
- lines slid into task-manager phrasing (`ответы, календарь и мелкие дела`);
- travel context took over too many lines, even when only one travel reminder was useful.

## Durable correction

When rerunning the same date several times:
1. Pull the recent same-date outputs first, not only recent-history across days.
2. Reuse the cleanest same-date weather line by default.
3. Reject any candidate whose middle/support line reads like a category list or generic task bundle.
4. Count travel mentions explicitly. One mention is usually enough for a departure day.
5. Accept only after a short stable streak of good reruns, not one isolated lucky output.

## Examples of weak phrasing

Reject lines like:
- `ответы, календарь и мелкие дела`;
- `финальные правки и короткие задачи`;
- `спокойные дела во второй половине дня`.

These are grammatically fine but still sound generated and managerial.

## Better direction

Prefer lines with one clear human movement:
- one concrete work push;
- one natural walk/evening note;
- one bounded travel reminder.

The rhythm should feel like a real short Telegram message, not a tidy checklist.
