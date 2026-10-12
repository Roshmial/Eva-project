# Trip-day style and real-city weather

Lessons from the July 2026 daily-brief tuning loop.

## What broke

A trip-day brief can still fail badly even when the structure looks correct.
Common failure pattern:
- weather is still given for Moscow by inertia;
- the city of the day is known in structured context, but the draft ignores it;
- the copy shifts into postcard / travel-editor mode;
- the text sounds polished and literary instead of like a short Telegram message.

## Hard rules

1. Weather follows the real city of the day.
- If structured context for the date has `city`, use that city for the weather line.
- Moscow is fallback only when the day context does not specify another place.

2. Trip-day copy must stay practical.
Prefer:
- where to go in the morning;
- what to avoid carrying or doing in the heat;
- what is realistically enough for the evening.

3. Reject postcard phrasing even if it sounds smooth.
Treat lines like these as hard failures:
- `город лучше брать без гонки`
- `правильный ритм`
- `кофе с видом на воду`
- `зайти в город с одной сильной точки`
- `сегодняшний выигрыш прост`
- `можно оставить себе`
- close variants with the same travel-editor feel

4. Reject synthetic glue words.
These often make the text sound generated:
- `есть смысл`
- `разумно`
- `пригодится`
- `терпимый`
- `лучший режим`
- `можно спокойно`

5. Slight live roughness is better than polished symmetry.
A line like `после часа там уже печка` can land better than a smoother but more artificial sentence.

## Acceptance signal

A good trip-day brief should read like a familiar person sending a short practical note from the phone, not like a travel caption, mini-itinerary, or editorial lifestyle digest.
