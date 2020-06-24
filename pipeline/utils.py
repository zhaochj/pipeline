import logging


def get_logger(mode: str, file_path: str):
    logger = logging.getLogger(mode)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.FileHandler(file_path)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s [%(name)s %(funcName)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger



