# Mixed transport ticket-selection notes

Use this when the user asks to build a multi-city trip with fixed arrival/departure windows and wants "all possible variants" across flight and rail.

## Output pattern that worked

For each segment:
- date;
- departure/arrival time;
- duration;
- transport type;
- minimum visible price;
- hard constraint markers, for example "arrives too late", "train arrives next day", "no купе shown".

Then assemble 2–4 itinerary scenarios:
- convenience-first;
- lower-budget;
- balanced;
- fallback if the user needs a later/earlier return.

Always compute:
- price per person by segment;
- rough total for 2 people;
- whether the route satisfies the final arrival-date constraint literally.

## Practical rule for mixed city stays

If the user gives:
- a required final arrival date,
- a required number of days in one city,
- and a second city filling the rest,

then first derive the stay windows before listing tickets. Example frame:
- city A from start date to transfer date;
- city B for 3–4 days;
- return leg must land on the required final date.

## Important filtering lesson

Do not recommend trains from the final city if they arrive the day after the user's hard return date.
State them as technically available but ineligible.

Likewise, if the user says "поезд — не меньше купе", do not present seated/platskart-only options as primary candidates; keep them only as rejected or secondary notes.

## Yandex Rasp extraction pattern

When direct search results are weak, Yandex Rasp can still provide grounded options.

Working pattern:
1. open the route page in browser;
2. click the exact calendar date;
3. read `main.innerText` or `table.innerText` to capture:
   - flight/train number;
   - departure and arrival;
   - duration;
   - visible fare;
   - seat classes for trains.

Useful pages:
- `all-transport/<from>--<to>` for mixed mode;
- `plane/...` for flight-only clarity;
- `train/...` for seat class visibility.

## Presentation rule

For this class of task, keep the final answer practical:
- short recommendation first;
- then segment facts;
- then scenario comparison;
- then a clear "my recommended option".

Do not drown the user in every scraped row if a smaller decision-ready shortlist is enough.
