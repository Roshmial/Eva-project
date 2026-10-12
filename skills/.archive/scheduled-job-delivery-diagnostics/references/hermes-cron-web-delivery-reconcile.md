# Hermes cron output on time, Web delivery late after recipients refresh

Use this pattern when a user says a scheduled digest was "marked done at 09:30" but the visible message appeared much later, especially after editing recipients or opening the jobs screen.

## Symptom shape

- Hermes cron run starts on time.
- Output markdown/file appears on disk on time in `~/.hermes/cron/output/<job_id>/`.
- User-visible message in Hermes Web thread appears much later.
- The late appearance coincides with one of these actions:
  - recipients update,
  - opening `/api/jobs`,
  - opening a specific job,
  - manual job save/run.

## What it usually means

The scheduler is not the bottleneck. The missing link is autonomous reconcile/delivery from Hermes cron output into Hermes Web threads.

## Concrete diagnostic steps

1. Record cron start and finish time from Hermes logs.
2. Record output file mtime for the relevant `<job_id>`.
3. Record Web `messages.created_at` for the user/thread that eventually received the digest.
4. Record `job_recipients` / `hermes_job_recipients` rewrite time.
5. Inspect whether backend code calls `reconcile_hermes_job_delivery(...)` only from UI/API handlers or also from a background worker.

## Interpretation rule

If output file mtime is near the scheduled time, but Web delivery happens only after recipients refresh or jobs-screen/API access, classify the incident as:
- delivery-reconcile coupling bug,
not as:
- scheduler delay,
- slow LLM generation,
- Telegram delay.

## Preferred fix order

1. Immediate mitigation: run background reconcile inside the existing backend runtime.
2. Better long-term fix: trigger backend reconcile directly from cron completion (event-driven), so delivery uses the current recipients without depending on polling or UI/API side effects.

## Communication pattern

Good phrasing:
- "Cron отработал вовремя; задержка возникла не в генерации, а между готовым output и доставкой в Web-контур. Доставка зависела от позднего reconcile получателей."

Avoid saying:
- "cron опоздал"
when the file/output timestamp shows it finished on time.
