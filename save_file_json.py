import json
import logging

from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def create_file(ads_data, name_file):
    """Сохраняет данные в JSON файл."""

    logger.info('Сохранение данных в JSON.')

    if not ads_data:
        logger.error('Нет данных для сохранения!')
        return

    try:
        with open(name_file, 'w', encoding='utf-8') as json_file:
            json.dump(ads_data, json_file, indent=2, ensure_ascii=False)
        logger.info(f'Данные сохранены в {name_file}.')
    except Exception as e:
        logger.error(f'Ошибка при сохранении: {e}')
