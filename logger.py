"""logger configuration module."""
import logging


def logger(file=None):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Create handler and set default log level
    file_handler = logging.FileHandler(file)
    file_handler.setLevel(logging.DEBUG)

    # Create formatter and add to handler
    file_format = logging.Formatter(fmt=log_format, datefmt=date_format)
    file_handler.setFormatter(file_format)

    # Add handler to the logger
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(file_handler)

    return logger
