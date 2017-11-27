from functools import wraps
from flask import g, request, redirect, url_for
import datetime
from math import pow, log
import os
import logging
import traceback

from logging.config import dictConfig
from settings.local import LOGGING_CONFIG

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def authorized():
    try:
        authorized = False

        key = 0
        if request.headers.get('AUTH'):
            key = request.headers['AUTH']

        if key == os.environ['KEY']:
            return True, "Allowed"

        return False, "Invalid AUTH key"
    except Exception as ex:
        logger.info(traceback.format_exc())
        return False, "Error when authorizing request: {}".format(ex)


def protect_view(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        
            allowed, message = authorized()

            if allowed:
                return fn(*args, **kwargs)
            else:
                logger.info(message)
                return (message), 401
        
    return inner
