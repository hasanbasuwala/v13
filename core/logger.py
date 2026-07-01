import logging
from logging.handlers import RotatingFileHandler


def setup_logger():

    logger = logging.getLogger()

    logger.setLevel(
        logging.INFO
    )

    handler = RotatingFileHandler(

        "logs/bot.log",

        maxBytes=10_000_000,

        backupCount=5
    )

    formatter = logging.Formatter(

        "%(asctime)s "

        "%(levelname)s "

        "%(name)s "

        "%(message)s"
    )

    handler.setFormatter(
        formatter
    )

    logger.addHandler(
        handler
    )