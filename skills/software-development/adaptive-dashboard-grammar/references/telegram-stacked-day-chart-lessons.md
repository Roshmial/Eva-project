# Telegram stacked day chart lessons

Session lesson for Hermes Web dashboard rendering.

What the user actually wanted:
- one combined visual object;
- X axis = dates;
- Y axis = message count;
- each date column internally split by message types as a stacked composition.

What was wrong in the earlier attempt:
- grouped/day-by-day rendering behaved like several separate objects instead of one chart;
- extra sections such as overall day timeline and overall type structure duplicated the same information;
- non-top message types risked disappearing instead of preserving daily totals.

Durable implementation pattern:
- backend emits one `bar_list` section for the whole period;
- each item carries `meta: series=<type>; total_day=<n>; raw_day=<YYYY-MM-DD>`;
- frontend regroups by day and renders one stacked multi-column chart;
- top-N types stay explicit, everything else is aggregated into `прочее`.

When to apply:
- Telegram digest analytics;
- any period dashboard with daily buckets and categorical split inside each bucket;
- any user phrasing like "по оси горизонтальной даты, по оси вертикальной количество, внутри дня по типам".
