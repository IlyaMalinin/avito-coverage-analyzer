import json
import logging
import time

import requests

from constants import API_URL, API_KEY, PARSER_FILE_NAME, ENRICHER_FILE_NAME
from logging_config import setup_logging
from save_file_json import create_file

setup_logging()
logger = logging.getLogger(__name__)


def read_raw_ads():
    """ Читает сырые объявления из JSON файла. """

    logger.info(f'Читаем сырые объявления из файла: {PARSER_FILE_NAME}')

    try:
        with open(PARSER_FILE_NAME, 'r', encoding='utf-8') as file:
            ads = json.load(file)
        if not isinstance(ads, list):
            logger.error(f'Ошибка: Файл {PARSER_FILE_NAME} должен содержать список объявлений')
            return []

        logger.info(f'Успешно загружено {len(ads)} объявлений')

        return ads

    except FileNotFoundError:
        logger.error(f'Файл {PARSER_FILE_NAME} не найден! Сначала запустите парсер.')
        return []
    except json.JSONDecodeError as e:
        logger.error(f' Ошибка при чтении JSON: {e}')
        return []
    except Exception as e:
        logger.error(f' Неизвестная ошибка: {e}')
        return []


def enricher_api():
    fails = {}
    source_files = read_raw_ads()
    logger.info(f'Отправлено объявлений: {len(source_files)}')
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
        response_api_json = requests.post(
            API_URL, json=payload, headers=headers, timeout=30)
        code = response_api_json.status_code
        if code != 200:
            logger.error(f'При обращении к API возникла ошибка: {code}')
            fails[code] = fails.get(code, 0) + 1
            continue

        try:
            response_api = response_api_json.json()
        except json.JSONDecodeError:
            fails['not_json(не json ответ)'] = fails.get('not_json', 0) + 1
            continue
        enricher_ad = original_ad.copy()
        additional_data = response_api.get('processed_data', None)
        if not additional_data:
            logger.error(
                f'Запрос "{original_ad['title']}" вернул пустой список.')
            fails['empty_list(пустой список)'] = fails.get('empty_list', 0) + 1
            continue
        enricher_ad.update(additional_data[0])
        ads_enriched.append(enricher_ad)
        time.sleep(0.30)
    create_file(ads_enriched, ENRICHER_FILE_NAME)
    logger.info(f'Обогащено объявлений: {len(ads_enriched)}')
    logger.info(f'Основные ошибки: {fails}')

enricher_api()
