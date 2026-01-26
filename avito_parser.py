import requests
from bs4 import BeautifulSoup
import json
import logging

from constants import URL, HEADERS
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def parser_avito():
    """Парсит объявления с Avito."""
    logger.info("Запуск парсера Avito.")

    try:
        response = requests.get(URL, headers=HEADERS, timeout=30)
        logger.info(f"Статус ответа: {response.status_code}")
    except Exception as e:
        logger.error(f"Ошибка при запросе: {e}")

    soup = BeautifulSoup(response.text, 'html.parser')
    ad_items = soup.find_all('div', {'data-marker': 'item'})
    all_ads_data = []
    for i in range(min(15, len(ad_items))):
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
                href = f"https://www.avito.ru{href}"
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
    logger.info(f"Успешно собрано: {len(all_ads_data)} объявлений.")
    return all_ads_data


def create_ads_raw(ads_data=None):
    """Сохраняет данные в JSON файл."""

    if ads_data is None:
        ads_data = parser_avito()

    logger.info("Сохранение данных в JSON.")

    if not ads_data:
        logger.error("Нет данных для сохранения!")
        return

    try:
        with open('ads_raw.json', 'w', encoding='utf-8') as json_file:
            json.dump(ads_data, json_file, indent=2, ensure_ascii=False)
        logger.info(f"Данные сохранены в ads_raw.json.")
    except Exception as e:
        logger.error(f"Ошибка при сохранении: {e}")
