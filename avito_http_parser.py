import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import time
import random
import os
from typing import List, Dict, Optional
import logging
import json

# === Настройки ===
AVITO_SEARCH_URL = 'https://www.avito.ru/sankt-peterburg/kvartiry/prodam-ASgBAgICAUSSA8YQ'
COOKIES_JSON = ""
GOOGLE_CREDENTIALS_JSON = ""
GOOGLE_SHEET_NAME = 'Авито'
PROXY_LIST_URL = 'https://www.proxy-list.download/api/v1/get?type=https'
USE_PROXY = False  # Можно отключить, если не нужны прокси
REQUEST_DELAY = (2, 5)  # Задержка между запросами (секунды)
MAX_LISTINGS = 10  # Ограничение на количество объявлений
SHEET_ID = '1-MgalKBBe1FqtLr3caL1h_CJjRfwc8GS51VAIsPgfNg'
MAX_PAGES_LIMIT = 5 

# Настройка логирования ошибок
logging.basicConfig(
    filename='avito_parser_errors.log',
    filemode='a',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.ERROR,
    encoding='utf-8'
)

def log_error(msg: str):
    print(f'[ERROR] {msg}')
    logging.error(msg)

# === Чтение cookies ===
def load_cookies_from_json(session: requests.Session, cookies_json: str):
    """Загружает cookies из JSON-строки (массив объектов) и добавляет их в сессию requests"""
    cookies = json.loads(cookies_json)
    for cookie in cookies:
        # Только name, value, domain, path обязательны
        session.cookies.set(
            name=cookie.get('name'),
            value=cookie.get('value'),
            domain=cookie.get('domain'),
            path=cookie.get('path', '/')
        )

# === Прокси ===
def get_proxy_list() -> List[str]:
    try:
        resp = requests.get(PROXY_LIST_URL, timeout=10)
        if resp.ok:
            return [p.strip() for p in resp.text.split('\n') if p.strip()]
    except Exception:
        pass
    return []

def get_random_proxy(proxy_list: List[str]) -> Optional[dict]:
    if not proxy_list:
        return None
    proxy = random.choice(proxy_list)
    return {
        'http': f'http://{proxy}',
        'https': f'https://{proxy}'
    }

# === Google Sheets ===
def get_gspread_client():
    creds = Credentials.from_service_account_info(json.loads(GOOGLE_CREDENTIALS_JSON), scopes=[
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ])
    client = gspread.authorize(creds)
    return client

def get_or_create_worksheet(client):
    # Просто открываем по ID, не создаём новую таблицу
    return client.open_by_key(SHEET_ID).worksheet(GOOGLE_SHEET_NAME)

# === Сбор ссылок на объявления ===
def collect_listing_links(session: requests.Session, proxy_list: List[str]) -> List[str]:
    """Собирает все ссылки на объявления по пагинации Avito"""
    links = []
    page = 1
    max_pages = MAX_PAGES_LIMIT  # Ограничение на случай бесконечной пагинации
    while page <= max_pages:
        url = f"{AVITO_SEARCH_URL}?p={page}"
        proxies = get_random_proxy(proxy_list) if USE_PROXY else None
        resp = session.get(url, proxies=proxies, timeout=20)
        if resp.status_code != 200:
            print(f"Ошибка загрузки страницы {page}: {resp.status_code}")
            break
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.select('[data-marker="item"]')
        page_links = []
        for item in items:
            a = item.find('a', itemprop='url')
            if a and 'href' in a.attrs:
                href = str(a['href'])
                if href.startswith('/'):
                    href = 'https://www.avito.ru' + href
                page_links.append(href)
        if not page_links:
            print(f'Ссылки на объявления не найдены на странице {page}!')
            break
        print(f'Страница {page}: найдено {len(page_links)} ссылок')
        links.extend(page_links)
        # Проверка на последнюю страницу: если меньше 10-20 объявлений, вероятно, это конец
        if len(page_links) < 10:
            break
        time.sleep(random.uniform(*REQUEST_DELAY))
        page += 1
    return links

# === Парсинг одного объявления ===
def extract_block_params_bs(soup, block_title: str) -> dict:
    """Извлекает параметры из блока по заголовку (например, 'О квартире')"""
    params = {}
    # Ищем div с классом cK39j, внутри которого есть h2 с нужным текстом
    for block in soup.find_all('div', class_='cK39j'):
        h2 = block.find('h2')
        if h2 and h2.get_text(strip=True) == block_title:
            ul = block.find('ul')
            if not ul:
                continue
            for li in ul.find_all('li'):
                spans = li.find_all('span')
                if spans:
                    key = spans[0].get_text(strip=True).replace(':', '')
                    value = li.get_text(strip=True)
                    if ':' in value:
                        value = value.split(':', 1)[-1].strip()
                    params[key] = value
                else:
                    text = li.get_text(strip=True)
                    params[text] = text
            break
    return params

def parse_listing(session: requests.Session, url: str, proxy_list: List[str]) -> Dict[str, str]:
    proxies = get_random_proxy(proxy_list) if USE_PROXY else None
    resp = session.get(url, proxies=proxies, timeout=20)
    if resp.status_code != 200:
        print(f"Ошибка загрузки объявления: {url}")
        return {}
    soup = BeautifulSoup(resp.text, 'html.parser')
    data = {}
    # Название
    h1 = soup.find('h1', attrs={'data-marker': 'item-view/title-info'})
    data['Название'] = h1.get_text(strip=True) if h1 else ''
    # Описание
    desc_block = soup.find('div', id='bx_item-description')
    desc = ''
    if desc_block:
        desc_inner = desc_block.find('div', attrs={'data-marker': 'item-view/item-description'})
        if desc_inner:
            desc = desc_inner.get_text(strip=True)
    data['Описание'] = desc
    # Цена
    price_span = soup.find('span', attrs={'itemprop': 'price', 'data-marker': 'item-view/item-price'})
    if price_span:
        price = price_span.get('content')
        if not price:
            price = price_span.get_text(strip=True)
        if price:
            price = str(price).replace('\xa0', '').replace(' ', '')
        else:
            price = ''
        data['Цена'] = price
    else:
        data['Цена'] = ''
    # Ссылка
    data['Ссылка'] = url
    # Количество фото
    gallery = soup.find('div', id='bx_item-gallery')
    num_photos = 0
    if gallery:
        preview_list = gallery.find('ul', attrs={'data-marker': 'image-preview/preview-wrapper'})
        if preview_list:
            items_li = preview_list.find_all('li', attrs={'data-marker': 'image-preview/item'})
            num_photos = len(items_li) if items_li else 0
    data['Кол-во фото'] = num_photos
    # Блоки параметров
    apt_params = extract_block_params_bs(soup, 'О квартире')
    dom_params = extract_block_params_bs(soup, 'О доме')
    loc_params = extract_block_params_bs(soup, 'Расположение')
    # Добавляем параметры в data
    for k, v in apt_params.items():
        data[f'О квартире: {k}'] = v
    for k, v in dom_params.items():
        data[f'О доме: {k}'] = v
    for k, v in loc_params.items():
        data[f'Расположение: {k}'] = v
    return data

# === Основной запуск ===
def main():
    proxy_list = get_proxy_list() if USE_PROXY else []
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9',
    })
    load_cookies_from_json(session, COOKIES_JSON)

    client = get_gspread_client()
    sheet = get_or_create_worksheet(client)

    print('Собираю ссылки на объявления...')
    links = collect_listing_links(session, proxy_list)
    print(f'Найдено {len(links)} объявлений')

    count = 0
    for i, url in enumerate(links, 1):
        if count >= MAX_LISTINGS:
            print(f'Достигнут лимит {MAX_LISTINGS} объявлений, остановка.')
            break
        print(f'[{i}/{len(links)}] Парсинг: {url}')
        try:
            data = parse_listing(session, url, proxy_list)
        except Exception as e:
            log_error(f'Ошибка при парсинге {url}: {e}')
            continue
        if not data:
            continue
        # Получаем текущую шапку
        try:
            headers = sheet.row_values(1)
            new_cols = [k for k in data.keys() if k not in headers]
            if new_cols:
                sheet.add_cols(len(new_cols))
                headers += new_cols
                sheet.delete_rows(1)
                sheet.insert_row(headers, 1)
            # Формируем строку для записи
            row = [data.get(h, '') for h in headers]
            sheet.append_row(row)
            count += 1
        except Exception as e:
            log_error(f'Ошибка при записи в Google Sheets для {url}: {e}')
        time.sleep(random.uniform(*REQUEST_DELAY))

if __name__ == '__main__':
    main() 