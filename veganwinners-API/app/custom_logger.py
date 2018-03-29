import sys
import logging
from pythonjsonlogger import jsonlogger


class InfoFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno in (logging.DEBUG, logging.INFO)


def setup_logger(logger):
    supported_keys = [ 'asctime', 'message']
    custom_format = ' '.join((lambda x: ['%({0:s})'.format(i) for i in x])(supported_keys))

    formatter = jsonlogger.JsonFormatter(custom_format)

    logger.setLevel(logging.DEBUG)

    h1 = logging.StreamHandler(sys.stdout)
    h1.setLevel(logging.DEBUG)
    h1.addFilter(InfoFilter())
    h1.setFormatter(formatter)

    h2 = logging.StreamHandler()
    h2.setLevel(logging.WARNING)
    h2.setFormatter(formatter)

    logger.addHandler(h1)
    logger.addHandler(h2)

    return logger
