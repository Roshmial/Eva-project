from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import re
import requests
import yaml

TZ = ZoneInfo('Europe/Moscow')
DAILY_OUT = Path('/home/hermes/.hermes/cron/output/329913efa98a')
REGISTRY_PATH = Path('/home/hermes/workspace/eva-daily-usefulness-registry.yaml')
WEATHER_URL = 'https://pogoda.mail.ru/prognoz/moskva/'


def extract_response(text: str) -> str:
    marker = '## Response\n\n'
    idx = text.rfind(marker)
    if idx == -1:
        return text.strip()
    return text[idx + len(marker):].strip()


def recent_output_files(limit: int) -> list[Path]:
    files = sorted(DAILY_OUT.glob('*.md'))
    return files[-limit:]


def recent_final_texts(limit: int) -> list[str]:
    return [extract_response(p.read_text(encoding='utf-8', errors='ignore')) for p in recent_output_files(limit)]


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r'\[[^\]]+\]\(https?://[^\)]+\)', ' ', text)
    text = re.sub(r'[^a-z0-9а-яё ]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def load_registry() -> dict:
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding='utf-8')) or {}
    data.setdefault('main_items', [])
    data.setdefault('small_items', [])
    data.setdefault('semantic_bans', [])
    data.setdefault('settings', {})
    return data


def item_tokens(item: dict) -> set[str]:
    toks = [t for t in normalize(item.get('text', '')).split() if len(t) >= 5]
    stop = {
        'сегодня', 'можно', 'потом', 'вечер', 'короткую', 'короткий', 'короткое',
        'сделала', 'сделать', 'открыла', 'открыть', 'проверила', 'проверить', 'ответила',
        'ответить', 'написала', 'написать', 'закрыла', 'закрыть', 'быстро', 'потом',
    }
    return {t for t in toks if t not in stop}


def used_recent_ids(items: list[dict], recent_texts: list[str]) -> set[str]:
    haystack = normalize('\n'.join(recent_texts))
    used = set()
    for item in items:
        item_id = item.get('id', '')
        if item_id.replace('-', ' ') in haystack:
            used.add(item_id)
            continue
        toks = list(item_tokens(item))[:3]
        if len(toks) >= 2 and all(tok in haystack for tok in toks[:2]):
            used.add(item_id)
    return used


def recent_families(items: list[dict], recent_texts: list[str], cooldown: int) -> set[str]:
    recent_slice = recent_texts[-cooldown:] if cooldown > 0 else recent_texts
    used_ids = used_recent_ids(items, recent_slice)
    return {item.get('family') for item in items if item.get('id') in used_ids}


def choose_main(items: list[dict], recent_texts: list[str], day_seed: int, cooldown: int) -> dict:
    used_ids = used_recent_ids(items, recent_texts)
    used_families = recent_families(items, recent_texts, cooldown)
    ranked = []
    for item in items:
        same_recent = item['id'] in used_ids
        family_repeat = item.get('family') in used_families
        stable = (sum(ord(c) for c in item['id']) + day_seed) % 97
        ranked.append(((same_recent, family_repeat, stable, item['id']), item))
    ranked.sort(key=lambda x: x[0])
    return ranked[0][1]


def choose_small(items: list[dict], recent_texts: list[str], day_seed: int, cooldown: int, main_item: dict) -> dict:
    used_ids = used_recent_ids(items, recent_texts)
    used_families = recent_families(items, recent_texts, cooldown)
    main_tokens = item_tokens(main_item)
    main_family = main_item.get('family')
    ranked = []
    for item in items:
        same_recent = item['id'] in used_ids
        family_repeat = item.get('family') in used_families
        same_family = item.get('family') == main_family
        overlap = len(main_tokens & item_tokens(item))
        stable = (sum(ord(c) for c in item['id']) + day_seed + 17) % 97
        prefer_link = 0 if item.get('has_link') else 1
        ranked.append(((same_recent, same_family, overlap, family_repeat, prefer_link, stable, item['id']), item))
    ranked.sort(key=lambda x: x[0])
    return ranked[0][1]


def choose_pair(main_items: list[dict], small_items: list[dict], recent_texts: list[str], day_seed: int, cooldown: int) -> tuple[dict, dict]:
    main_item = choose_main(main_items, recent_texts, day_seed, cooldown)
    small_item = choose_small(small_items, recent_texts, day_seed, cooldown, main_item)
    if main_item.get('has_link') or small_item.get('has_link'):
        return main_item, small_item

    linked_mains = [item for item in main_items if item.get('has_link')]
    if linked_mains:
        alt_main = choose_main(linked_mains, recent_texts, day_seed, cooldown)
        alt_small = choose_small(small_items, recent_texts, day_seed, cooldown, alt_main)
        if alt_small.get('family') != alt_main.get('family'):
            return alt_main, alt_small

    linked_smalls = [item for item in small_items if item.get('has_link')]
    if linked_smalls:
        alt_small = choose_small(linked_smalls, recent_texts, day_seed, cooldown, main_item)
        if alt_small.get('family') != main_item.get('family'):
            return main_item, alt_small

    return main_item, small_item


def fetch_weather_summary() -> dict:
    html = requests.get(WEATHER_URL, timeout=20, headers={'User-Agent': 'Mozilla/5.0'}).text
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
        temps.append((hour, temp))
        if icon in {'09', '10', '11', '12', '13'}:
            rain_likely = True

    daytime = max((temp for hour, temp in temps if 12 <= hour <= 20), default=current_temp)
    if current_temp is not None and current_text:
        line = f'Погода: в Москве сейчас +{current_temp} °C, {current_text}'
        if daytime is not None:
            line += f'; днём до +{daytime} °C'
        line += '; дождь сегодня возможен.' if rain_likely else '; без дождя.'
    else:
        line = 'Погода: сегодня лучше ещё раз свериться с прогнозом.'
    return {'url': WEATHER_URL, 'weather_line': line}


def main() -> None:
    now = datetime.now(TZ)
    today = now.date().isoformat()
    weekday = now.strftime('%A')
    registry = load_registry()
    settings = registry.get('settings', {})
    recent = recent_final_texts(int(settings.get('recent_window', 14)))
    preview_count = int(settings.get('preview_count', 7))
    cooldown = int(settings.get('same_family_cooldown', 4))
    weather = fetch_weather_summary()
    seed = now.date().toordinal()

    main_item, small_item = choose_pair(registry['main_items'], registry['small_items'], recent, seed, cooldown)

    print('DAILY_CONTEXT')
    print(f'today: {today}')
    print(f'weekday: {weekday}')
    print('timezone: Europe/Moscow')
    print('\nWEATHER_SOURCE')
    print(f"- url: {weather['url']}")
    print(f"- weather_line: {weather['weather_line']}")
    print('\nRECENT_FINAL_TEXTS')
    for idx, text in enumerate(recent[-preview_count:], start=1):
        compact = ' | '.join([line.strip() for line in text.splitlines() if line.strip()][2:])
        print(f'- recent_{idx}: {compact}')
    print('\nDAY_LINE_RENDERED')
    ru_weekdays = {
        'Monday': 'Понедельник', 'Tuesday': 'Вторник', 'Wednesday': 'Среда',
        'Thursday': 'Четверг', 'Friday': 'Пятница', 'Saturday': 'Суббота', 'Sunday': 'Воскресенье'
    }
    month_names = {
        1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
        7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
    }
    day_line = f"{ru_weekdays.get(weekday, weekday)}, {now.day} {month_names[now.month]}. {weather['weather_line']}"
    print(day_line)
    print('\nSELECTED_MAIN')
    print(f"- id: {main_item['id']}")
    print(f"- family: {main_item['family']}")
    print(f"- has_link: {str(bool(main_item.get('has_link'))).lower()}")
    print(f"- text: {main_item['text']}")
    print('\nSELECTED_SMALL')
    print(f"- id: {small_item['id']}")
    print(f"- family: {small_item['family']}")
    print(f"- has_link: {str(bool(small_item.get('has_link'))).lower()}")
    print(f"- text: {small_item['text']}")
    print('\nSELECTED_MAIN_RENDERED')
    print(main_item['text'])
    print('\nSELECTED_SMALL_RENDERED')
    print(small_item['text'])
    print('\nANTI_REPEAT_RULES')
    print('- Не повторяй свежие идеи из recent outputs.')
    print('- Не давай main и small из одного семейства.')
    print('- Не перефразируй abstract-management мысли.')
    print('- Если linked-item выбран, ссылка уже встроена в текст и не должна теряться.')
    print('- Если возможно, хотя бы одна из строк 3 или 4 должна быть linked-item.')
    print('\nSEMANTIC_BANS')
    for value in registry.get('semantic_bans', []):
        print(f'- {value}')


if __name__ == '__main__':
    main()
