---
name: it-tender-csv-collection
description: Use when collecting a flat CSV of Russian IT tenders from public sources, starting with zakupki.gov.ru, with explicit unknowns and no invented fields.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [tenders, procurement, csv, research, public-data, russian-market]
    related_skills: [public-procurement-source-triage, scheduled-hermes-monitoring]
---

# IT Tender CSV Collection

## Overview

This skill captures a practical workflow for assembling a user-facing CSV with relevant IT tenders from public Russian procurement sources.

The primary working source is `zakupki.gov.ru`. Additional marketplaces may be checked later, but they should be included only if they are actually reachable and key fields are publicly retrievable from the current environment.

The output is a flat business-facing CSV where each row is one tender and every missing field is marked explicitly as `не указано`.

## When to Use

Use this skill when:
- the user asks to collect current IT tenders into a CSV;
- the expected format is a plain flat list of all found tenders, not a narrative digest;
- the user wants business fields like buyer, subject, dates, price, source, and source URL;
- the task may later become recurring and needs a repeatable procedure.

Do not use this skill when:
- the user wants legal interpretation of procurement rules;
- the user wants a full authenticated multi-market export pipeline;
- the task is source-feasibility triage only rather than actual collection.

## Required Output Format

Final CSV columns:
- `кто`
- `что`
- `сколько`
- `дата тендера`
- `дата подачи`
- `стоимость`
- `источник`
- `ссылка на источник`

Rules:
- one row = one tender;
- if a field is unavailable, write `не указано`;
- do not add technical commentary into the CSV;
- always keep the direct source URL;
- use a flat format suitable for later filtering and sorting.

## Baseline Source Strategy

Start with `zakupki.gov.ru` as the default source.

Reason:
- it is publicly reachable from the current environment;
- list pages and tender cards can be collected without introducing new infrastructure;
- it fits the local-first workflow.

At minimum, the next source to include is `B2B-Center`.

Current grounded status for `B2B-Center`:
- the public market/search pages were reachable from the current environment in live checks;
- keyword search via public query parameters appeared workable;
- it is reasonable to treat B2B-Center as the first expansion source after `zakupki.gov.ru`;
- however, include B2B rows in the final CSV only when the actual row fields and source URLs are verified in the same run.

Other sources such as Bidzaar, Roseltorg, and Fabrikant should still be added only after separate live verification. Do not claim they are included just because they were discussed earlier.

## Practical Collection Workflow

1. Fix the time window.
- If the user asks for today, filter by today's publication date.
- If the user asks for another period, keep the same schema and adjust only the date window.

2. Query `zakupki.gov.ru` with multiple IT-oriented search phrases.
Useful starting phrases:
- `разработка программного обеспечения`
- `сопровождение информационных систем`
- `техническая поддержка программного обеспечения`
- `внедрение информационных систем`
- `интеграция информационных систем`
- `информационная безопасность услуги`
- `цифровизация услуги`
- `оказание ИТ услуг`
- `аутсорсинг ит`
- `аутстаффинг ит`

3. Parse search cards into a normalized structure.
Minimum fields to extract from list pages:
- registry number;
- buyer if available;
- object/subject of procurement;
- publication date;
- submission deadline;
- public price if available;
- source URL.

4. Deduplicate by registry number.
If the same tender appears under several search phrases, keep one row.

5. Score relevance conservatively.
Prefer service-like IT tenders and down-rank hardware supply.

Useful positive markers:
- `разработ`
- `доработ`
- `сопровожден`
- `поддержк`
- `внедрен`
- `интеграц`
- `автоматизац`
- `цифров`
- `аутсорс`
- `аутстафф`

Useful negative markers:
- `поставка`
- `товар`
- `оборудован`
- `картридж`
- `мфу`
- `ноутбук`
- `монитор`
- `компьютер`
- `неисключительных прав`
- obvious license-only or supply-only wording

Important:
- do not pretend the filter is perfect;
- if a result is borderline, prefer honesty over forced inclusion.

6. Keep only relevant public results.
- exclude obvious hardware-only and supply-only rows;
- keep service, support, implementation, integration, maintenance, and IT operations tenders;
- if relevance is uncertain, mention that the dataset is a shortlist, not an official exhaustive register.

7. Try to enrich buyer from detail pages if the search card is incomplete.
- open the tender detail card by registry number;
- first try the explicit buyer field `Заказчик`;
- if `Заказчик` is absent, use `Организация, осуществляющая размещение` as the fallback buyer-like field;
- extract the value only if a clean organization name is actually found;
- if parsing returns page boilerplate or garbage text, discard that parse and keep `не указано`.

8. Add minimum B2B-Center expansion when needed.
- use B2B-Center as the first non-`zakupki.gov.ru` source to try;
- confirm that the search/list page is reachable in the current run;
- collect only publicly visible fields that map cleanly into the common CSV schema;
- if B2B does not expose a field publicly, write `не указано` rather than inferring it;
- tag every imported row with `источник = B2B-Center` and keep the direct public URL.

9. Write the final CSV.
- delimiter can be `;` for Russian spreadsheet compatibility;
- keep UTF-8 with BOM if the file is meant for Excel-friendly opening;
- verify a sample of the final rows after writing.

## Data Integrity Rules

Always separate:
- confirmed values;
- missing values;
- inferred relevance.

Never do the following:
- invent buyer names;
- convert unavailable price into zero;
- claim quantity when the card does not show it;
- describe an expected result as already collected if the source was not actually parsed.

## Known Limitations From Live Use

1. Search-card text may contain broken spacing inside Russian words.
This is a source parsing artifact. Do not silently claim the text was clean if it was not.

2. Buyer extraction from detail pages is unreliable in some cards.
If the parse captures footer text, legal boilerplate, or unrelated content, set buyer to `не указано`.

3. The field `сколько` is often absent in public tender cards.
Default to `не указано` unless quantity is clearly shown.

4. Public search results may surface adjacent categories such as certificates, licenses, or security-related services.
Treat them as included only if they still match the user's practical IT-services intent.

## Suggested User-Facing Framing

When delivering the file, keep the explanation short and factual:
- what period was covered;
- which source(s) actually made it into the file;
- that missing fields are marked as `не указано`;
- that the file is a working shortlist of relevant public tenders.

## If This Becomes Recurring

For one-off and future collection:
- keep the same CSV schema;
- keep the same query pack unless live results show drift;
- store output files with a date in the filename;
- keep `zakupki.gov.ru` as the base source and `B2B-Center` as the minimum second source;
- only add Bidzaar, Roseltorg, Fabrikant, or others after source-feasibility verification;
- prefer a local Python collector script under `~/.hermes/scripts/` with a config-driven source registry, so new sources can be added by enabling a new source block plus its collector function;
- write both a business CSV and a separate source-status CSV so zero-row or partially available sources do not pollute the main dataset;
- do not create a Hermes cron job unless the user explicitly asks for recurring execution;
- if scheduling is later requested for Moscow time on a UTC host, translate the cron expression explicitly instead of assuming local timezone.

See also `references/hermes-daily-pipeline-pattern.md` for the production shape validated in live use.

## Common Pitfalls

1. Mixing source-triage notes into the business CSV.
Keep blockers in the message or a separate note, not inside the tender rows.

2. Overstating completeness.
This workflow builds a practical shortlist from public results, not a guaranteed complete market-wide export.

3. Treating broken parser output as real buyer data.
If the extracted buyer looks like page navigation, footer text, or long legal wording, reject it.

4. Broadening the source set without live verification.
Do not say Fabrikant, B2B-Center, Roseltorg, or Bidzaar are in the final file unless they were actually parsed and verified in the same run.

5. Forcing a source into the main CSV when it returned zero usable rows.
If `B2B-Center` or another configured source is reachable but yields zero relevant public tenders for the target date, keep the business CSV clean and record that outcome in the status CSV instead of inventing placeholder rows.

6. Using an agent cron job when a deterministic script-only cron is enough.
If the workflow already has deterministic collection logic and the only delivery need is to send the CSV, prefer a Hermes `cronjob` with `no_agent=true` and make the script print the final delivery message plus `MEDIA:` path.

## Verification Checklist

- [ ] CSV has exactly the expected columns.
- [ ] Each row has a source and source URL.
- [ ] Missing values are marked as `не указано`.
- [ ] Duplicate tenders by registry number are removed.
- [ ] Obvious hardware-only rows are excluded.
- [ ] Buyer field is blanked to `не указано` if extraction is unreliable.
- [ ] Final user message does not overclaim coverage.
