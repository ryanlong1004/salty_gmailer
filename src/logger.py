"""logging convenience module"""

import logging


def get_logger(module_name, file_name):
    """fetches a logger instance"""
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    f_handler = logging.FileHandler(file_name)
    f_handler.setLevel(logging.ERROR)
    # create console handler with a higher log level
    ch_handler = logging.StreamHandler()
    ch_handler.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    f_handler.setFormatter(formatter)
    ch_handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(f_handler)
    logger.addHandler(ch_handler)

    return logger
