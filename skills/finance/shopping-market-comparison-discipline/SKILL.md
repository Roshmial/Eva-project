---
name: shopping-market-comparison-discipline
description: "Use when comparing the same product across stores."
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Shopping Market Comparison Discipline

## Purpose

This skill governs live price-comparison tasks where the user wants the same product checked across several stores or marketplaces.

The main goal is to avoid drifting from the exact item requested into nearby variants, adjacent pack sizes, or flavor mixes unless the user explicitly asks for substitutes.

## When to use

Use this skill when the user asks to:
- find the same product in other stores;
- compare marketplace prices for one exact listing;
- check whether a current store price is good relative to the market;
- search pet-store chains, marketplaces, or retailer sites for a specific SKU-like item.

## Core rule

Start with exact-match discipline.

Before comparing prices, lock these fields from the user's source page when visible:
- brand;
- product line;
- product type;
- flavor mix;
- pack count;
- unit weight/volume;
- any visible article/SKU if present.

If one of these fields changes, treat the result as analog or nearby variant, not as the same item.

## Required workflow

1. Read the source item first.
   - Confirm what the original product actually is.
   - Extract the exact title and package size.
   - Watch for hidden traps like the source being 40 pcs, while search results surface many 26 pcs offers.

2. Search for the same item across marketplaces and chain pet stores.
   - Prefer exact title fragments.
   - Prefer the same pack count and same flavor combination.
   - Check official stores, marketplaces, and pet-retail chains separately.

3. Separate findings into three buckets.
   - exact match;
   - same line but different pack size;
   - same line but different flavor/composition.

4. Present exact matches first.
   - If no exact match is confirmed, say so directly.
   - Only then mention nearby variants as fallback context.

5. Mark evidence quality.
   - confirmed live page;
   - confirmed by snippet/search result only;
   - blocked by captcha / 403 / anti-bot.

## User-facing output shape

Default structure:
- direct conclusion;
- exact matches with prices and links;
- blocked / unconfirmed stores;
- nearby variants only if exact matches are missing or scarce.

## Pitfalls

- Pitfall: drifting from the exact requested item to close-enough analogs too early.
  Fix: keep exact-match discipline until the answer is exhausted.

- Pitfall: comparing 26 pcs and 40 pcs as if they were the same product.
  Fix: separate exact match from equivalent-price math. If you normalize by per-unit price, label it explicitly as normalization, not as the same listing.

- Pitfall: presenting a price from a blocked card as fully verified.
  Fix: label snippet-only or blocked-card prices as partially confirmed.

- Pitfall: when the user asked for the same item, leading with near analogs from the same brand/line.
  Fix: exact item first, analogs second.

## Support files

- `references/exact-match-vs-analog-market-comparison.md` — compact notes and examples from live shopping comparison sessions.
