from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import re
import requests
import yaml

TZ = ZoneInfo('Europe/Moscow')
DAILY_OUT = Path('/home/hermes/.hermes/cron/output/329913efa98a')
CTX_PATH = Path('/home/hermes/workspace/eva-digest-context.yaml')
PROMPT_PATH = Path('/home/hermes/workspace/eva-daily-v4.md')
WEATHER_URL = 'https://pogoda.mail.ru/prognoz/moskva/'

MAIN_ITEMS = [
    {
        'id': 'makers-schedule',
        'category': 'article',
        'text': 'Я бы сегодня открыла [Maker\'s Schedule, Manager\'s Schedule]({url}) и просто прочитала его целиком',
        'label': 'Maker\'s Schedule, Manager\'s Schedule',
        'url': 'https://paulgraham.com/makersschedule.html',
    },
    {
        'id': 'bitter-lesson',
        'category': 'article',
        'text': 'Я бы сегодня прочитала [The Bitter Lesson]({url}) и посмотрела, что из него у тебя всё ещё цепляет',
        'label': 'The Bitter Lesson',
        'url': 'http://www.incompleteideas.net/IncIdeas/BitterLesson.html',
    },
    {
        'id': 'delete-code',
        'category': 'article',
        'text': 'Я бы сегодня прочитала [Write code that is easy to delete, not easy to extend]({url}) и примерила его к своим текущим штукам',
        'label': 'Write code that is easy to delete, not easy to extend',
        'url': 'https://programmingisterrible.com/post/139222674273/how-to-write-disposable-code-in-large-systems',
    },
    {
        'id': 'karpathy-ai-software',
        'category': 'video',
        'text': 'Я бы сегодня посмотрела [Software Is Changing (Again)]({url}) и по ходу пометила пару мест, к которым захочется вернуться',
        'label': 'Software Is Changing (Again)',
        'url': 'https://www.youtube.com/watch?v=LCEmiRjPEtQ',
    },
    {
        'id': '12factor',
        'category': 'article',
        'text': 'Я бы сегодня перечитала [The Twelve-Factor App]({url}) и сверила, что из этого у тебя до сих пор живое',
        'label': 'The Twelve-Factor App',
        'url': 'https://12factor.net/',
    },
    {
        'id': 'sicp-preface',
        'category': 'book',
        'text': 'Я бы сегодня открыла [предисловие SICP]({url}) и просто посидела с ним',
        'label': 'предисловие SICP',
        'url': 'https://sarabander.github.io/sicp/html/Preface.xhtml',
    },
]

SMALL_ITEMS = [
    {
        'id': 'neck-shoulders',
        'category': 'practice',
        'text': 'Можно потом сделать [разминку для шеи и плеч]({url})',
        'label': 'разминку для шеи и плеч',
        'url': 'https://www.youtube.com/watch?v=r3fBXr8gVNI',
    },
    {
        'id': 'townscaper',
        'category': 'game',
        'text': 'На вечер можно открыть [Townscaper]({url}) минут на десять',
        'label': 'Townscaper',
        'url': 'https://store.steampowered.com/app/1291340/Townscaper/',
    },
    {
        'id': 'music-brian-eno',
        'category': 'music',
        'text': 'На вечер можно включить [Brian Eno]({url})',
        'label': 'Brian Eno',
        'url': 'https://music.youtube.com/watch?v=jl_z5JvrKlc&list=OLAK5uy_l4zX5bN7f7r6bZ1tY-ambient',
    },
    {
        'id': 'short-walk-vdnh',
        'category': 'walk',
        'text': 'Если дождь не начнётся раньше, можно дойти до [ВДНХ]({url})',
        'label': 'ВДНХ',
        'url': 'https://www.google.com/maps/dir/55.850568,37.602219/55.829651,37.633257/',
    },
    {
        'id': 'article-paul-graham-do-things',
        'category': 'article',
        'text': 'Можно потом открыть [Do Things that Don\'t Scale]({url})',
        'label': 'Do Things that Don\'t Scale',
        'url': 'https://paulgraham.com/ds.html',
    },
    {
        'id': 'cleanup-15-things',
        'category': 'cleanup',
        'text': 'Можно спокойно разобрать стол, полку или ящик; если понадобится, вот [метод]({url})',
        'label': 'метод',
        'url': 'https://www.apartmenttherapy.com/decluttering-tips-36631032',
    },
    {
        'id': 'pomodoro-video',
        'category': 'video',
        'text': 'Можно посмотреть короткий разбор про [Pomodoro]({url}) и просто проверить, хочется ли тебе так работать',
        'label': 'Pomodoro',
        'url': 'https://www.youtube.com/watch?v=mNBmG24djoY',
    },
    {
        'id': 'music-nils-frahm',
        'category': 'music',
        'text': 'На вечер можно включить [Nils Frahm]({url})',
        'label': 'Nils Frahm',
        'url': 'https://music.youtube.com/watch?v=HPPzQgTaLbo&list=OLAK5uy_nilsfrahm',
    },
]


def extract_response(text: str) -> str:
    marker = '## Response\n\n'
    idx = text.rfind(marker)
    if idx == -1:
        return text.strip()
    return text[idx + len(marker):].strip()


def recent_final_texts(limit: int = 14) -> list[str]:
    files = sorted(DAILY_OUT.glob('*.md'))[-limit:]
    return [extract_response(p.read_text(encoding='utf-8', errors='ignore')) for p in files]


def used_recent_ids(items: list[dict], recent_texts: list[str]) -> set[str]:
    used = set()
    haystack = '\n'.join(recent_texts).lower()
    for item in items:
        if item['id'].replace('-', ' ') in haystack:
            used.add(item['id'])
            continue
        key = re.sub(r'[^a-z0-9а-яё ]+', ' ', item['text'].lower())
        tokens = [t for t in key.split() if len(t) > 4][:4]
        if tokens and all(tok in haystack for tok in tokens[:2]):
            used.add(item['id'])
    return used


def used_recent_categories(items: list[dict], recent_ids: set[str]) -> set[str]:
    return {item['category'] for item in items if item['id'] in recent_ids}


def pick_item(items: list[dict], used_ids: set[str], day_seed: int) -> dict:
    fresh = [x for x in items if x['id'] not in used_ids]
    pool = fresh or items
    return pool[day_seed % len(pool)]


def find_event(day: str) -> dict | None:
    if not CTX_PATH.exists():
        return None
    data = yaml.safe_load(CTX_PATH.read_text(encoding='utf-8')) or {}
    for item in data.get('events', []):
        if str(item.get('date')) == day:
            return item
    return None


def fetch_weather_summary() -> dict:
    headers = {'User-Agent': 'Mozilla/5.0'}
    html = requests.get(WEATHER_URL, timeout=20, headers=headers).text

    current_match = re.search(r'В Москве \([^)]*\) \+?(\d+)&deg;C, ([^"<]+)', html)
    current_temp = int(current_match.group(1)) if current_match else None
    current_text = current_match.group(2).strip() if current_match else ''

    hour_pattern = re.compile(r'ForecastHourItem.*?<div[^>]*>(\d{2}:\d{2})</div>.*?svg/(\d+)\.svg.*?<div[^>]*>\+?(\d+).*?<a href="/prognoz/moskva/24hours/#h-(\d{4}-\d{2}-\d{2})-(\d{2})"', re.S)
    temps = []
    rain_likely = False
    target_day = None
    for match in hour_pattern.finditer(html):
        icon = match.group(2)
        temp = int(match.group(3))
        iso_day = match.group(4)
        hour = int(match.group(5))
        if target_day is None:
            target_day = iso_day
        if iso_day != target_day:
            continue
        temps.append((hour, temp, icon))
        if icon in {'09', '10', '11', '12', '13'}:
            rain_likely = True

    if temps:
        morning = min((temp for hour, temp, _ in temps if 6 <= hour <= 11), default=temps[0][1])
        daytime = max((temp for hour, temp, _ in temps if 12 <= hour <= 20), default=max(t for _, t, _ in temps))
    else:
        morning = current_temp
        daytime = current_temp

    if morning is not None and daytime is not None:
        weather_line = f'Погода: около +{morning} °C утром и до +{daytime} °C днём, ' + ('дождь сегодня вероятен.' if rain_likely else 'без дождя.')
    elif current_temp is not None:
        tail = 'дождь сегодня вероятен.' if rain_likely else (current_text + '.' if current_text else 'без дождя.')
        weather_line = f'Погода: около +{current_temp} °C, ' + tail
    else:
        weather_line = 'Погода: сегодня лучше свериться с прогнозом перед выходом.'

    return {
        'source': WEATHER_URL,
        'current_temp': current_temp,
        'current_text': current_text,
        'morning_temp': morning,
        'daytime_temp': daytime,
        'rain_likely': rain_likely,
        'weather_line': weather_line,
    }


def main() -> None:
    now = datetime.now(TZ)
    today = now.date().isoformat()
    weekday = now.strftime('%A')
    recent = recent_final_texts()
    weather = fetch_weather_summary()
    used_main = used_recent_ids(MAIN_ITEMS, recent)
    used_small = used_recent_ids(SMALL_ITEMS, recent)
    used_main_categories = used_recent_categories(MAIN_ITEMS, used_main)
    used_small_categories = used_recent_categories(SMALL_ITEMS, used_small)
    day_seed = date.fromisoformat(today).toordinal()
    main_pool = [x for x in MAIN_ITEMS if x['id'] not in used_main and x['category'] not in used_main_categories]
    if not main_pool:
        main_pool = [x for x in MAIN_ITEMS if x['id'] not in used_main] or MAIN_ITEMS
    main_item = main_pool[day_seed % len(main_pool)]

    small_pool = [x for x in SMALL_ITEMS if x['id'] not in used_small and x['category'] not in used_small_categories]
    if not small_pool:
        small_pool = [x for x in SMALL_ITEMS if x['id'] not in used_small] or SMALL_ITEMS
    small_item = small_pool[(day_seed + 3) % len(small_pool)]
    event = find_event(today)

    print('DAILY_CONTEXT')
    print(f'today: {today}')
    print(f'weekday: {weekday}')
    print(f'timezone: Europe/Moscow')
    print(f'today_event: {event if event else "null"}')
    print('\nWEATHER_SOURCE')
    print(f"- url: {weather['source']}")
    print(f"- current_temp: {weather['current_temp']}")
    print(f"- current_text: {weather['current_text']}")
    print(f"- morning_temp: {weather['morning_temp']}")
    print(f"- daytime_temp: {weather['daytime_temp']}")
    print(f"- rain_likely: {str(weather['rain_likely']).lower()}")
    print(f"- weather_line: {weather['weather_line']}")
    print('\nRECENT_FINAL_TEXTS')
    for idx, text in enumerate(recent[-5:], start=1):
        compact = ' | '.join([line.strip() for line in text.splitlines() if line.strip()][3:])
        print(f'- recent_{idx}: {compact}')
    print('\nFORMAT_CONTRACT')
    print('- greeting')
    print('- day/date')
    print('- weather')
    print('- exactly 1 main self-development task')
    print('- exactly 1 smaller support task')
    print('- links required for external sources')
    print('\nSELECTED_MAIN')
    print(f"- id: {main_item['id']}")
    print(f"- text: {main_item['text'].format(url=main_item['url'])}")
    print(f"- link: [{main_item['label']}]({main_item['url']})")
    print('\nSELECTED_SMALL')
    print(f"- id: {small_item['id']}")
    print(f"- text: {small_item['text'].format(url=small_item['url'])}")
    print(f"- link: [{small_item['label']}]({small_item['url']})")
    print('\nANTI_REPEAT_RULES')
    print('- Не повторяй конкретный id из recent texts, если есть свежая альтернатива.')
    print('- Не повторяй категорию main-item на соседних днях, если есть другая доступная категория.')
    print('- Не повторяй категорию small-item в окне последних дней, если есть другая доступная категория.')
    print('- Не меняй выбранные item id ради wording-игры.')
    print('- Не добавляй вторую мелкую задачу.')
    print('- Не превращай main task снова в абстрактный рабочий текст.')
    print('\nPROMPT_PATH')
    print(PROMPT_PATH)


if __name__ == '__main__':
    main()
