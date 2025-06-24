import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import json
import gspread
from google.oauth2.service_account import Credentials
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

COOKIES = [
    {"domain": ".avito.ru", "expirationDate": 1784904603.643908, "hostOnly": False, "httpOnly": False, "name": "_ga", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "GA1.1.1476714821.1750344604", "id": 1},
    {"domain": ".avito.ru", "expirationDate": 1784904603.643644, "hostOnly": False, "httpOnly": False, "name": "_ga_M29JC28873", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "GS2.1.s1750344603$o1$g0$t1750344603$j60$l0$h0", "id": 2},
    {"domain": ".avito.ru", "expirationDate": 1758120603, "hostOnly": False, "httpOnly": False, "name": "_gcl_au", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "1.1.913174113.1750344603", "id": 3},
    {"domain": ".avito.ru", "expirationDate": 1781880603, "hostOnly": False, "httpOnly": False, "name": "_ym_d", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "1750344603", "id": 4},
    {"domain": ".avito.ru", "expirationDate": 1750416603, "hostOnly": False, "httpOnly": False, "name": "_ym_isad", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "1", "id": 5},
    {"domain": ".avito.ru", "expirationDate": 1781880603, "hostOnly": False, "httpOnly": False, "name": "_ym_uid", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "1750344603534911422", "id": 6},
    {"domain": ".avito.ru", "expirationDate": 1750346404, "hostOnly": False, "httpOnly": False, "name": "_ym_visorc", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "b", "id": 7},
    {"domain": ".avito.ru", "expirationDate": 1781880602.345621, "hostOnly": False, "httpOnly": True, "name": "buyer_laas_location", "path": "/", "sameSite": "lax", "secure": True, "session": False, "storeId": "0", "value": "637640", "id": 8},
    {"domain": ".avito.ru", "expirationDate": 1781880602.345646, "hostOnly": False, "httpOnly": True, "name": "buyer_location_id", "path": "/", "sameSite": "lax", "secure": True, "session": False, "storeId": "0", "value": "637640", "id": 9},
    {"domain": ".avito.ru", "expirationDate": 1750345202.345685, "hostOnly": False, "httpOnly": True, "name": "dfp_group", "path": "/", "sameSite": "lax", "secure": True, "session": False, "storeId": "0", "value": "42", "id": 10},
    {"domain": ".avito.ru", "expirationDate": 1750431005, "hostOnly": False, "httpOnly": False, "name": "f", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "5.0c4f4b6d233fb90636b4dd61b04726f147e1eada7172e06c47e1eada7172e06c47e1eada7172e06c47e1eada7172e06cb59320d6eb6303c1b59320d6eb6303c1b59320d6eb6303c147e1eada7172e06c8a38e2c5b3e08b898a38e2c5b3e08b890df103df0c26013a7b0d53c7afc06d0b2ebf3cb6fd35a0ac0df103df0c26013a8b1472fe2f9ba6b9c99dece94c5a563168e2978c700f15b60e443cd372d739d68392db7d8ea6de2955dea7d86f77f81946b8ae4e81acb9fad99271d186dc1cd087829363e2d856a246b8ae4e81acb9fa143114829cf33ca734d62295fceb188dd50b96489ab264edf88859c11ff00895f88859c11ff00895f88859c11ff00895e2415097439d40471a2a574992f83a9213974252838f5be48b9480d83b9d7585781fae5f646f60991473b3bdbdd1477be3078e2a0753d42019e54102f9e4c4b70c6b3f0bba1f9cd300594a1bd53a660e8a2415e3553547b23e2a3471175c4b0b91e52da22a560f550df103df0c26013a0df103df0c26013aaaa2b79c1ae9259591f05816ce47b911e298c7a08e79909e3de19da9ed218fe2c772035eab81f5e110e95b305e77352aa1a4201a28a6ec9b059080ed9becc4cd", "id": 11},
    {"domain": ".avito.ru", "expirationDate": 1750431005, "hostOnly": False, "httpOnly": False, "name": "ft", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "\"AA+2pMqDep4GUk4EGS4I/ivfre04QmI9WJU7fq+0F+Pw4JFg++tj+cFADCS69rF/SbRf21Iw4GTVS3msWzGWZbWOUEuwzel6obJN6Q4FCsPOkKTckt6E5Z+5EJ/wqM2YZVXWCw6q70mK2+Q606iv4U2VbStPciu+37BtoICx+WNiApS9lFJm0feqEwuKNypy\"", "id": 12},
    {"domain": ".avito.ru", "expirationDate": 1750431005.720779, "hostOnly": False, "httpOnly": True, "name": "gMltIuegZN2COuSe", "path": "/", "sameSite": "lax", "secure": True, "session": False, "storeId": "0", "value": "EOFGWsm50bhh17prLqaIgdir1V0kgrvN", "id": 13},
    {"domain": ".avito.ru", "expirationDate": 1750431002.345635, "hostOnly": False, "httpOnly": True, "name": "luri", "path": "/", "sameSite": "lax", "secure": True, "session": False, "storeId": "0", "value": "moskva", "id": 14},
    {"domain": ".avito.ru", "expirationDate": 1781880603.572427, "hostOnly": False, "httpOnly": False, "name": "ma_cid", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "1750344603984933996", "id": 15},
    {"domain": ".avito.ru", "expirationDate": 1781880604.448738, "hostOnly": False, "httpOnly": False, "name": "ma_id", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "3049551971750344603997", "id": 16},
    {"domain": ".avito.ru", "expirationDate": 1750431003, "hostOnly": False, "httpOnly": False, "name": "ma_ss_64a8dba6-67f3-4fe4-8625-257c4adae014", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "1750344603473537892.1.1750344620.2.1750344603", "id": 17},
    {"domain": ".avito.ru", "expirationDate": 1784904602.345505, "hostOnly": False, "httpOnly": True, "name": "srv_id", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "vHAQtgyVlFaYBfHf.fp9azxjHYug9M-FEz8bs-jFaGTHGbbt2Kc-COqGLmAa5ZLcMG4IR-k8bu5C-dPY=.JGv_cF8nJ7KuoEpIqqPcLYEeiCyfZuI4et9Msks3k0A=.web", "id": 18},
    {"domain": ".avito.ru", "expirationDate": 1750949402.345662, "hostOnly": False, "httpOnly": True, "name": "sx", "path": "/", "sameSite": "lax", "secure": True, "session": False, "storeId": "0", "value": "H4sIAAAAAAAC%2F6pWMjMzM0tOMTdLszSzNDUzMbNMNU9KNbZMMTc1SE42T7FUsqpWKlOyUgr0D070yXUuzisy8iwoKS5T0lFKVbIyNDc1MDE2NDAwqq0FBAAA%2F%2F9ei9V%2FTAAAAA%3D%3D", "id": 19},
    {"domain": ".avito.ru", "expirationDate": 1784904594.757101, "hostOnly": False, "httpOnly": True, "name": "u", "path": "/", "sameSite": "lax", "secure": True, "session": False, "storeId": "0", "value": "374s61vf.cscj2i.yrl5vvz6mm00", "id": 20},
    {"domain": ".avito.ru", "expirationDate": 1784904603, "hostOnly": False, "httpOnly": False, "name": "uxs_uid", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "aee71c10-4d1c-11f0-a81c-d534398d27d5", "id": 21},
    {"domain": ".avito.ru", "expirationDate": 1750346411.985003, "hostOnly": False, "httpOnly": True, "name": "v", "path": "/", "sameSite": "lax", "secure": True, "session": False, "storeId": "0", "value": "1750344595", "id": 22},
    {"domain": ".www.avito.ru", "expirationDate": 1750346411, "hostOnly": False, "httpOnly": False, "name": "csprefid", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "bcbc284d-bcc5-4595-8664-952c5c31ab3f", "id": 23},
    {"domain": ".www.avito.ru", "expirationDate": 1750346403, "hostOnly": False, "httpOnly": False, "name": "cssid", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "c149d55a-92a6-4881-9ac4-cc99ae15ced2", "id": 24},
    {"domain": ".www.avito.ru", "expirationDate": 1750346403, "hostOnly": False, "httpOnly": False, "name": "cssid_exp", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "1750346403010", "id": 25},
    {"domain": "www.avito.ru", "hostOnly": True, "httpOnly": False, "name": "abp", "path": "/", "sameSite": "unspecified", "secure": False, "session": True, "storeId": "0", "value": "0", "id": 26},
    {"domain": "www.avito.ru", "expirationDate": 1755528604, "hostOnly": True, "httpOnly": False, "name": "cookie_consent_shown", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "1", "id": 27},
    {"domain": "www.avito.ru", "expirationDate": 1752936605, "hostOnly": True, "httpOnly": False, "name": "yandex_monthly_cookie", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "true", "id": 28}
]

def get_fields():
    with open('fields.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_value_by_field(driver, field_selector):
    # Поддержка поиска по атрибутам (itemprop=..., class=..., id=..., data-marker=...)
    # Пример: 'itemprop=name class=EEPdn ... data-marker=item-view/title-info'
    parts = field_selector.split()
    selector = ''
    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            if key == 'class':
                selector += f'.{value.replace(" ", ".")}'
            elif key == 'id':
                selector += f'#{value}'
            elif key.startswith('data-'):
                selector += f'[{key}="{value}"]'
            elif key == 'itemprop':
                selector += f'[{key}="{value}"]'
            elif key == 'itemtype':
                selector += f'[{key}="{value}"]'
        else:
            selector += part
    try:
        el = driver.find_element(By.CSS_SELECTOR, selector)
        return el.text
    except Exception as e:
        print(f'Не найдено по селектору {selector}: {e}')
        return None

def count_photos(driver):
    try:
        # Находим все теги <img> внутри галереи
        gallery = driver.find_element(By.CSS_SELECTOR, '#bx_item-gallery')
        images = gallery.find_elements(By.TAG_NAME, 'img')
        return len(images)
    except Exception as e:
        print(f'Не удалось посчитать фото: {e}')
        return 0

def find_block_by_title(driver, title_text):
    blocks = driver.find_elements(By.CSS_SELECTOR, 'div.cK39j')
    for block in blocks:
        try:
            h2 = block.find_element(By.TAG_NAME, 'h2')
            if h2.text.strip() == title_text:
                return block
        except Exception:
            continue
    return None

def extract_block_params_from_block(block):
    params = {}
    try:
        ul = block.find_element(By.TAG_NAME, 'ul')
        li_elements = ul.find_elements(By.TAG_NAME, 'li')
        for li in li_elements:
            spans = li.find_elements(By.TAG_NAME, 'span')
            if spans:
                inner_text = spans[0].get_attribute('innerText')
                key = inner_text.split(':')[0].strip() if inner_text else ''
                if not key:
                    key_html = spans[0].get_attribute('innerHTML')
                    if key_html:
                        key_html = key_html.split('<span')[0].strip()
                        key = re.sub(r'<.*?>', '', key_html).replace(':', '').strip()
                last_span = spans[-1]
                last_span_html = last_span.get_attribute('outerHTML')
                li_html = li.get_attribute('innerHTML')
                after_span = li_html.split(last_span_html)[-1] if last_span_html and li_html else ''
                value = re.sub(r'<.*?>', '', after_span)
                value = value.replace('\xa0', ' ').replace('&nbsp;', ' ').strip()
            else:
                key = li.text.strip()
                value = li.text.strip()
            params[key] = value
    except Exception as e:
        print(f'[extract_block_params_from_block] Ошибка: {e}')
    return params

def parse_avito():
    # Google Sheets setup
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('google-credentials.json', scopes=SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open('Недвижимость Объявления')
    worksheet = sh.worksheet('Авито')

    # Чтение полей и селекторов
    fields_map = get_fields()
    fields = list(fields_map.keys())
    # Убираем столбец 'О квартире' из выгрузки
    fields = [f for f in fields if f != 'О квартире']
    # Проверяем, есть ли заголовки (первые N столбцов совпадают с fields)
    existing = worksheet.get_all_values()
    if not existing or existing[0][:len(fields)] != fields:
        worksheet.clear()
        worksheet.append_row(fields, value_input_option='USER_ENTERED')

    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = uc.Chrome(options=options)
    url = 'https://www.avito.ru/sankt_peterburg_i_lo/kvartiry/prodam'
    print(f'Открываю страницу: {url}')

    driver.get(url)
    time.sleep(2)
    driver.delete_all_cookies()

    for cookie in COOKIES:
        if "sameSite" in cookie and cookie["sameSite"] not in ["Strict", "Lax", "None"]:
            del cookie["sameSite"]
        if "expirationDate" in cookie:
            cookie["expires"] = int(cookie["expirationDate"])
            del cookie["expirationDate"]
        cookie.pop("storeId", None)
        cookie.pop("id", None)
        driver.add_cookie(cookie)
    driver.get(url)
    time.sleep(5)

    items = driver.find_elements(By.CSS_SELECTOR, '[data-marker="item"]')
    print(f'Найдено карточек объявлений: {len(items)}')
    links = []

    for item in items:
        try:
            link = item.find_element(By.CSS_SELECTOR, 'a[itemprop="url"]').get_attribute('href')
            if link:
                links.append(link)
        except Exception as e:
            print(f'Не удалось получить ссылку: {e}')
    print(f'Собрано ссылок: {len(links)}')
    if not links:
        print('Ссылки на объявления не найдены! Проверьте селектор или структуру страницы.')

    for i, link in enumerate(links):
        print(f'[{i+1}/{len(links)}]')
        driver.get(link)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1[data-marker='item-view/title-info']"))
            )
            # Ожидание появления всех элементов по селекторам из fields.json
            for selector in fields_map.values():
                if selector == 'URL':
                    continue
                # Преобразуем селектор из fields.json в валидный CSS (если нужно)
                parts = selector.split()
                css_selector = ''
                for part in parts:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        if key == 'class':
                            css_selector += f'.{value.replace(" ", ".")}';
                        elif key == 'id':
                            css_selector += f'#{value}';
                        elif key.startswith('data-'):
                            css_selector += f'[{key}="{value}"]';
                        elif key == 'itemprop':
                            css_selector += f'[{key}="{value}"]';
                        elif key == 'itemtype':
                            css_selector += f'[{key}="{value}"]';
                    else:
                        css_selector += part
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
                    )
                except Exception as e:
                    print(f'Не дождался загрузки поля по селектору {css_selector}: {e}')
        except Exception as e:
            print(f'Не дождался загрузки заголовка объявления: {e}')
            continue

        row = {}

        # Сбор стандартных полей
        for field, selector in fields_map.items():
            if field == 'Ссылка':
                row[field] = link
            elif field == 'Фотки':
                row[field] = count_photos(driver)
            elif field in ['О квартире', 'О доме', 'Местоположение']:
                continue  # Эти блоки не выгружаем напрямую
            else:
                row[field] = get_value_by_field(driver, selector)

        # Сбор параметров из блоков по заголовку
        apt_block = find_block_by_title(driver, 'О квартире')
        dom_block = find_block_by_title(driver, 'О доме')
        loc_block = find_block_by_title(driver, 'Расположение')
        apt_params = extract_block_params_from_block(apt_block) if apt_block else {}
        dom_params = extract_block_params_from_block(dom_block) if dom_block else {}
        loc_params = extract_block_params_from_block(loc_block) if loc_block else {}

        # Автоматическая подстройка структуры таблицы
        current_headers = worksheet.row_values(1)
        new_columns = []
        for col in list(apt_params.keys()) + list(dom_params.keys()) + list(loc_params.keys()):
            if col and col not in current_headers:
                new_columns.append(col)
        if new_columns:
            worksheet.add_cols(len(new_columns))
            updated_headers = current_headers + new_columns
            worksheet.delete_rows(1)
            worksheet.insert_row(updated_headers, 1)
            current_headers = updated_headers

        # Объединяем row с параметрами из всех блоков
        for k, v in apt_params.items():
            row[k] = v
        for k, v in dom_params.items():
            row[k] = v
        for k, v in loc_params.items():
            row[k] = v

        # Формируем values по актуальным заголовкам
        values = [row.get(field, '') for field in current_headers]
        worksheet.append_row(values, value_input_option='USER_ENTERED')
        time.sleep(1)
    driver.quit()
    print(f'Сохранено {len(links)} объявлений в Google Sheets')

def main():
    parse_avito()

if __name__ == '__main__':
    main() 