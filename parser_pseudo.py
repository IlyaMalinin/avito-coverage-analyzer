from bs4 import BeautifulSoup
import logging

from constants import PARSER_FILE_NAME, FILES_FOR_PARSING
from logging_config import setup_logging
from save_file_json import create_file

setup_logging()
logger = logging.getLogger(__name__)


def parser_files(files):
    """Парсит объявления с из файлов."""

    all_ads_data = []
    for file_name in files:
        logger.info(f'Запуск парсера {file_name}.')
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                html_content = file.read()
        except Exception as e:
            logger.error(f'Ошибка при чтении {file_name}: {e}')
            continue

        soup = BeautifulSoup(html_content, 'html.parser')
        ad_items = soup.find_all('div', {'data-marker': 'item'})
        for i in range(min(10, len(ad_items))):
            ad = ad_items[i]
            ad_data = {}

            if 'data-item-id' in ad.attrs:
                ad_id = ad['data-item-id']
                ad_data['avito_ad_id'] = ad_id
            else:
                ad_data['avito_ad_id'] = None

            title_element = ad.find('a', {'data-marker': 'item-title'})
            if title_element:
                title = title_element.text.strip()
                ad_data['title'] = title
            else:
                ad_data['title'] = None

            if title_element and 'href' in title_element.attrs:
                href = title_element['href']
                if href.startswith('/'):
                    href = f'https://www.avito.ru{href}'
                ad_data['url'] = href
            else:
                ad_data['url'] = None

            geo_element = ad.find('div', {'data-marker': 'item-location'})
            if geo_element:
                region_text = geo_element.text.strip()
                ad_data['region'] = region_text
            else:
                ad_data['region'] = None

            all_ads_data.append(ad_data)
    logger.info(f'Успешно собрано: {len(all_ads_data)} объявлений.')
    create_file(all_ads_data, PARSER_FILE_NAME)
parser_files(FILES_FOR_PARSING)
