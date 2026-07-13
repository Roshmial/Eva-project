---
name: russian-procurement-identification
description: Identify a specific Russian public/commercial procurement from fuzzy clues by triangulating EIS, price-request cards, marketplaces, and indexers.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Russian Procurement Identification

## Purpose

Use this skill when the user is not asking for a bulk tender collection, but wants to find one concrete procurement from partial or noisy clues: buyer, date window, tail of number, platform name, subject fragment, or remembered deadline.

Typical cases:
- "номер вроде заканчивается на 35"
- "Бауманка, CRM, конец июня"
- "кажется, это было на Roseltorg, но могло быть иначе"
- "найди точную карточку, а не подборку"

## Core rule

Do not force the user's clues into a single perfect match too early. Treat them as a noisy clue set. The job is to separate:
- confirmed facts;
- mismatches;
- plausible explanation of why the mismatches happened.

## Source order

Default order when the contour is unknown:

1. Official source first when possible.
   - EIS notice cards
   - EIS price-request cards (`/epz/pricereq/card/...`)
   - EIS organization pages only as support, not as primary proof

2. Public indexers second, to discover candidates when EIS search is noisy.
   - Kontur, Rostender, Synapse, Zakupki360, etc.
   - Use them to surface likely titles/numbers, then confirm back on EIS.

3. Marketplace cards third.
   - Roseltorg and similar ETPs are useful, but public visibility is often partial and anti-bot/auth may interfere.

### User-contour override

If the user explicitly says the story lived in a marketplace-specific corporate/commercial contour (`не ЕИС, а Roseltorg`, `корп.контур`, `это было на площадке`, `в коммерческих закупках`), treat that as an immediate source-order override.

Then the working order becomes:
1. marketplace-specific contour and direct marketplace cards;
2. public indexers and mirrors that expose that contour;
3. EIS only as a secondary reconciliation layer for adjacent traces, earlier stages, or mirrored fragments.

Do not continue broad EIS-first exploration after that override just because EIS is easier to search. If you still consult EIS, label it explicitly as a secondary cross-check rather than the primary contour.

## Investigation flow

### 1) Normalize the clue set
Split clues into classes:
- buyer / organization
- number or number tail
- dates: publication, deadline, end date, review date
- subject keywords
- platform memory
- procedure type memory

Explicitly mark which clues are exact versus fuzzy.

### 2) Check non-classic EIS paths early
If the user remembers a procurement but standard 44-FZ / 223-FZ notice search looks empty, check whether it is actually one of these:
- request for price information / monitoring of prices
- procurement planning artifact
- protocol / print form / contract card
- marketplace mirror of an EIS object

Do not assume "not in 44/223 search" means "not on EIS".

### 3) Use indexers to discover exact titles
When EIS search is too noisy, search quoted subject fragments and buyer name on public indexers.
Good pattern:
- discover likely number/title on indexer
- open official EIS card by registry number
- treat the EIS card as source of truth

### 3.1) For Moscow small-procurement traces, pivot to the marketplace mirror early
If the buyer is a Moscow public entity and the remembered subject looks like a small software renewal, license extension, or Portal Suppliers purchase, do not wait for EIS to confirm it.

Practical pattern:
- use an indexer snippet to surface a likely marketplace card on `market.mosreg.ru/Trade/ViewTrade/...` or a mirror such as `Zakupki360`;
- open the marketplace card directly;
- extract the concrete fields that are often visible there even when EIS search is unhelpful: buyer name, INN, trade number, registry number, status, subject, end-of-offers date, and price;
- treat that marketplace card as the primary confirmation if it explicitly says the procurement is conducted in AIS `Портал поставщиков` and shows the buyer identity.

This is especially useful for Moscow procurement stories where the user's memory may point to `СЦ 44`, `Портал поставщиков`, or a software license subject, while classic 44-ФЗ / 223-ФЗ search returns nothing relevant.

### 4) Manually probe neighboring buyer-specific numbers when clue memory is mixed
If the buyer code is stable and the user remembers only a number tail, inspect adjacent registry numbers for that buyer.
This is especially useful when two neighboring cards can plausibly be mixed in memory.

Practical pattern:
- probe a short sequential range around the suspected tail
- record `number -> date -> subject`
- compare the user memory against the neighboring objects

This often reveals that:
- the remembered number belongs to one procurement,
- while the remembered subject belongs to another nearby procurement.

### 5) Separate official confirmation from indexer-only hints
Use this wording discipline:
- "подтверждено по официальной карточке ЕИС"
- "видно по сниппету агрегатора, но не подтверждено на официальной карточке"
- "гипотеза: могли смешаться два соседних объекта"

### 6) Explain mismatches, do not just list them
Best final answers usually include one of these interpretations:
- user mixed two neighboring procurements;
- user remembered the marketplace or indexer mirror instead of the official card;
- user remembered a later stage date instead of publication date;
- the object was a request for price information, not a classic notice.

## User-facing answer shape

Recommended structure:

1. Short conclusion
   - "нашёлся сильный матч"
   - or "точного совпадения нет, но есть наиболее вероятный объект"

2. What is confirmed
   - number
   - buyer
   - title
   - official URL
   - type of card/procedure
   - dates actually visible on source

3. What did not match
   - number tail
   - date window
   - platform memory
   - wording fragment

4. Interpretation
   - why the mismatch is still consistent with the likely identification

5. Optional next step
   - check adjacent procedures
   - check later stage / mirror / marketplace version

## Date discipline

Users often say "дата подачи" when they actually mean one of several dates:
- publication date
- request-for-price submission window
- notice deadline
- commission / review date
- marketplace end date

Always identify which date type the source is actually showing.

## Marketplace / anti-bot discipline

If a public source is noisy or blocked, classify it precisely:
- public and confirmed
- public but noisy / low precision
- reachable but anti-bot or auth-limited
- unreachable from current environment

Do not say "nothing there" when the real issue is visibility or anti-bot.

## EIS number-range probing note

For buyer-specific investigations, sequential probing of neighboring EIS numbers is a valid method when search is poor and the clue set includes a stable buyer code plus a number tail. This is often faster and more reliable than broad keyword search.

See `references/bauman-path-inzhenera-case.md` for a concrete example where number-tail memory and subject memory came from adjacent Bauman procedures.
See `references/moscow-portal-suppliers-bitrix24-trace.md` for a marketplace-first reconstruction pattern in the Moscow `Портал поставщиков` contour, including year-mismatch handling.

## Pitfalls

- Treating every clue as exact.
- Stopping at 44-FZ / 223-FZ notice search and forgetting price-request cards.
- Presenting indexer snippets as if they were official confirmation.
- Failing to explain why a near-match is likely the right object anyway.
- Ignoring adjacent number probing when buyer and year are stable.

## Output standard

In Russian, concise, analytical, with explicit separation of:
- facts;
- mismatches;
- hypotheses;
- recommended next step.
