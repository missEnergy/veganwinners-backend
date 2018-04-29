import sys
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler


class InfoFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno in (logging.DEBUG, logging.INFO)


def setup_logger(logger):
    supported_keys = [ 'asctime', 'levelname',
        'lineno', 'module', 'message', 'name']
    custom_format = ' '.join((lambda x: ['%({0:s})'.format(i) for i in x])(supported_keys))

    formatter = jsonlogger.JsonFormatter(custom_format)

    logger.setLevel(logging.DEBUG)

    #h1 = RotatingFileHandler('debug.log', maxBytes=1000000, backupCount=1)
    h1 = logging.StreamHandler(sys.stdout)
    h1.setLevel(logging.DEBUG)
    h1.addFilter(InfoFilter())
    h1.setFormatter(formatter)

    #h2 = RotatingFileHandler('warning.log', maxBytes=1000000, backupCount=1)
    h2 = logging.StreamHandler()
    h2.setLevel(logging.WARNING)
    h2.setFormatter(formatter)

    #h3 = RotatingFileHandler('error.log', maxBytes=1000000, backupCount=1)
    h3 = logging.StreamHandler()
    h3.setLevel(logging.ERROR)
    h3.setFormatter(formatter)

    logger.addHandler(h1)
    logger.addHandler(h2)
    logger.addHandler(h3)

    return logger
