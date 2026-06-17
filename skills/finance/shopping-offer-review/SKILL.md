---
name: shopping-offer-review
description: Helps compare online store offers, estimate whether a price is too low or too high for the item, and identify the most reasonable purchase option.
version: 1.0.0
user_locked: true
tags: [shopping, pricing, comparison, e-commerce]
category: shopping
priority: 85
---

# Shopping Offer Review

## Purpose

Help the user choose the most reasonable online store offer for a product by comparing price, seller quality, condition, delivery terms, warranty, and market price range.

The goal is not to pick the cheapest listing automatically, but to identify the best value and flag offers that look suspiciously cheap or unjustifiably expensive.

## When to Use

Use this skill for:
- choosing between several online store offers;
- checking whether the current asking price is reasonable;
- identifying overpriced or suspiciously cheap offers;
- evaluating value-for-money before purchase;
- making safer purchase decisions in marketplaces and online shops.

## Procedure

1. Clarify the target item:
   - product category;
   - brand and model;
   - desired specs or configuration;
   - new / used / refurbished;
   - region or marketplace constraints.
2. Collect offers from multiple relevant stores or listings.
3. For each offer, extract:
   - item name;
   - store / seller;
   - listed price;
   - shipping cost;
   - availability;
   - warranty / return policy;
   - condition;
   - bundle / included accessories;
   - any visible warning signs.
4. Estimate the market price range by comparing:
   - same model offers;
   - similar configuration offers;
   - reputable seller offers;
   - historical or currently typical market pricing if available.
5. Classify each offer:
   - good value,
   - fair,
   - overpriced,
   - suspiciously cheap,
   - insufficient data.
6. Explain why a price may be too low:
   - wrong or incomplete listing;
   - hidden defects;
   - no warranty;
   - fake / gray import risk;
   - unreliable seller;
   - missing accessories;
   - scam indicators.
7. Explain why a price may be too high:
   - seller premium without meaningful benefit;
   - outdated model;
   - weak specs relative to alternatives;
   - unnecessary bundle markup;
   - low market competitiveness.
8. Produce the answer in this structure:
   - short conclusion;
   - market price range;
   - best-value options;
   - risky or overpriced options;
   - recommended pick;
   - what to verify before purchase.
9. When the comparison is based on live provider or store pages, include a direct link for every recommended option.
10. Separate confirmed facts from weaker signals:
   - mark characteristics as confirmed only when they were visible on the live page you checked;
   - if the page exposes only plan-family fragments, mixed pricing blocks, or partially structured text, label the specs as preliminary and say what still needs manual verification;
   - do not present inferred or reconstructed configuration details as fully verified.

## Rules

- Do not assume the cheapest option is the best.
- Do not evaluate price without considering condition, warranty, seller reputation, and delivery.
- If the market range is uncertain, say so explicitly.
- Flag suspiciously low prices as risk signals, not automatic wins.
- Prefer total purchase value over headline listing price.

## Evaluation Criteria

Assess offers by:
- effective total cost;
- trustworthiness of seller/store;
- condition and completeness;
- warranty and returns;
- market price sanity;
- performance/value fit for the intended use.

## Pitfalls

- Do not compare different configurations as if they were identical.
- Do not ignore shipping, taxes, duties, or hidden fees.
- Do not miss counterfeit or gray-market risk.
- Do not label something “overpriced” without relative comparison.
- Do not label something “great deal” when the data is weak.
- Do not omit direct product/provider links in user-facing comparisons when the next practical step is to inspect the offer.
- Do not blur the line between page-verified specs and inferred specs extracted from messy marketing text.

## Verification

Check that:
- offers are actually comparable;
- total cost is visible;
- price sanity is grounded in market comparison;
- suspiciously cheap offers are flagged with reasons;
- the final recommendation is practical and cautious.