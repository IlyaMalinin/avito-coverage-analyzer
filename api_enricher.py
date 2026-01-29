import json
import time
import logging

import requests

from logging_config import setup_logging
from save_file_json import create_file

setup_logging()
logger = logging.getLogger(__name__)

API_URL = 'https://top505.ru/api/item_batch'
API_KEY = 'PXonxrdz8g45#rd61d5e732Ap4uhf/Sc='
INPUT_FILE = 'ads_raw.json'
OUTPUT_FILE = 'ads_enriched.json'


def read_raw_ads():
    """ Читает сырые объявления из JSON файла. """

    logger.info(f'Читаем сырые объявления из файла: {INPUT_FILE}')

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as file:
            ads = json.load(file)
        if not isinstance(ads, list):
            logger.error(f'Ошибка: Файл {INPUT_FILE} должен содержать список объявлений')
            return []

        logger.info(f'Успешно загружено {len(ads)} объявлений')

        return ads

    except FileNotFoundError:
        logger.error(f'Файл {INPUT_FILE} не найден! Сначала запустите парсер (step1_parser.py)')
        return []
    except json.JSONDecodeError as e:
        logger.error(f' Ошибка при чтении JSON: {e}')
        return []
    except Exception as e:
        logger.error(f' Неизвестная ошибка: {e}')
        return []


def enricher_api():
    source_files = read_raw_ads()
    ads_enriched = []
    for original_ad in source_files:
        headers = {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        }
        payload = {
            "source": "1c",
            "data": [
                {'title': original_ad['title']}]
        }
        response_api_json = requests.post(API_URL, json=payload, headers=headers)
        response_api = response_api_json.json()
        enricher_ad = original_ad.copy()
        additional_data = response_api.get('processed_data', None)
        if not additional_data:
            continue
        enricher_ad.update(additional_data[0])
        ads_enriched.append(enricher_ad)
    create_file(ads_enriched, OUTPUT_FILE)

enricher_api()
