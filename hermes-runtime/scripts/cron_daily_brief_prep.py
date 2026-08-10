from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import re
import yaml

TZ = ZoneInfo('Europe/Moscow')
DAILY_OUT = Path('/home/hermes/.hermes/cron/output/329913efa98a')
CTX_PATH = Path('/home/hermes/workspace/eva-digest-context.yaml')
PROMPT_PATH = Path('/home/hermes/workspace/eva-daily-v4.md')

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


def recent_final_texts(limit: int = 8) -> list[str]:
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


def main() -> None:
    now = datetime.now(TZ)
    today = now.date().isoformat()
    weekday = now.strftime('%A')
    recent = recent_final_texts()
    used_main = used_recent_ids(MAIN_ITEMS, recent)
    used_small = used_recent_ids(SMALL_ITEMS, recent)
    day_seed = date.fromisoformat(today).toordinal()
    main_item = pick_item(MAIN_ITEMS, used_main, day_seed)
    small_item = pick_item(SMALL_ITEMS, used_small, day_seed + 3)
    event = find_event(today)

    print('DAILY_CONTEXT')
    print(f'today: {today}')
    print(f'weekday: {weekday}')
    print(f'timezone: Europe/Moscow')
    print(f'today_event: {event if event else "null"}')
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
    print('- Не меняй выбранные item id ради wording-игры.')
    print('- Не добавляй вторую мелкую задачу.')
    print('- Не превращай main task снова в абстрактный рабочий текст.')
    print('\nPROMPT_PATH')
    print(PROMPT_PATH)


if __name__ == '__main__':
    main()
