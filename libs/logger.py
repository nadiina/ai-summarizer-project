import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_LEVEL = logging.INFO


def get_logger(name: str, log_dir: str = None, filename: str = os.getenv("LOG_FILENAME", "app.log")) -> logging.Logger:
    if log_dir is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(project_root, "logs")

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, filename)

    logger = logging.getLogger(name)
    logger.setLevel(DEFAULT_LOG_LEVEL)
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    if not logger.handlers:
        file_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


_logger = get_logger("GlobalLogger")


def log_info(message: str):
    _logger.info(message)


def log_warning(message: str):
    _logger.warning(message)


def log_error(message: str):
    _logger.error(message)


def log_debug(message: str):
    _logger.debug(message)
