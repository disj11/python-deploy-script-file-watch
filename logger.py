import logging.handlers

logging_formatter = logging.Formatter("%(asctime)s [%(levelname)8s] %(message)s")
logging_handler = logging.handlers.TimedRotatingFileHandler(filename="logs/deploy.log", when="midnight", interval=1,
                                                            encoding="utf-8")
logging_handler.setFormatter(logging_formatter)
logging_handler.suffix = "%Y%m%d"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging_handler)


def info(msg):
    logger.info(msg)
