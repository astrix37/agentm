from functools import wraps
from flask import request
import os
import logging
import traceback

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
