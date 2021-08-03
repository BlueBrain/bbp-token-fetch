"""check modules logging fonctions"""
import os
import logging
from functools import wraps


def close_handler(logger):
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)


def log_args(logger, handler_path=None):
    def set_logger(file_, logger_path=handler_path):
        if handler_path is None:
            logger_path = os.path.join(".", f"{file_.__name__}.log")

        @wraps(file_)
        def wrapper(*args, **kw):
            file_handler = logging.FileHandler(logger_path)
            logger.setLevel(logging.INFO)
            logger.addHandler(file_handler)
            formatter = logging.Formatter(
                "[%(asctime)s] - %(name)s - {%(filename)s:%(lineno)d} "
                "- %(levelname)s: %(message)s"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            file_(*args, **kw)

        return wrapper

    return set_logger
