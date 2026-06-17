# Russia OS market dashboard evidence pattern

Use this reference when building a client-facing dashboard about the Russian operating-system market with only open-web sources and a strict structured payload.

## What worked

1. Split the problem into two evidence layers instead of forcing one false-precision table:
   - money / market-size layer: use open Russian industry sources such as TAdviser for market volume, growth, and segment mix;
   - usage-share layer: use open traffic-share sources such as StatCounter for device-usage orientation, then mark final combined shares as analytical estimates if exact exportable numbers are not openly extractable in-session.

2. Keep market-share meanings separate:
   - `доля рынка по выручке`;
   - `доля использования / usage share`;
   - `доля на ПК` vs `доля на всех устройствах`;
   - `рейтинг российских ОС` is not the same as market share.

3. For Russian OS competitive positioning, public CNews/ICT Moscow ranking pages are useful as a visible top-5 vendor/product layer when actual installed-base shares are not public.

## Concrete source pattern

- TAdviser `Операционные системы (рынок России)`:
  - public claims captured in the session:
    - Russian OS segment grew 37% to 12.5 bln RUB in 2024;
    - Windows share on the Russian computer market reached 87.6% at end-2024;
    - embedded OS market grew 21% to 9.58 bln RUB in 2024;
    - total Russian operating-system market grew 22% to 28.4 bln RUB in 2024.
- ICT Moscow summary of CNews 2025 ranking:
  - Astra Linux — 1.33k points;
  - Alt — 1.27k points;
  - Red OS — 1.18k points;
  - OSnova — 980 points;
  - Rosa — 979 points.
- GlobalCIO article:
  - useful for qualitative product landscape and characteristics of major Russian desktop/server OS vendors.
- StatCounter Russia pages:
  - use as authoritative open-web orientation for all-devices / mobile / desktop usage-share framing;
  - if live extraction of exact values is blocked, do not fabricate numbers from memory — either keep the section qualitative or provide clearly labeled analytical estimates.

## Dashboard-writing rule

When the user asks for a strict JSON dashboard:

- return only the JSON object;
- if exact usage-share numbers are not directly extractable, still build the dashboard but label the top-5 share table as `аналитическая оценка`;
- do not present ranking points, segment shares, and usage shares as if they were the same metric;
- add an explicit note when a card uses 2024 as the nearest public baseline for a 2025 market view.

## Good wording

Prefer formulations like:
- `ближайшая публичная база для оценки 2025`;
- `аналитическая оценка долей использования`;
- `не официальная единая таблица рынка, а сборка из открытых сегментных сигналов`;
- `использовать как ориентир, а не как бухгалтерскую долю выручки`.

## Pitfall

Do not collapse these three into one chart without a warning:
- Russian OS vendor ranking,
- Windows share on PCs,
- all-device OS usage share in Russia.

They answer different questions and mixing them creates false precision.