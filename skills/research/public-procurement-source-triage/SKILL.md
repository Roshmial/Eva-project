---
name: public-procurement-source-triage
description: Use when collecting or sanity-checking public tender/procurement sources, especially Russian marketplaces, and you need a grounded answer about what is publicly retrievable vs blocked by auth, anti-bot, or network access.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [procurement, tenders, source-triage, research, public-data]
    related_skills: [scheduled-hermes-monitoring, enterprise-vendor-research]
---

# Public Procurement Source Triage

## Overview

This skill is for fast, grounded reconnaissance of tender and procurement sources when the real question is not just “find records”, but “what can actually be collected from this environment today”.

It is especially useful for mixed-source Russian procurement work where some marketplaces expose public cards, some require login for export, some place price behind partial visibility, and some are blocked by captcha or network filtering.

The goal is to separate four states clearly:
1. data publicly retrievable now;
2. partially retrievable with important field gaps;
3. technically reachable but blocked by anti-bot/auth;
4. unreachable from the current environment.

## When to Use

- User asks to gather tenders from several marketplaces and compare what is available.
- You need a practical answer about source viability, not a theoretical one.
- You suspect different blockers per source: captcha, login wall, hidden price, timeout, regional/network filtering.
- You are preparing a recurring monitoring pipeline and need to test source feasibility first.

Do not use for:
- Legal interpretation of procurement rules.
- Deep parsing of one already-accessible source when source viability is no longer the question.
- Cases where the user already has a private API or authenticated export path and wants implementation directly.

## Working Output Shape

Always produce two layers of output:

1. User-facing summary
- what was collected;
- what was excluded;
- why it was excluded;
- what the final usable dataset actually contains.

2. Machine-usable files
- a clean final CSV with only usable records;
- a separate status file or note for excluded/problematic sources.

If the user asks to “убирай”, “подбивай”, “собери итог”, or similar, remove diagnostic/error rows from the final business-facing CSV and keep blockers only in a separate summary file.

## Recommended Triage Sequence

1. Start with source classification before broad scraping.
- Is the site reachable?
- Are list pages public?
- Are detail cards public?
- Are key fields public: buyer, subject, publish date, deadline, price, URL?

2. Verify retrieval at three levels.
- Root or landing page availability.
- Search/list page availability.
- At least one detail card availability.

3. Record the blocker precisely.
Use exact diagnoses like:
- `401 Unauthorized` on export endpoint;
- captcha / anti-bot challenge;
- HTTP 403 on entry page but public cards still reachable;
- TCP timeout before HTTP layer.

Do not collapse all failures into “source unavailable”.

4. Distinguish public-data quality from source reachability.
A source may be usable even if:
- price is not shown publicly;
- export requires login;
- root page is blocked but cards are public.

5. Only include confirmed records in the final dataset.
If you cannot verify a tender card or field, do not invent it. Mark the field as `не указано` or exclude the source from the final CSV.

## Source Assessment Matrix

For each source, decide one of these statuses:

- `собрано` — public data collected and card URLs verified.
- `частично доступно` — some public data confirmed, but export or some fields blocked.
- `не собрано: auth` — requires auth or export endpoint denies access.
- `не собрано: anti-bot` — captcha/challenge prevents practical collection.
- `не собрано: network` — connection timeout / TCP-level issue / DNS only.

Use the status in the diagnostics file, but keep the final user-facing CSV clean unless the user explicitly asks for diagnostic rows inline.

## CSV Rules

Preferred final columns for cross-source tender snapshots:
- `кто`
- `что`
- `сколько`
- `дата тендера`
- `дата подачи`
- `стоимость`
- `источник`
- `ссылка на источник`

Practical rules:
- Keep `источник` explicit for every row.
- Use `не указано` for missing structured fields.
- Use the marketplace URL as the source-of-truth link.
- Keep blocker/status commentary out of the final clean CSV unless asked.

## Handling Totals and “Подбить итог” Requests

When the user asks for a final tally:
- count only usable records in the final dataset;
- count records by source;
- separate “known public price” vs “price not публично показана”;
- if summing money, sum only confirmed numeric public values;
- state explicitly that the total is only for rows with known public price.

Good final summary shape:
- total usable rows;
- source split;
- number with known price;
- number without public price;
- sum of known public prices.

## Current Known Patterns

See `references/russian-marketplace-access-notes.md` for grounded source-specific notes discovered in live work.

## Common Pitfalls

1. Mixing diagnostic rows into the business-facing CSV.
If one source failed, keep that in a separate status file unless the user explicitly wants a combined audit sheet.

2. Treating export failure as source failure.
A source can still be usable through public cards even if CSV/XLS export requires login.

3. Reporting hidden prices as zero or guessing them.
If price is not public, say so directly.

4. Confusing root-page blocking with complete source blocking.
Sometimes the landing page returns 403 while search or card pages still work.

5. Saying “all additional sources collected” when only one source produced usable public records.
Be explicit about which sources actually made it into the final dataset.

## Verification Checklist

- [ ] Every final CSV row has a verified source URL.
- [ ] Excluded/problematic sources are moved to a separate status summary.
- [ ] Final record count excludes failed-source placeholder rows.
- [ ] Monetary total includes only rows with confirmed public values.
- [ ] Final user message says what was removed and what remained.
