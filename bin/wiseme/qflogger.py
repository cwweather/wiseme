# coding: utf-8
import logging
import logging.config
from settings import Config


def initlog(logpath, notepath):
    conf = {
        'version': 1,
        'formatters': {
            'myformat': {
                'format': '%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'myformat',
                'level': 'DEBUG',
                'stream': 'ext://sys.stdout'
            },
            'handle_info': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': logpath,
                'when': 'midnight',
                'interval': 1,
                'formatter': 'myformat',
                'level': 'INFO',
                'backupCount': 0
            },
            'handle_note': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': notepath,
                'when': 'midnight',
                'interval': 1,
                'formatter': 'myformat',
                'level': 'INFO',
                'backupCount': 0
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['handle_info', 'handle_note']
        }
    }
    logging.config.dictConfig(conf)
    return logging

qflogging = initlog(Config.LOGPATH, Config.NOTEPATH)
log = qflogging.getLogger("handle_info")
note_log = qflogging.getLogger("handle_note")