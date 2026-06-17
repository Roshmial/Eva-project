#!/usr/bin/env python3
import argparse
import csv
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup

WORKSPACE_DIR = Path('/home/hermes/workspace')
BASE_DIR = WORKSPACE_DIR / 'tenders'
BASE_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = BASE_DIR / 'it_tender_sources.json'
REFRESH_SCRIPT = WORKSPACE_DIR / 'eva-data' / 'refresh_eva_hub.py'

DEFAULT_TARGET_DATE = datetime.now(timezone.utc).strftime('%d.%m.%Y')
DEFAULT_TARGET_DATE_ISO = datetime.now(timezone.utc).strftime('%Y-%m-%d')
ZAKUPKI_BASE = 'https://zakupki.gov.ru'
B2B_BASE = 'https://www.b2b-center.ru'

DEFAULT_QUERIES = [
    'разработка программного обеспечения',
    'сопровождение информационных систем',
    'техническая поддержка программного обеспечения',
    'внедрение информационных систем',
    'внедрение информационной системы',
    'интеграция информационных систем',
    'информационная безопасность услуги',
    'цифровизация услуги',
    'оказание ИТ услуг',
    'аутсорсинг ит',
    'аутстаффинг ит',
]

FINAL_COLUMNS = [
    'кто',
    'что',
    'сколько',
    'дата тендера',
    'дата подачи',
    'стоимость',
    'источник',
    'ссылка на источник',
]

DEFAULT_CONFIG = {
    'queries': DEFAULT_QUERIES,
    'sources': [
        {
            'key': 'zakupki',
            'name': 'zakupki.gov.ru',
            'enabled': True,
            'kind': 'zakupki',
            'params': {'pages': 3, 'min_score': 8},
        },
        {
            'key': 'b2b',
            'name': 'B2B-Center',
            'enabled': True,
            'kind': 'b2b',
            'params': {'min_score': 7},
        },
        {
            'key': 'fabrikant',
            'name': 'Fabrikant',
            'enabled': False,
            'kind': 'placeholder',
            'params': {'reason': 'Источник пока не реализован в скрипте; добавить отдельный collector.'},
        },
        {
            'key': 'bidzaar',
            'name': 'Bidzaar',
            'enabled': False,
            'kind': 'placeholder',
            'params': {'reason': 'Источник пока не реализован в скрипте; добавить отдельный collector.'},
        },
        {
            'key': 'roseltorg',
            'name': 'Roseltorg',
            'enabled': False,
            'kind': 'placeholder',
            'params': {'reason': 'Источник пока не реализован в скрипте; добавить отдельный collector.'},
        },
    ],
}

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})


def clean(text: str) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()


def normalize_text(text: str) -> str:
    text = clean(text)
    return text.replace(' ,', ',').replace(' .', '.').replace('( ', '(').replace(' )', ')')


def compact_spaced_cyrillic(text: str) -> str:
    text = normalize_text(text)
    replacements = {
        'техническ ой': 'технической',
        'техническ ую': 'техническую',
        'поддержк и': 'поддержки',
        'поддержк у': 'поддержку',
        'поддержк е': 'поддержке',
        'программн ого': 'программного',
        'программн ых': 'программных',
        'обеспечен ия': 'обеспечения',
        'обеспечен ию': 'обеспечению',
        'информацион ной': 'информационной',
        'информацион ные': 'информационные',
        'информацион ных': 'информационных',
        'сист емы': 'системы',
        'сист ема': 'система',
        'сист ем': 'систем',
        'сопровожден ию': 'сопровождению',
        'внедрен ной': 'внедренной',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace('услугпо', 'услуг по')
    return text


def score_text(text: str) -> int:
    t = (text or '').lower()
    positives = [
        ('разработ', 5), ('доработ', 5), ('сопровожден', 5), ('поддержк', 5),
        ('внедрен', 5), ('интеграц', 5), ('автоматизац', 4), ('цифров', 3),
        ('информационн', 2), ('программного обеспечения', 3), ('информационной систем', 3),
        ('аутсорс', 4), ('аутстафф', 4), ('услуг', 2),
    ]
    negatives = [
        ('поставка', -8), ('товар', -6), ('оборудован', -6), ('картридж', -8),
        ('мфу', -8), ('ноутбук', -8), ('монитор', -8), ('компьютер', -8),
        ('неисключительных прав', -7), ('сертификатов', -4), ('предоставлению лицензии', -6),
        ('дебондинга', -8), ('бондинга', -8), ('подписки на программное обеспечение', -4),
    ]
    score = 0
    for term, value in positives:
        if term in t:
            score += value
    for term, value in negatives:
        if term in t:
            score += value
    return score


def load_or_create_config() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding='utf-8')
        return DEFAULT_CONFIG
    return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))


def reliable_buyer(text: str) -> bool:
    text = clean(text)
    if not text or text == 'не указано':
        return False
    bad_markers = [
        'Опросы', 'Статистика', 'Карта сайта', 'Требования к таким банкам',
        'Исполнитель должен', 'Органам контроля', 'Версия hotfix', 'удаленном режиме',
    ]
    return len(text) <= 220 and not any(marker in text for marker in bad_markers)


def parse_dt(value: str):
    try:
        if len(value.strip()) == 10:
            return datetime.strptime(value, '%d.%m.%Y')
        return datetime.strptime(value, '%d.%m.%Y %H:%M')
    except Exception:
        return datetime.max


def sort_key(row: dict):
    return (parse_dt(row['дата подачи']), parse_dt(row['дата тендера']), row['источник'], row['что'])


def write_csv(path: Path, rows: list, columns: list):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter=';')
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, 'не указано') or 'не указано' for col in columns})


def normalize_rows(rows: list):
    for row in rows:
        for key in FINAL_COLUMNS:
            row[key] = normalize_text(row.get(key, 'не указано')) or 'не указано'


def parse_zakupki_card(card) -> dict:
    reg = clean(card.select_one('.registry-entry__header-mid__number').get_text(' ', strip=True)).replace('№ ', '')
    link = card.select_one('.registry-entry__header-mid__number a')['href']
    if link.startswith('/'):
        link = urljoin(ZAKUPKI_BASE, link)

    fields = {}
    for block in card.select('.registry-entry__body-block'):
        title = block.select_one('.registry-entry__body-title')
        value = block.select_one('.registry-entry__body-value, .registry-entry__body-href')
        if title and value:
            fields[clean(title.get_text(' ', strip=True))] = clean(value.get_text(' ', strip=True))

    price = clean((card.select_one('.price-block__value') or card).get_text(' ', strip=True)).replace(' ₽ ₽', ' ₽')
    placed = ''
    deadline = ''
    date_bits = [clean(x.get_text(' ', strip=True)) for x in card.select('.data-block__title, .data-block__value')]
    for i in range(0, len(date_bits) - 1, 2):
        if date_bits[i] == 'Размещено':
            placed = date_bits[i + 1]
        elif date_bits[i] == 'Окончание подачи заявок':
            deadline = date_bits[i + 1]

    return {
        'uid': f'zakupki:{reg}',
        'кто': compact_spaced_cyrillic(fields.get('Заказчик', '')),
        'что': compact_spaced_cyrillic(fields.get('Объект закупки', '')),
        'сколько': 'не указано',
        'дата тендера': placed or 'не указано',
        'дата подачи': deadline or 'не указано',
        'стоимость': price or 'не указано',
        'источник': 'zakupki.gov.ru',
        'ссылка на источник': link,
        'reg': reg,
    }


def enrich_zakupki_buyer(row: dict) -> None:
    if reliable_buyer(row['кто']):
        return
    reg = row.get('reg', '')
    if not reg:
        row['кто'] = 'не указано'
        return

    preferred_titles = ['Заказчик', 'Организация, осуществляющая размещение']

    def try_extract_from_sections(sections, title_selector: str, value_selector: str):
        extracted = {}
        for sec in sections:
            title = sec.select_one(title_selector)
            value = sec.select_one(value_selector)
            if not title or not value:
                continue
            title_text = clean(title.get_text(' ', strip=True))
            buyer = compact_spaced_cyrillic(value.get_text(' ', strip=True))
            if reliable_buyer(buyer):
                extracted[title_text] = buyer
        for preferred_title in preferred_titles:
            if preferred_title in extracted:
                return extracted[preferred_title]
        return None

    candidates = [row['ссылка на источник']]
    for kind in ['ea20', 'ok20', 'zk20']:
        candidate = f'{ZAKUPKI_BASE}/epz/order/notice/{kind}/view/common-info.html?regNumber={reg}'
        if candidate not in candidates:
            candidates.append(candidate)
    for url in candidates:
        try:
            html = session.get(url, timeout=30).text
        except Exception:
            continue
        soup = BeautifulSoup(html, 'html.parser')

        buyer = try_extract_from_sections(
            soup.select('.cardMainInfo__section'),
            '.cardMainInfo__title',
            '.cardMainInfo__content',
        )
        if buyer:
            row['кто'] = buyer
            row['ссылка на источник'] = url
            return

        buyer = try_extract_from_sections(
            soup.select('.blockInfo__section'),
            '.section__title',
            '.section__info',
        )
        if buyer:
            row['кто'] = buyer
            row['ссылка на источник'] = url
            return
    row['кто'] = 'не указано'


def collect_zakupki(target_date_str: str, queries: list, params: dict) -> tuple[list, dict]:
    items = {}
    pages = int(params.get('pages', 3))
    min_score = int(params.get('min_score', 8))
    for query in queries:
        for page in range(1, pages + 1):
            url = (
                f'{ZAKUPKI_BASE}/epz/order/extendedsearch/results.html?'
                f'searchString={quote(query)}&morphology=on&publishDateFrom={quote(target_date_str)}&publishDateTo={quote(target_date_str)}&'
                'sortBy=PUBLISH_DATE&sortDirection=false&recordsPerPage=_50&'
                f'pageNumber={page}&fz44=on&af=on&ca=on&pc=on&pa=on'
            )
            soup = BeautifulSoup(session.get(url, timeout=40).text, 'html.parser')
            cards = soup.select('.search-registry-entry-block')
            if not cards:
                break
            for card in cards:
                row = parse_zakupki_card(card)
                if row['дата тендера'] != target_date_str:
                    continue
                score = score_text(f"{row['что']} {row['кто']}")
                if score < min_score:
                    continue
                prev = items.get(row['uid'])
                if not prev or score > prev['_score']:
                    row['_score'] = score
                    items[row['uid']] = row
    rows = []
    for row in items.values():
        text = f"{row['что']} {row['кто']}".lower()
        if 'поставка' in text and not any(x in text for x in ['услуг', 'сопровожден', 'поддержк', 'разработ', 'внедрен', 'интеграц']):
            continue
        enrich_zakupki_buyer(row)
        row['кто'] = row['кто'] if reliable_buyer(row['кто']) else 'не указано'
        rows.append(row)
    status = {
        'источник': 'zakupki.gov.ru',
        'статус': 'собрано' if rows else 'собрано: 0 строк',
        'что получилось': f'найдено и выгружено {len(rows)} релевантных ИТ-закупок за {target_date_str}',
        'ограничение': 'по части карточек заказчик публично нечитабелен и остаётся как «не указано»' if rows else 'по текущим запросам не найдено релевантных строк за дату запуска',
    }
    return rows, status


def parse_b2b_rows_for_query(query: str) -> list:
    url = f'{B2B_BASE}/market/?f_keyword={quote(query)}&searching=1'
    html = session.get(url, timeout=30).text
    soup = BeautifulSoup(html, 'html.parser')
    rows = []
    for tr in soup.select('table.search-results tr')[1:]:
        cells = tr.select('td')
        if len(cells) < 4:
            continue
        main_link = tr.select_one('a[href*="tender-"]')
        if not main_link:
            continue
        firm_link = None
        for a in tr.select('a[href]'):
            href = a.get('href', '')
            if '/firms/' in href:
                firm_link = a
                break
        href = urljoin(B2B_BASE, main_link['href'].split('#')[0])
        title_text = ' '.join(main_link.get_text(' ', strip=True).split())
        number_match = re.search(r'№\s*(\d+)', title_text)
        tender_num = number_match.group(1) if number_match else href.rstrip('/').split('tender-')[-1].split('/')[0]
        subject = re.sub(r'^(Запрос предложений|Процедура закупки|Запрос цен|Конкурс|Аукцион)\s*№\s*\d+\s*', '', title_text).strip()
        subject = re.sub(r'^\d+\s*/\s*\d+\s*', '', subject).strip()
        buyer = compact_spaced_cyrillic(firm_link.get_text(' ', strip=True) if firm_link else '') or 'не указано'
        published = clean(cells[2].get_text(' ', strip=True))
        deadline = clean(cells[3].get_text(' ', strip=True))
        category = clean(cells[0].get_text(' ', strip=True))
        rows.append({
            'uid': f'b2b:{tender_num}',
            'кто': buyer,
            'что': compact_spaced_cyrillic(subject),
            'сколько': 'не указано',
            'дата тендера': published or 'не указано',
            'дата подачи': deadline or 'не указано',
            'стоимость': 'не указана на публичной карточке',
            'источник': 'B2B-Center',
            'ссылка на источник': href,
            '_category': category,
        })
    return rows


def collect_b2b(target_date_str: str, queries: list, params: dict) -> tuple[list, dict]:
    items = {}
    min_score = int(params.get('min_score', 7))
    for query in queries:
        for row in parse_b2b_rows_for_query(query):
            if not row['дата тендера'].startswith(target_date_str):
                continue
            score = score_text(f"{row['что']} {row['кто']} {row['_category']}")
            if score < min_score:
                continue
            prev = items.get(row['uid'])
            if not prev or score > prev['_score']:
                row['_score'] = score
                items[row['uid']] = row
    rows = []
    for row in items.values():
        text = f"{row['что']} {row['кто']} {row.get('_category', '')}".lower()
        if any(x in text for x in ['внешнего контактного центра', 'картридж', 'ноутбук', 'монитор', 'компьютер']) and not any(y in text for y in ['разработ', 'внедрен', 'систем', 'интеграц', 'автоматизац']):
            continue
        rows.append(row)
    status = {
        'источник': 'B2B-Center',
        'статус': 'собрано' if rows else 'собрано: 0 строк',
        'что получилось': f'найдено и выгружено {len(rows)} релевантных ИТ-закупок за {target_date_str}',
        'ограничение': 'у большинства карточек стоимость не показана публично' if rows else 'публичная выдача по текущим запросам не дала строк за дату запуска',
    }
    return rows, status


def collect_placeholder(_target_date_str: str, _queries: list, params: dict, name: str) -> tuple[list, dict]:
    reason = params.get('reason', 'Источник пока не реализован в скрипте.')
    return [], {
        'источник': name,
        'статус': 'не включён в сбор',
        'что получилось': 'данные не собирались',
        'ограничение': reason,
    }


def build_collectors():
    return {
        'zakupki': lambda date_str, queries, params, name: collect_zakupki(date_str, queries, params),
        'b2b': lambda date_str, queries, params, name: collect_b2b(date_str, queries, params),
        'placeholder': lambda date_str, queries, params, name: collect_placeholder(date_str, queries, params, name),
    }


def collect_enabled_sources(config: dict, target_date_str: str):
    queries = config.get('queries') or DEFAULT_QUERIES
    collectors = build_collectors()
    combined_rows = []
    statuses = []
    source_counts = {}
    enabled_sources = [s for s in config.get('sources', []) if s.get('enabled', False)]
    for source in enabled_sources:
        kind = source.get('kind')
        collector = collectors.get(kind)
        if not collector:
            statuses.append({
                'источник': source.get('name', source.get('key', 'unknown')),
                'статус': 'ошибка конфигурации',
                'что получилось': 'collector не найден',
                'ограничение': f'Неизвестный kind: {kind}',
            })
            continue
        rows, status = collector(target_date_str, queries, source.get('params', {}), source.get('name', source.get('key', kind)))
        normalize_rows(rows)
        combined_rows.extend(rows)
        statuses.append(status)
        source_counts[status['источник']] = len(rows)
    combined_rows.sort(key=sort_key)
    return combined_rows, statuses, source_counts, [s.get('name', s.get('key')) for s in enabled_sources]


def parse_args():
    parser = argparse.ArgumentParser(description='Сбор ИТ-закупок в единый CSV.')
    parser.add_argument('--date', default=DEFAULT_TARGET_DATE, help='Дата публикации в формате ДД.ММ.ГГГГ')
    parser.add_argument('--out-dir', default=str(BASE_DIR), help='Папка для результатов')
    return parser.parse_args()


def main():
    args = parse_args()
    target_date_str = args.date
    target_date_iso = datetime.strptime(target_date_str, '%d.%m.%Y').strftime('%Y-%m-%d')
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    config = load_or_create_config()
    combined_rows, statuses, source_counts, enabled_source_names = collect_enabled_sources(config, target_date_str)

    dated_csv = out_dir / f'it_tenders_{target_date_iso}.csv'
    latest_csv = out_dir / 'it_tenders_latest.csv'
    status_csv = out_dir / f'tender_sources_status_{target_date_iso}.csv'
    latest_status_csv = out_dir / 'tender_sources_status_latest.csv'
    summary_json = out_dir / 'last_run_summary.json'

    write_csv(dated_csv, combined_rows, FINAL_COLUMNS)
    write_csv(latest_csv, combined_rows, FINAL_COLUMNS)
    write_csv(status_csv, statuses, ['источник', 'статус', 'что получилось', 'ограничение'])
    write_csv(latest_status_csv, statuses, ['источник', 'статус', 'что получилось', 'ограничение'])

    summary = {
        'date': target_date_str,
        'enabled_sources': enabled_source_names,
        'total_rows': len(combined_rows),
        'by_source': dict(Counter(row['источник'] for row in combined_rows)),
        'status_by_source': {status['источник']: status['статус'] for status in statuses},
        'csv_path': str(dated_csv),
        'latest_csv_path': str(latest_csv),
        'status_csv_path': str(status_csv),
        'latest_status_csv_path': str(latest_status_csv),
        'config_path': str(CONFIG_PATH),
    }
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    if REFRESH_SCRIPT.exists():
        subprocess.run([sys.executable, str(REFRESH_SCRIPT)], check=True)

    lines = [
        f'Готово. Собрала ИТ-закупки за {target_date_str}.',
        f'Всего строк: {len(combined_rows)}.',
    ]
    for name in enabled_source_names:
        lines.append(f'{name}: {source_counts.get(name, 0)}.')
    lines += [
        '',
        f'Файл: {dated_csv.name}',
        f'Файл статусов: {status_csv.name}',
        f'Конфиг источников: {CONFIG_PATH.name}',
        f'MEDIA:{dated_csv}',
    ]
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
