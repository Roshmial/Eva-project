# Bauman corporate procurement reconstruction notes

Use these notes when a user remembers a procurement only by partial signs and says the real story was in a corporate/commercial contour.

## Durable patterns from live work

### 1. Mixed-memory pattern is common
A user may combine attributes from multiple adjacent procedures:
- number suffix from one card;
- subject from another;
- dates from a later or mirrored stage;
- budget from the corporate procedure while the visible EIS trace has no public amount.

Do not force one card to satisfy every remembered field.

### 2. EIS can show only adjacent traces
For one buyer, EIS may show request-for-price cards or neighboring public artifacts, while the main business-relevant process lives in the corporate marketplace layer.

Treat EIS as:
- confirmation of buyer/theme/date windows;
- a source of neighboring identifiers;
- not always the final source of the target procedure.

### 3. Corporate marketplace search can be weaker than direct-card access
Observed pattern on hostile marketplaces:
- search UX is poor or blocked;
- browser can show an anti-bot block page on the root/search entry;
- direct procedure cards may still open when the identifier is already known.

Therefore the fallback sequence is:
1. confirm blocking state once;
2. stop brute-retrying browser search;
3. pivot to direct-card probing plus external indexers and mirrors.

### 4. Strong-but-imperfect match reporting
When you find a candidate that matches buyer and subject but not dates or amount, report it like this:
- confirmed: buyer, subject, procedure family;
- mismatch: dates / amount / suffix;
- interpretation: likely adjacent or earlier-stage trace, not yet proven as the exact target.

## Useful phrasing
- "Похоже, у вас смешались как минимум два соседних объекта."
- "По ЕИС виден сильный тематический след, но основной корпоративный контур мог жить отдельно на площадке."
- "Чистого номера нет, поэтому ищем не точное совпадение, а набор признаков и затем отсеиваем ложные следы."
