from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo('Europe/Moscow')
OUT_ROOT = Path('/home/hermes/.hermes/cron/output/3c26e0954d43')

SOURCES = [
    ('МАММ', 'https://mamm-mdf.ru/exhibitions/'),
    ('ГЭС-2', 'https://ges-2.org/events/'),
    ('Пионер', 'https://pioner-cinema.ru/ru/afisha'),
    ('Garage / Summer Cinema by Garage', 'https://garageccc.com/ru/event'),
    ('Афиша Daily', 'https://daily.afisha.ru/afisha/'),
    ('KudaGo Москва', 'https://kudago.com/msk/'),
    ('Time Out Москва', 'https://www.timeout.ru/msk'),
    ('Яндекс Афиша Москва', 'https://afisha.yandex.ru/moscow'),
    ('Пушкинский музей', 'https://pushkinmuseum.art/events/'),
    ('Музей Москвы', 'https://mosmuseum.ru/events/'),
    ('Хлебозавод', 'https://hlebozavod9.ru/events/'),
    ('ДК Рассвет', 'https://dkrassvet.space/events'),
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


def main() -> None:
    now = datetime.now(TZ)
    week_start = now.date()
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
    for path in latest_outputs():
        text = path.read_text(encoding='utf-8', errors='ignore')
        titles = extract_titles(text)
        if not titles:
            continue
        any_titles = True
        print(f'[{path.name}]')
        for title in titles[:12]:
            print(f'- {title}')
    if not any_titles:
        print('(none)')


if __name__ == '__main__':
    main()
