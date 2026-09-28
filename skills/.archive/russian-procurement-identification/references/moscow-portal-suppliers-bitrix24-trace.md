# Moscow Portal Suppliers / marketplace-mirror trace pattern

Use this note when a user remembers a Moscow public procurement with a software-license subject, but classic EIS search does not yield a clean match.

## Observed reconstruction pattern

A practical reconstruction path was confirmed on the `ГБУ "СЦ 44" + Битрикс24` case:

1. A web-search indexer snippet exposed a likely mirror card.
2. The mirror pointed to `market.mosreg.ru/Trade/ViewTrade/...`.
3. The marketplace card explicitly stated that the purchase was conducted in AIS `Портал поставщиков` of Moscow.
4. The card exposed enough structured fields to identify the likely procurement even without a clean EIS card in hand.

## Fields that were publicly visible on the marketplace card

- buyer full name;
- buyer INN;
- marketplace trade number;
- registry number;
- procurement subject;
- end-of-offers datetime;
- planned contract date;
- status;
- price (МЦК).

## Working rule

If the card explicitly ties the procurement to `Портал поставщиков` and the buyer/subject match strongly, you can present it as a strong confirmed marketplace match even if:
- the remembered year is off;
- EIS confirmation is still missing;
- the public mirror is the most accessible source from the current environment.

## Reporting rule

In the final answer, separate:
- what the marketplace card confirms;
- what does not match the user's memory, especially year/date;
- whether the mismatch most likely means a memory shift rather than a wrong object.

Do not silently convert a 2021 marketplace card into a "2020 tender found" claim.
