from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo('Europe/Moscow')
OUT_ROOT = Path('/home/hermes/.hermes/cron/output/3c26e0954d43')

SOURCES = [
    ('Городские сезонные программы', 'https://leto.mos.ru/'),
    ('ВДНХ события', 'https://vdnh.ru/events/'),
    ('МАММ', 'https://mamm-mdf.ru/exhibitions/'),
    ('ГЭС-2', 'https://ges-2.org/events/'),
    ('Пионер', 'https://pioner-cinema.ru/ru/afisha'),
    ('Garage / Summer Cinema by Garage', 'https://garageccc.com/ru/event'),
    ('Пушкинский музей', 'https://pushkinmuseum.art/events/'),
    ('Музей Москвы', 'https://mosmuseum.ru/events/'),
    ('Хлебозавод', 'https://hlebozavod9.ru/events/'),
    ('ДК Рассвет', 'https://dkrassvet.space/events'),
    ('Афиша Daily', 'https://daily.afisha.ru/afisha/'),
    ('KudaGo Москва', 'https://kudago.com/msk/'),
    ('Time Out Москва', 'https://www.timeout.ru/msk'),
    ('Яндекс Афиша Москва', 'https://afisha.yandex.ru/moscow'),
]


def latest_outputs(limit: int = 3) -> list[Path]:
    files = sorted(OUT_ROOT.glob('*.md'))
    return files[-limit:]


def extract_titles(text: str) -> list[str]:
    titles = []
    for line in text.splitlines():
        m = re.match(r'^\d+\.\s+[^—]+—\s+(.+)$', line.strip())
        if m:
            titles.append(m.group(1).strip())
    return titles


def extract_places(text: str) -> list[str]:
    places = []
    for line in text.splitlines():
        if line.startswith('Где: '):
            places.append(line.removeprefix('Где: ').strip())
    return places


def extract_links(text: str) -> list[str]:
    links = []
    for line in text.splitlines():
        if line.startswith('Ссылка: '):
            links.append(line.removeprefix('Ссылка: ').strip())
    return links


def domain_of(url: str) -> str:
    m = re.match(r'^https?://([^/]+)', url)
    return m.group(1).lower() if m else url


def main() -> None:
    now = datetime.now(TZ)
    week_start = now.date() - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)
    print('WEEK_CONTEXT')
    print(f'moscow_now: {now:%Y-%m-%d %H:%M}')
    print(f'week_start: {week_start.isoformat()}')
    print(f'week_end: {week_end.isoformat()}')
    print('source_clusters:')
    for name, url in SOURCES:
        print(f'- {name}: {url}')
    print('\nRECENT_WEEKLY_OUTPUT_TITLES')
    any_titles = False
    place_counter: dict[str, int] = {}
    domain_counter: dict[str, int] = {}
    for path in latest_outputs():
        text = path.read_text(encoding='utf-8', errors='ignore')
        titles = extract_titles(text)
        for place in extract_places(text):
            place_counter[place] = place_counter.get(place, 0) + 1
        for link in extract_links(text):
            domain = domain_of(link)
            domain_counter[domain] = domain_counter.get(domain, 0) + 1
        if not titles:
            continue
        any_titles = True
        print(f'[{path.name}]')
        for title in titles[:12]:
            print(f'- {title}')
    if not any_titles:
        print('(none)')
    print('\nRECENT_PLACE_BIAS')
    if place_counter:
        for place, count in sorted(place_counter.items(), key=lambda x: (-x[1], x[0]))[:8]:
            print(f'- {place}: {count}')
    else:
        print('(none)')
    print('\nRECENT_DOMAIN_BIAS')
    if domain_counter:
        for domain, count in sorted(domain_counter.items(), key=lambda x: (-x[1], x[0]))[:8]:
            print(f'- {domain}: {count}')
    else:
        print('(none)')


if __name__ == '__main__':
    main()
