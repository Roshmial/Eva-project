# Fallback sources and comparison notes for road-trip vacation planning

## Purpose
Compact notes for cases where the user wants accommodation shortlists and route comparison, but the preferred booking platform cannot be fully validated in-session.

## Accommodation source fallback order
1. Requested platform.
2. Alternative aggregator with visible object pages or structured listing data.
3. Official property page.
4. Search snippet only as a lead for manual follow-up.

## How to label evidence in the answer
Use short labels directly in the shortlist:
- `подтверждено на Ostrovok` — object and score visible there.
- `подтверждено существование объекта` — object page/listing found, but score not safely extracted.
- `нужна финальная проверка на даты` — availability, current price, or seasonal access not verified.
- `источник рейтинга не Яндекс` — when the user originally asked for Yandex but a fallback source was used.

## Practical pattern that worked
- Use a routing tool to confirm drive times between base and side trips.
- Use accommodation aggregators as a shortlist source, not as a substitute for honest uncertainty handling.
- If the user corrects the geography or names a more meaningful base, reframe around that base instead of defending the original generic option.

## Comparison frame for two destination regions
For each region, explicitly score in prose:
- what is the anchor attraction,
- whether there are 2-4 good supporting day trips,
- whether accommodation supply matches the requested style,
- whether the trip feels like a calm base vacation or a moving route vacation.

## Example from northern Russia class of trips
A region can win on beauty of accommodation but lose on route burden.
Another region can win on breadth of day trips but feel thinner as a final retreat.
Say this directly instead of forcing one universal winner.
