import json
import logging
import logging.config

from app.config.config import settings


def init_logger():
    # Загрузка конфигурации из файла
    with open(settings.PATH_TO_CONFIG_LOGS, 'r') as f:
        config = json.load(f)
    logging.config.dictConfig(config)
    # Добавляем суффикс для TimedRotatingFileHandler (добавление времени в название файла)
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.handlers.TimedRotatingFileHandler):
            handler.suffix = "%Y-%m-%d_%H-%M-%S"  # Формат времени для имени файла
