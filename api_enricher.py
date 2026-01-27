import json
import time
import logging
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from requests.exceptions import RequestException, Timeout, JSONDecodeError

from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class APIEnricher:

    def __init__(self):
        self.api_key = "PXonxrdz8g45#rd61d5e732Ap4uhf/Sc="
        self.base_url = "https://top505.ru"
        self.endpoint = f"{self.base_url}/api/item_batch"
        self.headers = {
            "X-API-Key": self.api_key,  # Ключ API передается в заголовке
            "Content-Type": "application/json",  # Говорим серверу, что мы отправляем JSON
            "User-Agent": "Mozilla/5.0"  # Имитируем браузер (не обязательно, но хорошая практика)
        }
        self.stats = {
            "total_ads": 0,          # Всего объявлений загружено
            "sent_to_api": 0,        # Сколько заголовков отправлено в API
            "successfully_enriched": 0,  # Сколько успешно обогащено
            "failed": 0,             # Сколько не удалось обогатить
            "errors": {              # Детализация ошибок по типам
                "timeout": 0,        # Таймаут (долгий ответ)
                "rate_limit": 0,     # Слишком много запросов (429)
                "server_error": 0,   # Ошибки сервера (5xx)
                "invalid_json": 0,   # Ответ не в JSON формате
                "network_error": 0,  # Проблемы с сетью
                "other": 0           # Все остальные ошибки
            }
        }
        logger.info("API Enricher инициализирован. Готов к работе.")

    def load_raw_ads(self) -> List[Dict]:
        """
        Загружает сырые объявления из файла ads_raw.json.
        
        Возвращает:
            List[Dict]: Список словарей с данными объявлений
            
        АНАЛОГИЯ: Это как взять блокнот с записями с предыдущего шага.
        """
        try:
            # Открываем файл для чтения
            # 'r' - режим чтения (read)
            # encoding='utf-8' - указываем кодировку для русских букв
            with open('ads_raw.json', 'r', encoding='utf-8') as f:
                # json.load() - читает JSON из файла и преобразует в Python объект
                ads = json.load(f)
            
            # Проверяем, что мы получили именно список (массив)
            # isinstance() - проверяет тип объекта
            if not isinstance(ads, list):
                # Если это не список, пишем ошибку в лог
                logger.error("Некорректный формат ads_raw.json, ожидается список")
                return []  # Возвращаем пустой список
            
            # Сохраняем количество объявлений в статистику
            self.stats["total_ads"] = len(ads)
            
            # Логируем успешную загрузку
            logger.info(f"Загружено {len(ads)} сырых объявлений из файла ads_raw.json")
            
            # Возвращаем загруженные объявления
            return ads
