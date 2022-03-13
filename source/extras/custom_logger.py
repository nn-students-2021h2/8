"""
Logger formatter module
"""

import logging
from logging import Logger

from pathlib import Path


class CustomFormatter(logging.Formatter):
    """Custom formatter for logging messages in color"""
    _grey = "\x1b[34;20m"
    _green = "\x1b[32;20m"
    _yellow = "\x1b[33;20m"
    _red = "\x1b[31;20m"
    _bold_red = "\x1b[31;1m"
    _reset = "\x1b[0m"

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    FORMATS = {
        logging.DEBUG: _green + log_format + _reset,
        logging.INFO: _grey + log_format + _reset,
        logging.WARNING: _yellow + log_format + _reset,
        logging.ERROR: _red + log_format + _reset,
        logging.CRITICAL: _bold_red + log_format + _reset
    }

    def format(self, record):
        logger_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(logger_format)
        return formatter.format(record)


def setup_logging(logger: Logger):
    """
    Configurate logging system (file and console output)
    :param logger:
    """
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(Path().absolute() / "logs.txt")
    file_handler.setLevel(logging.INFO)
    file_handler_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    file_handler.setFormatter(logging.Formatter(file_handler_format))
    logger.addHandler(file_handler)
